from typing import *
import ipy
import os
import sys

def run_app(path:str):
    # reading file
    with open(path, encoding='utf-8') as f:
        ipyp = ipy.IPYP(f.read(), os.path.basename(path))
    
    # compiling
    try:
        app = ipy.App(ipyp)
    except ipy.BaseException as e:
        print(e.text, file=sys.stderr)

    # running
    try:
        app.run()
    except ipy.BaseException as e:
        print(e.text, file=sys.stderr)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python runner.py <file>', file=sys.stderr)
        sys.exit(1)

    file = os.path.abspath(sys.argv[1])
    path = os.path.dirname(file)
    os.chdir(path)
    run_app(os.path.basename(file))
    