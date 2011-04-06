__all__ = ['Package', 'SystemPackage', 
           'GNUPackage', 'CMakePackage', 'PythonPackage', 'WafPackage',
           'mode']

import os, os.path, shutil, tempfile, glob
import tarfile, zipfile, subprocess, re, string
import urlparse, urllib
try:
    from hashlib import sha1
except:
    from sha import new as sha1
from Util import *

mode = 'src'

# {{{ class Package
class Package(object):
    def _setDefault(self, name, val):
        if not (self.__dict__.has_key(name) or 
                self.__class__.__dict__.has_key(name)):
            self.__dict__[name] = val

    def __init__(self, *args, **kwargs):
        self._setDefault('name', 'Unknown')
        self._setDefault('version', '1.0')
        self._setDefault('prereqs', [])
        self._setDefault('prereqs_src', [])
        self._setDefault('src_url', None)
        self._setDefault('optionList', []) # possible options
        self._setDefault('env', {})

        self.deps = {}

        for dep in args:
            self.deps[dep.name] = dep

        # selected options
        self.options = kwargs.get('options', [])

        self.prereqs = self._opt_merge_lists('prereqs')
        if mode=='src':
            self.prereqs.extend(self._opt_merge_lists('prereqs_src'))

        self.checkPreReq()

        # features provided
        featureList = self._opt_merge_lists('featureList')
        if len(featureList)==0:
            self.featureList = [self.name]

        # features requested
        features=kwargs.get('features', None)
        if features==None:
            self.features = self.featureList # all available features
        else:
            # all features requested, that are available
            self.features = []
            for f in features:
                if f in self.featureList:
                    self.features.append(f)

        self.workDir = None

    def _opt_merge_lists(self, prefix):
        maps = [self.__dict__,self.__class__.__dict__]
        appends = []
        deletes = []
        for map in maps:
            if map.has_key(prefix):
                appends.append(map[prefix])
        for opt in self.options:
            for k,l in [ ('%s_%s_append' % (prefix, opt), appends),
                         ('%s_%s_delete' % (prefix, opt), deletes) ]:
                for map in maps:
                    if map.has_key(k):
                        l.append(map[k])
    
        res = []
        for lst in appends:
            for o in lst:
                res.append(o)
        for lst in deletes:
            for o in lst:
                try: res.remove(o)
                except: pass
        return res

    def _opt_merge_dict(self, prefix):
        maps = [self.__dict__,self.__class__.__dict__]
        appends = []
        deletes = []
        for map in maps:
            if map.has_key(prefix):
                appends.append(map[prefix])
        for opt in self.options:
            for k,l in [ ('%s_%s_append' % (prefix, opt), appends),
                         ('%s_%s_delete' % (prefix, opt), deletes) ]:
                for map in maps:
                    if map.has_key(k):
                        l.append(map[k])
    
        res = {}
        for dct in appends:
            for k,v in dct.iteritems():
                res[k]=v
        for dct in deletes:
            for k,v in dct.iteritems():
                try: del res[k]
                except: pass
        return res

    def checkPreReq(self):
        avail = {}
        for _,dep in self.deps.iteritems():
            for f in dep.features:
                avail[f] = True
        for req in self.prereqs:
            if req.startswith('sys:'):
                # base system dependencies
                parts = req.split(':')
                name = parts[1]
                if len(parts)>2:
                    ver = parts[2]
                else:
                    ver = '0.0.0'
                self.deps[req] = SystemPackage(name=name, version=ver)
            else:
                if not avail.has_key(req):
                    raise Exception('Missing Pre-requisite Argument: %s' % req)

    def sig(self):
        lst = [self.name, self.version]
        lst.extend(self.options)
        for _,dep in self.deps.iteritems():
            lst.append(str(dep.sig()))
        #lst.append(str(self.__class__.build.__hash__()))
        #lst.append(str(self.__class__.install.__hash__()))
        
        return sha1(','.join(lst)).hexdigest()[0:7]

    def dirName(self, obj=None):
        if obj==None:   name=self.features[0]
        else:           name=obj
        return '%s.%s.%s' % (name, self.version, self.sig())

    def _patch(self):
        pass

    def build(self, tgtDir):
        pass

    def install(self, tgtDir, obj):
        pass

    def _build(self, tgtDir):
        print 'building package %s v%s in %s' % (self.name, self.version, self.workDir)
        self.build(tgtDir)

    def _install(self, tgtDir, obj=None):
        if obj==None:   obj=self.features[0]
        print 'installing package %s v%s in %s' % (obj, self.version, tgtDir)
        self.install(tgtDir, obj)

    def _cleanup(self):
        if os.path.exists(self.workDir):
            shutil.rmtree(self.workDir)

    def _fetch(self):
        print 'fetching package %s v%s in %s' % (self.name, self.version, self.workDir)
        self.fetch()

    def _getFile(self, urls):
        ''' get a file and save in workDir
            @return fname, isArchive'''

        for url in urls:
            print 'Trying to download from %s.' % url
            if url.startswith('http'):
                try:
                    fname = os.path.basename(urlparse.urlsplit(url)[2])
                    src_file = os.path.join(self.workDir, fname)
                    urllib.urlretrieve(url, src_file)
                    return src_file, True
                except Exception,e:
                    print 'Failed to download from %s.' % url
                    print e
            elif url.startswith('ssh+git'):
                try:
                    cmd = ['git', 'clone', url]
                    ret = subprocess.call(cmd, cwd=self.workDir)
                    if ret==0:
                        return '', False
                except:
                    print 'Failed to download from %s.' % url
            else:
                try:
                    if not os.path.exists(url):
                        raise Exception
                    return url, True
                except:
                    print 'Failed to download from %s.' % url


    def fetch(self):
        if self.src_url==None:
            return

        src_dir = os.path.join(self.workDir, 'src')
        #if os.path.exists(src_dir):
        #    return

        src_file, isarchive = self._getFile(self.src_url)
        if src_file==None:
            raise Exception('Failed fetching package %s v%s' % (self.name, self.version))

        if isarchive:
            if tarfile.is_tarfile(src_file):
                tf = tarfile.open(src_file)
                tf.extractall(self.workDir)
            elif zipfile.is_zipfile(src_file):
                zf = zipfile.ZipFile(src_file)
                zf.extractall(self.workDir)

        src_dir = os.path.join(self.workDir, 'src')
        if os.path.lexists(src_dir):
            shutil.rmtree(src_dir)
        for entry in os.listdir(self.workDir):
            epath = os.path.join(self.workDir, entry)
            if os.path.isdir(epath):
                shutil.move(epath, src_dir)
                break

    def installWorld(self, wldDir, objDir, obj):
        if objDir==None:
            raise Error

        fileList = []
        for path, dirs, files in os.walk(objDir):
            tgtPath = os.path.join(wldDir, os.path.relpath(path, objDir))
            for dir in dirs:
                tgt=os.path.join(tgtPath,dir)
                if not os.path.exists(tgt):
                    os.makedirs(tgt)
                shutil.copymode(os.path.join(path,dir), tgt)
            for file in files:
                tgt=os.path.join(tgtPath,file)
                if os.path.lexists(tgt):
                    os.unlink(tgt)
                os.symlink(os.path.join(path,file), tgt)
                fileList.append(tgt)
        return fileList

    def _installWorld(self, wldDir, objDir, obj=None):
        if obj==None:   obj=self.features[0]
        print 'installing package %s v%s to world %s' % (obj, self.version, wldDir)
        return self.installWorld(wldDir, objDir, obj)

    def _subst_vars(self, lst_or_dict, vars):
        v = dict(**vars)
        if not self.workDir==None:
            v['SRCDIR'] = os.path.join(self.workDir, 'src')
        return substVars(lst_or_dict, v)

    def _commonEnv(self, vars):
        env = self._opt_merge_dict('env')
        env = dict(os.environ, **env)

        tgtDir = vars.get('TGTDIR')
        env['PATH'] = '%s:%s' % (os.path.join(tgtDir,'bin'), env.get('PATH',''))
        env['LD_LIBRARY_PATH'] = '%s:%s' % (os.path.join(tgtDir,'lib'), env.get('LD_LIBRARY_PATH',''))
        return self._subst_vars(env, vars)


