import json
import weakref
import gc
from functools import reduce

UNIQUE_ID = {}

OBJECTS = {}

# generator of unique id for objects
def id_generator(name):
    if not name in UNIQUE_ID:
        UNIQUE_ID[name] = 0

    UNIQUE_ID[name] += 1

    return str(name + '_' + str(UNIQUE_ID[name]))

class Node(object):
    def __init__(self, name = None, terminal = None, json_node = None, other_node = None):
        self.name = ""
        self.terminal = False
        self.children = []
        self.parent = None
        
        if not json_node is None:
            self.__init_from_json(json_node)
        if not name is None:
            self.name = name
        if not terminal is None:
            self.terminal = terminal

        if not other_node is None:
            self.name = other_node.name
            self.terminal = other_node.terminal
            for node in other_node.children:
                new_node = Node(other_node = node)
                new_node.parent = self
                self.children.append(new_node)

        if self.terminal:
            self.id = ''

    def handle_id(self):
        if self.terminal:
            self.id = id_generator(self.name)
        elif hasattr(self, 'id'):
            del self.id

    def __eq__(self, other):

        result = self.terminal == other.terminal

        if result and self.terminal:
            result &= self.id == other.id

        result &= self.name == other.name

        return result

    def __ne__(self, other):
        return not self.__eq__(other)

    def add(self, node):
        self.children.append(node)
        node.parent = self
        self.children = sorted(self.children, key = lambda n: (n.name, n.terminal))
    
    def __init_from_json(self, json_node):
        self.name     = json_node['name']
        self.terminal = json_node['terminal']

        if 'symbol' in json_node:
            if type(json_node['symbol']) is list:
                for symbol in json_node['symbol']:
                    new_node = Node(json_node = symbol)
                    new_node.parent = self
                    self.children.append(new_node)
            else:
                new_node = Node(json_node = json_node['symbol'])
                new_node.parent = self
                self.children.append(new_node)

        self.children = sorted(self.children, key = lambda n: (n.name, n.terminal))

    def clear(self):
        def clear_rec(node):
            for n in node.children:
                clear_rec(n)

            node.children = []
            del node

        for n in self.children:
            clear_rec(n)
        self.children = []

