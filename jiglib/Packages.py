__all__ = ['Package', 'SystemPackage', 
           'GNUPackage', 'CMakePackage', 'PythonPackage', 'WafPackage',]

import os, os.path, shutil, tempfile, glob
import tarfile, zipfile, re, string
import urlparse, urllib
try:
    from hashlib import sha1
except:
    from sha import new as sha1
from Util import *
import Settings
from Logger import *

# {{{ class Package
class Package(object):
    def _setDefault(self, name, val):
        if not (self.__dict__.has_key(name) or 
                self.__class__.__dict__.has_key(name)):
            self.__dict__[name] = val

    # {{{ __init__()
    def __init__(self, *args, **kwargs):
        self._setDefault('name', 'Unknown')
        self._setDefault('version', '1.0')
        self._setDefault('prereqs', [])
        self._setDefault('prereqs_src', [])
        self._setDefault('src_url', None)
        self._setDefault('optionList', []) # possible options
        self._setDefault('env', {})
        self._setDefault('patches', [])
        self._setDefault('logger', std_logger)

        # all dependencies
        self.deps = {}
        
        # explicitly declared deps, for calculating signature
        self.args = {}

        for dep in args:
            self.deps[dep.name] = dep
            self.args[dep.name] = dep

        # selected options
        self.options = kwargs.get('options', [])

        self.prereqs = self._opt_merge_lists('prereqs')
        if Settings.mode=='src':
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
    # }}}

    # {{{ _opt_merge_lists()
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
    # }}}

    # {{{ _opt_merge_dict
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
    # }}}

    # {{{ checkPreReq()
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
    # }}}

    # {{{ sig()
    def sig(self):
        lst = [self.name, self.version]
        lst.extend(self.options)
        for _,dep in self.args.iteritems():
            lst.append(str(dep.sig()))
        #lst.append(str(self.__class__.build.__hash__()))
        #lst.append(str(self.__class__.install.__hash__()))
        
        return sha1(','.join(lst)).hexdigest()[0:7]
    # }}}

    # {{{ dirName
    def dirName(self, obj=None):
        if obj==None:   name=self.features[0]
        else:           name=obj
        return '%s.%s.%s' % (name, self.version, self.sig())
    # }}}

    # {{{ patch
    def patch(self, tgtDir):
        patches = self._opt_merge_lists('patches')
        for i,patch in enumerate(patches):
            self.logger.write_begin('Applying patch %d' % (i+1))
            if isinstance(patch, tuple):
                patch, mandatory = patch
            else: mandatory = False

            if patch.startswith('/') or len(patch)<256:
                # probably a patch file
                patch = self._subst_vars(patch, {'TGTDIR': tgtDir})
                if os.path.exists(patch):
                    patch = open(patch).read()

            ret = cmd_n_log(['patch', '-p1'],
                            input=patch,
                            cwd=os.path.join(self.workDir, 'src'),
                            logger=self.logger)
            if ret==None:
                self.logger.write_end('fail')
                if mandatory:
                    raise Exception
            else:
                self.logger.write_end('ok')
    # }}}

    def _patch(self, tgtDir):
        self.patch(tgtDir)

    def build(self, tgtDir):
        pass

    def install(self, tgtDir, obj):
        pass

    def _build(self, tgtDir):
        self.logger.write('building package %s v%s in %s' % (self.name, self.version, self.workDir))
        self.build(tgtDir)

    def _install(self, tgtDir, obj=None):
        if obj==None:   obj=self.features[0]
        self.logger.write('installing package %s v%s in %s' % (obj, self.version, tgtDir))
        self.install(tgtDir, obj)

    def _cleanup(self):
        if os.path.exists(self.workDir):
            shutil.rmtree(self.workDir)

    def _fetch(self):
        self.logger.write('fetching package %s v%s in %s' % (self.name, self.version, self.workDir))
        self.fetch()

    # {{{ _getFile()
    def _getFile(self, urls):
        ''' get a file and save in workDir
            @return fname, isArchive'''

        for url in urls:
            if isinstance(url, tuple):
                url, arg = url[0:2]
            else:
                arg = None
            self.logger.write('Trying to download from %s.' % url)

            if url.startswith('ssh+git') or \
               url.startswith('http') and url.endswith('.git'):
                repoDir=os.path.join(self.workDir, 'repo')
                if os.path.exists(repoDir):
                    shutil.rmtree(repoDir)
                try:
                    ret = cmd_n_log(['git', 'clone', url, 'repo'],
                                    cwd=self.workDir,
                                    logger=self.logger)
                    if ret==None:
                        return '', False
                    if arg:
                        cmd_n_log(['git', 'checkout', arg],
                                  cwd=repoDir, logger=self.logger)
                    src_file = os.path.join(self.workDir, 'repo')
                    return src_file, False
                except:
                    self.logger.write('Failed to checkout from %s.' % url)
            elif url.startswith('http'):
                try:
                    fname = os.path.basename(urlparse.urlsplit(url)[2])
                    src_file = os.path.join(self.workDir, fname)
                    urllib.urlretrieve(url, src_file)
                    return src_file, True
                except Exception,e:
                    self.logger.write(['Failed to download from %s.' % url, str(e)])
            else:
                try:
                    if not os.path.exists(url):
                        raise Exception
                    return url, True
                except:
                    self.logger.write('Failed to download from %s.' % url)
    # }}}

    # {{{ fetch()
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
                if hasattr(tarfile.TarFile, 'extractall'):
                    tf = tarfile.open(src_file)
                    tf.extractall(self.workDir)
                else:
                    cmd = ['tar', '-xf', src_file]
                    cmd_n_log(cmd, cwd=self.workDir, logger=self.logger)
            elif zipfile.is_zipfile(src_file):
                if hasattr(zipfile.ZipFile, 'extractall'):
                    zf = zipfile.ZipFile(src_file)
                    zf.extractall(self.workDir)
                else:
                    cmd = ['unzip', src_file]
                    cmd_n_log(cmd, cwd=self.workDir, logger=self.logger)

        src_dir = os.path.join(self.workDir, 'src')
        if os.path.lexists(src_dir):
            shutil.rmtree(src_dir)
        for entry in os.listdir(self.workDir):
            epath = os.path.join(self.workDir, entry)
            if os.path.isdir(epath):
                shutil.move(epath, src_dir)
                break
    # }}}

    # {{{ installWorld()
    def installWorld(self, wldDir, objDir, obj):
        if objDir==None:
            raise Exception('Object not found in %s' % objDir)

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
                lnk = os.path.relpath(os.path.join(path,file), tgtPath)
                os.symlink(lnk, tgt)
                fileList.append(tgt)
        return fileList
    # }}}

    # {{{ _installWorld()
    def _installWorld(self, wldDir, objDir, obj=None):
        if obj==None:   obj=self.features[0]
        self.logger.write('installing package %s v%s to world %s' % (obj, self.version, wldDir))
        return self.installWorld(wldDir, objDir, obj)
    # }}}

    # {{{ _subst_vars()
    def _subst_vars(self, lst_or_dict, vars):
        v = dict(**vars)
        if not self.workDir==None:
            v['SRCDIR'] = os.path.join(self.workDir, 'src')
        return substVars(lst_or_dict, v)
    # }}}

    # {{{ _commonEnv()
    def _commonEnv(self, vars):
        env = self._opt_merge_dict('env')
        env = dict(os.environ, **env)

        tgtDir = vars.get('TGTDIR')
        env['PATH'] = '%s:%s' % (os.path.join(tgtDir,'bin'), env.get('PATH',''))
        env['LD_LIBRARY_PATH'] = '%s:%s' % (os.path.join(tgtDir,'lib'), env.get('LD_LIBRARY_PATH',''))
        return self._subst_vars(env, vars)
    # }}}