# }}}

# {{{ SystemPackage
class SystemPackage(object):
    def _setDefault(self, name, val):
        if not (self.__dict__.has_key(name) or 
                self.__class__.__dict__.has_key(name)):
            self.__dict__[name] = val

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('name'): self.name=kwargs['name']
        if kwargs.has_key('version'): self.version=kwargs['version']

        self._setDefault('name', 'Unknown')
        self._setDefault('version', '1.0')
        self._setDefault('features', [])

    def sig(self):
        lst = [self.name, self.version]
        return sha1(','.join(lst)).hexdigest()[0:7]

    def isAvailable(self):
        raise NotImplementedError

    def _installWorld(self, wldDir):
        pass

# }}}

# {{{ class GNUPackage
class GNUPackage(Package):
    def __init__(self, *args, **kwargs):
        self._setDefault('env', {})
        self._setDefault('autoconf', ['autoconf',])
        self._setDefault('conf_args', [])
        self._setDefault('conf_cmd', ['./configure'])
        self._setDefault('make_cmd', ['gmake', '-j4'])
        self._setDefault('make_install_cmd', ['gmake', 'install'])
        self._setDefault('dest_path_fixes', ['lib/pkgconfig/*.pc'])

        super(GNUPackage, self).__init__(*args, **kwargs)

    def build(self, tgtDir):
        srcDir = os.path.join(self.workDir, 'src')
        vars = {'TGTDIR': tgtDir}

        env = self._commonEnv(vars)

        # autoconf
        if not os.path.exists(os.path.join(srcDir, 'configure')) and self.autoconf:
            for cmd in self.autoconf:
                ret = subprocess.call(cmd, cwd=srcDir, env=env)
                if not ret==0:
                    raise Exception('Failed to execute %s' % str(cmd))

        # configure
        cmd = self.conf_cmd
        cmd.extend(self._opt_merge_lists('conf_args'))
        cmd = self._subst_vars(cmd, vars)

        print cmd
        ret = subprocess.call(cmd, True, cwd=srcDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

        cmd = self.make_cmd
        ret = subprocess.call(cmd, cwd=srcDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src')
        vars = {'TGTDIR': tgtDir}
        cmd = self.make_install_cmd

        env = self._commonEnv(vars)

        print cmd
        ret = subprocess.call(cmd, cwd=srcDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

        # fixes
        for fglob in self.dest_path_fixes:
            for path in glob.glob('%s/%s' % (tgtDir,fglob)):
                subTxtFile(path, tgtDir, 'JIG_WORLD_DIR')

    def installWorld(self, wldDir, objDir, obj):
        fileList = super(GNUPackage, self).installWorld(wldDir, objDir, obj)

        # fix pkgconfig
        for fglob in self.dest_path_fixes:
            for path in glob.glob('%s/%s' % (objDir,fglob)):
                tgtPath = os.path.join(wldDir, os.path.relpath(path, objDir))
                os.unlink(tgtPath)
                shutil.copy(path,tgtPath)
                subTxtFile(tgtPath, 'JIG_WORLD_DIR', wldDir)

        return fileList
# }}}

# {{{ class CMakePackage
class CMakePackage(Package):
    def __init__(self, *args, **kwargs):
        self._setDefault('env', {})
        self._setDefault('conf_args', [])
        self._setDefault('conf_cmd', ['cmake'])
        self._setDefault('make_cmd', ['gmake', '-j4'])
        self._setDefault('make_install_cmd', ['gmake', 'install'])
        self._setDefault('dest_path_fixes', ['lib/pkgconfig/*.pc'])

        super(CMakePackage, self).__init__(*args, **kwargs)

    def build(self, tgtDir):
        srcDir = os.path.join(self.workDir, 'src')
        bldDir = os.path.join(self.workDir, 'build')
        vars = {'TGTDIR': tgtDir}
        if os.path.exists(bldDir): shutil.rmtree(bldDir)
        os.makedirs(bldDir)

        env = self._commonEnv(vars)

        # configure
        cmd = self.conf_cmd
        cmd.extend(self._opt_merge_lists('conf_args'))
        cmd = self._subst_vars(cmd, vars)
        cmd.append('../src')

        print cmd
        ret = subprocess.call(cmd, True, cwd=bldDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

        cmd = self.make_cmd
        ret = subprocess.call(cmd, cwd=bldDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src')
        bldDir = os.path.join(self.workDir, 'build')
        vars = {'TGTDIR': tgtDir}
        cmd = self.make_install_cmd

        env = self._commonEnv(vars)

        print cmd
        ret = subprocess.call(cmd, cwd=bldDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

        # fixes
        for fglob in self.dest_path_fixes:
            for path in glob.glob('%s/%s' % (tgtDir,fglob)):
                subTxtFile(path, tgtDir, 'JIG_WORLD_DIR')

    def installWorld(self, wldDir, objDir, obj):
        fileList = super(CMakePackage, self).installWorld(wldDir, objDir, obj)

        # fix pkgconfig
        for fglob in self.dest_path_fixes:
            for path in glob.glob('%s/%s' % (objDir,fglob)):
                tgtPath = os.path.join(wldDir, os.path.relpath(path, objDir))
                os.unlink(tgtPath)
                shutil.copy(path,tgtPath)
                subTxtFile(tgtPath, 'JIG_WORLD_DIR', wldDir)

        return fileList
# }}}

# {{{ class PythonPackage
class PythonPackage(Package):
    def __init__(self, *args, **kwargs):
        self._setDefault('env', {})
        self._setDefault('build_args', [])
        self._setDefault('build_verb', 'build')
        self._setDefault('build_cmd',   ['python', 'setup.py'])
        self._setDefault('install_args', [])
        self._setDefault('install_verb', 'install')
        self._setDefault('install_cmd', ['python', 'setup.py'])

        super(PythonPackage, self).__init__(*args, **kwargs)

    def build(self, tgtDir):
        srcDir = os.path.join(self.workDir, 'src')
        vars = {'TGTDIR': tgtDir}

        env = self._commonEnv(vars)

        # build
        cmd = self.build_cmd
        cmd.extend(self._opt_merge_lists('build_args'))
        cmd.append(self.build_verb)
        cmd = self._subst_vars(cmd, vars)

        print cmd
        ret = subprocess.call(cmd, True, cwd=srcDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src')
        vars = {'TGTDIR': tgtDir}

        env = self._commonEnv(vars)

        # install
        cmd = self.install_cmd
        cmd.extend(self._opt_merge_lists('install_args'))
        cmd.append(self.install_verb)
        cmd = self._subst_vars(cmd, vars)

        print cmd
        ret = subprocess.call(cmd, True, cwd=srcDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

# }}}

# {{{ class WafPackage
class WafPackage(Package):
    def __init__(self, *args, **kwargs):
        self._setDefault('env', {})
        self._setDefault('waf_src_url',   ['http://waf.googlecode.com/files/waf-1.6.3'])
        self._setDefault('waf_cmd',   ['python', 'waf'])
        self._setDefault('waf_args', [])
        self._setDefault('build_verb', ['configure', 'build'])
        self._setDefault('install_verb', ['install'])

        super(WafPackage, self).__init__(*args, **kwargs)

    def fetch(self):
        super(WafPackage, self).fetch()
        
        f_waf = os.path.join(self.workDir, 'src', 'waf')
        if os.path.exists(f_waf):
            return

        # download waf script
        f, _ = self._getFile(self.waf_src_url)
        shutil.copy(f, f_waf)

    def build(self, tgtDir):
        srcDir = os.path.join(self.workDir, 'src')
        vars = {'TGTDIR': tgtDir}

        env = self._commonEnv(vars)

        # build
        cmd = self.waf_cmd
        cmd.extend(self._opt_merge_lists('waf_args'))
        cmd.extend(self.build_verb)
        cmd = self._subst_vars(cmd, vars)

        print cmd
        ret = subprocess.call(cmd, True, cwd=srcDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src')
        vars = {'TGTDIR': tgtDir}

        env = self._commonEnv(vars)

        # install
        cmd = self.waf_cmd
        cmd.extend(self._opt_merge_lists('waf_args'))
        cmd.extend(self.install_verb)
        cmd = self._subst_vars(cmd, vars)

        print cmd
        ret = subprocess.call(cmd, True, cwd=srcDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

# }}}
