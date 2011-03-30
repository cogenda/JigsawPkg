__all__=['writeFile', 'copyX', 'subTxtFile']

import os, os.path, shutil, tempfile, glob
import re, string

# {{{ utils
def copyX(src, dst):
    dir=os.path.dirname(dst)
    if not os.path.exists(dir): os.makedirs(dir)

    if os.path.isdir(src):
        shutil.copytree(src, dst, symlinks=True)
    elif os.path.islink(src):
        dir,fname = os.path.split(dst)
        linkto = os.readlink(src)
        os.symlink(linkto, dst)
    else:
        shutil.copy2(src, dst)


def writeFile(rootpath, relpath, data, mode=0666, uid=-1, gid=-1):
    fname = os.path.join(rootpath, relpath)
    dir,_ = os.path.split(fname)
    if not os.path.exists(dir):
        os.makedirs(dir)
    f = open(fname, 'w')
    f.write(data)
    f.close()

    os.chown(fname, uid, gid)
    os.chmod(fname, mode)

def subTxtFile(path, pattern, replace, mode='plain'):
    fin = open(path, 'r')
    lines = fin.readlines()
    fin.close()

    fout = open(path, 'w')
    for l in lines:
        if mode=='re':
            fout.write(re.sub(pattern, replace, l))
        else:
            fout.write(string.replace(l, pattern, replace))
    fout.close()
# }}}

