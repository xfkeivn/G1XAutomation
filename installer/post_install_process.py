import sys
import os
import re
START = re.compile(b'(#![C-Zc-z]:.*python.exe)')

def update_exe_python_after_installation(exefilepath):
    print (exefilepath)
    pythonpath = os.path.dirname(os.path.dirname(exefilepath))
    pythonexename = bytes(os.path.join(pythonpath,"python.exe"),encoding='ascii')
    pythonexename = os.path.normpath(pythonexename)
    pythonexename = os.path.abspath(pythonexename)
    new_content = None
    with open(exefilepath,'r+b') as f:
        f_content = f.read()
        matched = re.search(START,f_content)
        if matched is not None:
            start,end = matched.span()
            new_content = f_content[0:start] + b'#!'+ pythonexename + f_content[end:]
        else:
            new_content = f_content
            f.close()
    os.remove(exefilepath)
    with open(exefilepath,"bw") as new_f:
        new_f.write(new_content)
        new_f.close()

if __name__ == "__main__":
    scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"Python3/Scripts"))
    scripts_path = os.path.normpath(scripts_path)
    #scripts_path = sys.argv[1]
    for exefile in os.listdir(scripts_path):
        exefilepath = os.path.join(scripts_path, exefile)
        if os.path.isfile(exefilepath) and exefile.endswith("exe") or exefile.endswith("py"):
            update_exe_python_after_installation(exefilepath)

