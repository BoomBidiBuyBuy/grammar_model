import json
import weakref
import gc
from collections import defaultdict
from functools import reduce
from .timer import Timer

UNIQUE_ID = defaultdict(lambda:0)

OBJECTS = defaultdict(lambda:{})

# generator of unique id for objects
def id_generator(name):
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
                self.add(Node(other_node = node))

        if self.terminal:
            self.id = ''

    def handle_id(self):
        if self.terminal:
            self.id = id_generator(self.name)
        elif hasattr(self, 'id'):
            del self.id

    def __eq__(self, other):
        if type(other) is weakref.ReferenceType:
            other = other()

        result = self.terminal == other.terminal

        if result and self.terminal:
            result &= self.id == other.id

        result &= self.name == other.name

        return result

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return (self.name, self.terminal) < (other.name, other.terminal)

    def __le__(self, other):
        return (self.name, self.terminal) <= (other.name, other.terminal)

    def __gt__(self, other):
        return (self.name, self.terminal) > (other.name, other.terminal)

    def __ge__(self, other):
        return (self.name, self.terminal) >= (other.name, other.terminal)

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
                    self.add(Node(json_node = symbol))
            else:
                self.add(Node(json_node = json_node['symbol']))

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

        self.time = 0.0
        if 'time' in json_rule:
            self.time = json_rule['time']

        self.error_time = 0.0
        if 'error_time' in json_rule:
            self.error_time = json_rule['error_time']

        self.left = None
        if 'left' in json_rule:
            self.left  = Node( json_node = json_rule['left']['symbol'])

        self.right = None
        if 'right' in json_rule:
            self.right = Node( json_node = json_rule['right']['symbol'])

        self.base = None
        if 'base' in json_rule:
            self.base = Node( json_node = json_rule['base']['symbol'])
        else:
            self.base = Node( name = self.type, terminal = True)

        self.context = None
        if self.left and self.right:
            self.context = self.__find_context_nodes()

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

    def is_applicable(self, node, passed_node_name, passed_node_id):
        def check_rec(node1, node2, passed_node_name, passed_node_id):
            result = Rule.__ndeep_eq(node1, node2)
            result &= len(node1.children) <= len(node2.children)
            
            if result:
                for node1_child in node1.children:
                    found = False
                    for node2_child in node2.children:
                        cmp_result = Rule.__ndeep_eq(node1_child, node2_child)
                        dfs_result = Rule.__dfs_by_id(node2_child, passed_node_name, passed_node_id)
                        in_context = (node2_child.name, node2_child.terminal) in self.context

                        if cmp_result and \
                                (passed_node_id is None or \
                                 not passed_node_id is None and (dfs_result or in_context)):

                            if node2_child.name == passed_node_name:
                                passed_node_name, passed_node_id = None, None

                            found = check_rec(node1_child, node2_child, passed_node_name, passed_node_id)

                            if found:
                                break

                    if not found:
                        result = found
                        break

            return result

        return check_rec(self.left, node, passed_node_name, passed_node_id)

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

    def __find_context_nodes(self):
        singular = self.__find_singular_nodes()
        required = self.__find_required_nodes()

        context = singular - required

        result = set()

        for name, terminal in context:
            if name != self.type:
                result.add((name, terminal))

        return result

    # Find singular nodes, that don't change.
    # It needs to find context in which rule is applied.
    def __find_singular_nodes(self):
        def find(left, right):
            result = set()

            if Rule.__ndeep_eq(left, right):
                result.add((left.name, left.terminal))

            left_inx, right_inx = 0, 0

            while left_inx < len(left.children) and \
                    right_inx < len(right.children):

                left_child, right_child = left.children[left_inx], right.children[right_inx]

                if left_child < right_child:
                    left_inx += 1
                    continue
                elif left_child > right_child:
                    right_inx += 1
                    continue

                result = result.union(find(left_child, right_child))
                left_inx += 1
                right_inx += 1

            return result

        return find(self.left, self.right)

    def __find_required_nodes(self):
        def find(left, base):
            result = set()

            if Rule.__ndeep_eq(left, base):
                result.add((left.name, left.terminal))
                return result, True

            for child in left.children:
                nodes, found = find(child, base)

                if found:
                    nodes.add((left.name, left.terminal))
                    return nodes, True

            return set(), False

        res, found = find(self.left, self.base)
        return res

    def apply_list(self, **kwargs):
        Timer.add(self.time)
        result = []

        for _, value in OBJECTS[self.type].items():
            if len(kwargs):
                for filter_key, filter_value in kwargs.items():
                    if hasattr(value, filter_key) and getattr(value, filter_key) == filter_value:
                        result.append(value)
            else:
                result.append(value)

        return result

    def apply(self, node = None, is_error = False, **kwargs):
        if self.method == 'list':
            return self.apply_list(**kwargs)

        if is_error:
            Timer.add(self.error_time)
            return None
        Timer.add(self.time)

        if node is None:
            return None

        if type(node) is weakref.ReferenceType:
            node = node()

        node_id = None
        node_name = node.name
        if hasattr(node, 'id'):
            node_id = node.id

        node = self.__find_left_base(node)

        if self.is_applicable(node, node_name, node_id):
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

                    # modify case
                    if len(left.children) == len(right.children) == 0:
                        orig.__dict__.update(**kwargs)

                    while left_inx < len(left.children):
                        left_child  = left.children[left_inx]
                        right_child = right.children[right_inx]
                        orig_child  = orig.children[orig_inx]

                        while orig_inx < len(orig.children):
                            cmp_result = Rule.__ndeep_eq(left_child, orig_child)
                            dfs_result = Rule.__dfs_by_id(orig_child, passed_node_name, passed_node_id)
                            in_context = (orig_child.name, orig_child.terminal) in self.context

                            if cmp_result and \
                                    (passed_node_id is None or \
                                     not passed_node_id is None and (dfs_result or in_context)):
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

                OBJECTS[n().name][n().id] = n

            if len(result) == 1:
                result[0]().__dict__.update(**kwargs)
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

    type = content['type']

    for rule in content['rules']:
        rule.update({'type': type})
        r = Rule(rule)
        rules.append(r)

        if not r.type in export_classes:
            cls = ClassFactory(r.type)
            export_classes[r.type] = cls
        else:
            cls = export_classes[r.type]

        setattr(cls, r.method, r.apply)
        setattr(cls, 'name', r.type)

        # register type to global list of objects
        if not r.type in OBJECTS:
            OBJECTS[r.type] = {}

    return export_classes