# }}}

# {{{ class SystemPackage
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
        self._setDefault('features', [self.name])
        self._setDefault('deps', {})

        self._setDefault('logger', std_logger)

    def sig(self):
        lst = [self.name, self.version]
        return sha1(','.join(lst)).hexdigest()[0:7]

    def isAvailable(self):
        raise NotImplementedError

    def installWorld(self, wldDir):
        pass

    def _installWorld(self, wldDir):
        self.logger.write('installing system package %s v%s to world %s' % (self.name, self.version, wldDir))
        self.installWorld(wldDir)

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
                cmd_n_log(cmd, cwd=srcDir, env=env, logger=self.logger)

        # configure
        if self.conf_cmd:
            cmd = list(self.conf_cmd)
            cmd.extend(self._opt_merge_lists('conf_args'))
            cmd = self._subst_vars(cmd, vars)
            cmd_n_log(cmd, cwd=srcDir, env=env, logger=self.logger)

        cmd_n_log(self.make_cmd, cwd=srcDir, env=env, logger=self.logger)

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src')
        vars = {'TGTDIR': tgtDir}

        env = self._commonEnv(vars)

        cmd_n_log(self.make_install_cmd, cwd=srcDir, env=env, logger=self.logger)

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
        cmd = list(self.conf_cmd)
        cmd.extend(self._opt_merge_lists('conf_args'))
        cmd = self._subst_vars(cmd, vars)
        cmd.append('../src')

        cmd_n_log(cmd, cwd=bldDir, env=env, logger=self.logger)

        cmd_n_log(self.make_cmd, cwd=bldDir, env=env, logger=self.logger)

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src')
        bldDir = os.path.join(self.workDir, 'build')
        vars = {'TGTDIR': tgtDir}

        env = self._commonEnv(vars)

        cmd_n_log(self.make_install_cmd, cwd=bldDir, env=env, logger=self.logger)

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
        cmd = list(self.build_cmd)
        cmd.extend(self._opt_merge_lists('build_args'))
        cmd.append(self.build_verb)
        cmd = self._subst_vars(cmd, vars)
        cmd_n_log(cmd, cwd=srcDir, env=env, logger=self.logger)

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src')
        vars = {'TGTDIR': tgtDir}

        env = self._commonEnv(vars)

        # install
        cmd = list(self.install_cmd)
        cmd.extend(self._opt_merge_lists('install_args'))
        cmd.append(self.install_verb)
        cmd = self._subst_vars(cmd, vars)
        cmd_n_log(cmd, cwd=srcDir, env=env, logger=self.logger)

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
        cmd = list(self.waf_cmd)
        cmd.extend(self._opt_merge_lists('waf_args'))
        cmd.extend(self.build_verb)
        cmd = self._subst_vars(cmd, vars)
        cmd_n_log(cmd, cwd=srcDir, env=env, logger=self.logger)

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src')
        vars = {'TGTDIR': tgtDir}

        env = self._commonEnv(vars)

        # install
        cmd = list(self.waf_cmd)
        cmd.extend(self._opt_merge_lists('waf_args'))
        cmd.extend(self.install_verb)
        cmd = self._subst_vars(cmd, vars)
        cmd_n_log(cmd, cwd=srcDir, env=env, logger=self.logger)
# }}}

