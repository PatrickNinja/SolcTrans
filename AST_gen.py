import solcx.wrapper as sl
import solcx
import re
import json
import sys
import pymysql
import AST_parse
import function_extract

from contextlib import contextmanager
import threading
import _thread

class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg

@contextmanager
def time_limit(seconds, msg=''):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException("Timed out for operation {}".format(msg))
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()




def gen_AST(solpath,astpath):

    with open(solpath, 'r', encoding='utf-8') as f:
        solfile = f.read()
    f.close()
    version_list = re.findall(r'pragma solidity (.*);', solfile)

    # if version_list == [] or int(version_list[0].split('.')[-1]) < 12:
    #     exit(0);



    version = '0.'+ version_list[0].split('.')[-2] + '.' + version_list[0].split('.')[-1]


    print('Solidity ver:' + version)
    installed_solcs = solcx.get_installed_solc_versions()

    stdout = ""
    try:
        for ver in installed_solcs:
            solcx.set_solc_version(ver)
            try:
                stdout, stderr, lst, Popen = sl.solc_wrapper(solc_binary=None, stdin=None, source_files=solpath, import_remappings=None, success_return_code=None, devdoc=True)
            except Exception as e:
                continue
            break
    except Exception as e:
        print("compile error")


    if stdout is "":
        print("compile error")

    start = re.escape('=======')
    end = re.escape('=======')
    stdout = re.sub(r'%s(?:.|\s)*?%s' % (start, end), '',stdout)
    stdout = re.sub(r'Developer Documentation','',stdout)
    f = open(astpath,'w') #location of AST files
    f.write(stdout)
    f.close()
    stdout = re.sub('}\s*{','},{',stdout)
    lst = json.loads('['+stdout+']')
    func_comments ={}
    for contract in lst:
        # keys = list(contract.get('methods').keys())
        # print(contract)
        for key,value in contract.get('methods').items():
            func_comments[key]=value.get('details')
    # print(func_comments)
    if func_comments =={}:
        print(func_comments)




    # solfile = re.sub(r'%s(?:.|\s)*?%s' % ('require', ';'), remove_require_msg,solfile)
    #
    # f = open(solpath, 'w', encoding='utf-8')
    # f.write(solfile)
    # f.close()

    stdout, stderr, lst, Popen = sl.solc_wrapper(solc_binary=None, stdin=None, source_files=solpath, import_remappings=None, success_return_code=None, ast_compact_json=True)
    stdout = re.sub(r'%s(?:.|\s)*?%s' % (start, end), '',stdout)
    stdout = re.sub(r'JSON AST \(compact format\):','',stdout)
    f = open(astpath, 'w', encoding='utf-8')
    f.write(stdout)
    f.close()


if __name__ == "__main__":
    gen_AST(sys.argv[1],sys.argv[2])















# f = open('D:/func.json','w')
# f.write(stdout)
# f.close()