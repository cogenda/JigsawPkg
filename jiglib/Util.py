__all__=['writeFile', 'copyX', 'subTxtFile', 'substVars', 'version2int']

import sys, os, os.path, shutil, tempfile, glob
import re, string

# {{{ copyX
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
# }}}

# {{{ writeFile
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
# }}}

# {{{ subTxtFile
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

# {{{ version2int
def version2int(ver):
    parts = re.split(r'\.|-p?', ver)
    v = 0
    for i in xrange(4):
        v *= 100
        if i<len(parts):
            try: v += int(parts[i])
            except: pass
    return v
# }}}

# {{{ substVars
def substVars(lst_or_dict, vars):
    def _var(match):
        name=match.group(1)
        if vars.has_key(name):  return vars[name]

    pattern = '\$\{([a-zA-Z_]+)\}'
    if isinstance(lst_or_dict, str):
        return re.sub(pattern, _var, lst_or_dict)
    if isinstance(lst_or_dict, list):
        res = []
        for o in lst_or_dict:
            res.append(re.sub(pattern, _var, o))
        return res
    elif isinstance(lst_or_dict, dict):
        res = {}
        for k,v in lst_or_dict.iteritems():
            res[k] = re.sub(pattern, _var, v)
        return res
# }}}

# {{{ os.path.relpath()
# Creates os.path.relpath for Python 2.4
if not hasattr(os.path, 'relpath'):
    if os.path is sys.modules.get('ntpath'):
        def relpath(path, start=os.path.curdir):
            """Return a relative version of a path"""
        
            if not path:
                raise ValueError("no path specified")
            start_list = os.path.abspath(start).split(os.path.sep)
            path_list = os.path.abspath(path).split(os.path.sep)
            if start_list[0].lower() != path_list[0].lower():
                unc_path, rest = os.path.splitunc(path)
                unc_start, rest = os.path.splitunc(start)
                if bool(unc_path) ^ bool(unc_start):
                    raise ValueError("Cannot mix UNC and non-UNC paths (%s and %s)"
                                                                        % (path, start))
                else:
                    raise ValueError("path is on drive %s, start on drive %s"
                                                        % (path_list[0], start_list[0]))
            # Work out how much of the filepath is shared by start and path.
            for i in range(min(len(start_list), len(path_list))):
                if start_list[i].lower() != path_list[i].lower():
                    break
            else:
                i += 1
        
            rel_list = [os.path.pardir] * (len(start_list)-i) + path_list[i:]
            if not rel_list:
                return os.path.curdir
            return os.path.join(*rel_list)
    
    else:
        # default to posixpath definition
        def relpath(path, start=os.path.curdir):
            """Return a relative version of a path"""
        
            if not path:
                raise ValueError("no path specified")
        
            start_list = os.path.abspath(start).split(os.path.sep)
            path_list = os.path.abspath(path).split(os.path.sep)
        
            # Work out how much of the filepath is shared by start and path.
            i = len(os.path.commonprefix([start_list, path_list]))
        
            rel_list = [os.path.pardir] * (len(start_list)-i) + path_list[i:]
            if not rel_list:
                return os.path.curdir
            return os.path.join(*rel_list)
        
    os.path.relpath = relpath
# }}}

