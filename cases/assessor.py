import cases_dns
import cases_dhsm
import cases_ldap
import cases_ndmp
import cases_nfs
import cases_nis
import cases_cifs
import cases_nfs_share
import cases_cifs_share
import cases_nas
from core.timer import Timer
from common import clearAll,restore
import random

RESULTS = {}

def assess(funcs):
    Timer.refresh()

    last_name, last_mod = funcs[-1]
    prev_key = ''.join([name for name, module in funcs[:-1]])
    key = prev_key + last_name

    if prev_key in RESULTS:
        l_time, pool = RESULTS[prev_key]

        restore(pool)
        Timer.enable()
        getattr(last_mod, last_name)()
        time = l_time + Timer.time()
    else:
        Timer.enable()
        [getattr(module, name)() for name, module in funcs]
        time = Timer.time()

    pool = clearAll()
    #RESULTS[key] = (time, pool())

    return time

def find_for(check_array, funcs, mask):
    #print("Progress: ", str((len(check_array)/len(funcs) * 100.0)) + "%")
    result = None
    res_inx = None
    for inx in range(len(funcs)):
        if mask[inx]:
            continue

        loc_result = assess(check_array + [funcs[inx]])

        if not result or result > loc_result:
            result = loc_result
            res_inx = inx

    if res_inx is None:
        return None, check_array

    mask[res_inx] = True
    rec_result, rec_array = find_for(check_array + [funcs[res_inx]], funcs, mask)
    mask[res_inx] = False

    if rec_result is None:
        rec_result = result

    return rec_result, rec_array

def find_best(funcs):
    mask = [False for _ in range(len(funcs))]

    res_array = None
    res_time = None

    for inx in range(len(funcs)):
        mask[inx] = True
        rec_result, rec_array = find_for([funcs[inx]], funcs, mask)
        print(rec_result)#, str((inx / len(funcs)) * 100.0) + "%" )
        RESULTS.clear()
        mask[inx] = False

        if res_time is None or res_time > rec_result:
            res_array = rec_array
            res_time = rec_result

    return res_time, res_array

if __name__ == '__main__':
    random.seed()

    modules = [cases_dhsm, cases_dns, cases_ldap,
               cases_ndmp, cases_nfs, cases_nis,
               cases_nfs, cases_nfs_share, cases_cifs_share,
               cases_cifs, cases_nas]

    funcs = []

    for module in modules:
        for name in dir(module):
            if name.startswith('t_'):
                funcs.append((name, module))

    data_file= open("../distribution_analys/data1", "w")
    log_file = open("output.log", "w")

    log_str = ""

    funcs.sort(key=lambda x: x[0])
    print(assess(funcs))
    print("-----------------------")

    N = 10000

    try:
        for _ in range(10000):
            print(str((_ / N) * 100.0) + "%")
            random.shuffle(funcs)

            log_str = '[' + ''.join([name + ', ' for name, module in funcs]) + ']'

            data_file.write(str(assess(funcs)) + '\n')
            data_file.flush()
    finally:
        log_file.write(log_str)
        log_file.close()
        data_file.close()

    #best_time, best_funcs = find_best(funcs)
    #print(best_time)
    #for name, module in best_funcs:
    #    print(name + "()")