class Rule(object):
    def __init__(self, json_rule):
        self.name   = json_rule['name']
        self.type   = json_rule['type']
        self.method = json_rule['method']
        self.left  = Node(json_node = json_rule['left']['symbol'])
        self.right = Node(json_node = json_rule['right']['symbol'])

        self.base = None
        if 'base' in json_rule:
            self.base  = Node(json_node = json_rule['base']['symbol'])

    def get_terminals(self):
        result = set()

        def add_rec(s, node):
            if node.terminal:
                s.add(node.name)

            for n in node.children:
                add_rec(s, n)

        add_rec(result, self.left)
        add_rec(result, self.right)

        return result

    def get_nterminals(self):
        result = set()

        def add_rec(s, node):
            if node.terminal:
                s.add(node.name)

            for n in node.children:
                add_rec(s, n)

        add_rec(result, self.left)
        add_rec(result, self.right)

        return result

    def copy_right(self):
        return Node(other_node = self.right)

    def copy_left(self):
        return Node(other_node = self.left)

    def is_applicable(self, node):
        def check_rec(node1, node2):
            result = Rule.__ndeep_eq(node1, node2)
            result &= len(node1.children) <= len(node2.children)
            
            if result:
                for node1_child in node1.children:
                    found = False
                    for node2_child in node2.children:
                        #if node1_child == node2_child:
                        if Rule.__ndeep_eq(node1_child, node2_child):
                            found = check_rec(node1_child, node2_child)

                            if found:
                                break

                    if not found:
                        result = found
                        break

            return result

        return check_rec(self.left, node)

    def __find_terminal(self, node):
        result = []

        if node.terminal:
            result.append(weakref.ref(node))

        for child in node.children:
           result += self.__find_terminal(child)

        return result

    def __find_left_above(self, node):
        if node != self.left:
            if node.parent:
                return self.__find_left_above(node.parent)

            raise Exception("Corresponding node for rule is not found")# TODO

        return node

    def __find_left_base(self, node):
        if node != self.left:
            # find one level below
            for child in node.children:
                if child == self.left:
                    return child

            # find one level above
            return self.__find_left_above(node)

        return node

    @staticmethod
    def __delete_terminal_node(node):
        if node.terminal:
            del OBJECTS[node.name][node.id]

        for child in node.children:
            Rule.__delete_terminal_node(child)

        node.children = []
        del node
        gc.collect()

    # Don't compare id of nodes
    @staticmethod
    def __ndeep_eq(node1, node2):
        return node1.terminal == node2.terminal and node1.name == node2.name

    @staticmethod
    def __dfs_by_id(node, node_name, node_id):
        if node.name == node_name and hasattr(node, 'id') and node.id == node_id:
            return True

        return reduce(lambda res, child: res | Rule.__dfs_by_id(child, node_name, node_id),
                        node.children, False)

    def apply(self, node):
        if node is None:
            return False

        if type(node) is weakref.ReferenceType:
            node = node()

        node_id = None
        node_name = node.name
        if hasattr(node, 'id'):
            node_id = node.id

        node = self.__find_left_base(node)

        if self.is_applicable(node):
            # create new
            left_node = self.copy_left()
            right_node = self.copy_right()

            # merge
            def merge_diff_rec(left, right, orig, passed_node_id, passed_node_name):
                result = []

                # some nodes are added in rule
                if len(left.children) < len(right.children):
                    # find these nodes
                    for right_child in right.children:
                        found = False
                        for left_child in left.children:
                            if left_child == right_child:
                                found = True
                                break

                        if not found:
                            orig.add(right_child)
                            result += self.__find_terminal(right_child)
                # some nodes are deleted in rule
                elif len(left.children) > len(right.children):
                    for left_child in left.children:
                        found = False
                        # try to find the same symbol in right side of rule
                        for right_child in right.children:
                            if left_child == right_child:
                                found = True
                                break

                        # if such symbol is not found it means that this symbol should be deleted
                        if not found:
                            # find and remove such symbol
                            for inx in range(len(orig.children)):
                                orig_child = orig.children[inx]
                                if self.__ndeep_eq(left_child, orig_child) and orig_child.id == passed_node_id:
                                    orig.children.pop(inx)
                                    Rule.__delete_terminal_node(orig_child)
                                    break
                # if nodes are the same
                elif len(left.children) == len(right.children):
                    orig_children = []

                    left_inx, right_inx, orig_inx = 0, 0, 0

                    while left_inx < len(left.children):
                        left_child  = left.children[left_inx]
                        right_child = right.children[right_inx]
                        orig_child  = orig.children[orig_inx]

                        while orig_inx < len(orig.children):
                            cmp_result = Rule.__ndeep_eq(left_child, orig_child)

                            if (passed_node_id is None and cmp_result) or \
                                (not passed_node_id is None and cmp_result and Rule.__dfs_by_id(orig_child, passed_node_name, passed_node_id)):
                                break

                            orig_inx += 1
                            orig_child = orig.children[orig_inx]

                        if len(orig.children) == orig_inx:
                            break

                        if left_child != right_child:
                            orig.children[orig_inx] = None
                            Rule.__delete_terminal_node(orig_child)

                            # substitute the node from right tree
                            orig.children[orig_inx] = right_child
                            orig_child = right_child
                            right_child.parent = orig

                            if not left_child.terminal:
                                result += self.__find_terminal(orig_child)

                        orig_children.append(orig_child)

                        left_inx += 1
                        right_inx += 1
                        orig_inx += 1

                    # We don't need the id below the objects with pointed name,
                    # because there is no such nodes and hence there is no such id.
                    if orig.name == passed_node_name:
                        passed_node_name, passed_node_id = None, None

                    for left_child, right_child, orig_child in zip(left.children, right.children, orig_children):
                        result.extend(merge_diff_rec(left_child, right_child, orig_child, passed_node_id, passed_node_name))

                return result

            result = merge_diff_rec(left_node, right_node, node, node_id, node_name)

            for n in result:
                n().handle_id()

                # Add to global objects
                if not n().name in OBJECTS:
                    OBJECTS[n().name] = {}

                OBJECTS[n().name][n().id] = n

            if len(result) == 1:
                return result[0]
            else:
                return result

        return None

class BaseClass(object):
    def __init__(self, classtype):
        self._type = classtype

def ClassFactory(name):
    def __init__(self):
        BaseClass.__init__(self, name)

    newclass = type(name, (BaseClass,), {"__init__" : __init__})

    return newclass

def load_model_file(file_path):
    content = json.load(open(file_path, "r"))

    rules = []

    export_classes = {}

    # list method for each class
    def list_method(cls):
        def wrapper(**kwargs):
            result = []

            for _, value in OBJECTS[cls.name].items():

                if len(kwargs):
                    for filter_key, filter_value in kwargs.items():
                        if hasattr(value, filter_key) and getattr(value, filter_key) == filter_value:
                            result.append(value)
                else:
                    result.append(value)

            return result

        return wrapper

    for rule in content['rules']:
        r = Rule(rule)
        rules.append(r)

        if not r.type in export_classes:
            cls = ClassFactory(r.type)
            export_classes[r.type] = cls
        else:
            cls = export_classes[r.type]

        setattr(cls, r.method, r.apply)
        setattr(cls, 'name', r.type)
        setattr(cls, 'list', list_method(cls))

        # register type to global list of objects
        if not r.type in OBJECTS:
            OBJECTS[r.type] = {}

    return export_classes


