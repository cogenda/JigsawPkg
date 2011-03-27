__all__ = ['Repository', 'World', 'Package', 'writeFile', 'GNUPackage', 'mode']

import os, os.path, shutil, tempfile, glob
import tarfile, zipfile, subprocess, re, string
try:
    from hashlib import sha1
except:
    import sha as sha1


mode = 'src'

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
    lines = fin.readlines(1024)
    fin.close()

    fout = open(path, 'w')
    for l in lines:
        if mode=='re':
            fout.write(re.sub(pattern, replace, l))
        else:
            fout.write(string.replace(l, pattern, replace))
    fout.close()

class Repository(object):
    def __init__(self, rootDir, tmpDir='/tmp'):
        self.rootDir = rootDir
        self.tmpDir = tmpDir
        self.objects = []

        self.scan()

    def scan(self):
        for dir in os.listdir(self.rootDir):
            if not os.path.isdir(os.path.join(self.rootDir,dir)): continue

            parts = dir.split('.')
            self.objects.append((parts[0],                  # name
                                 '.'.join(parts[1:-1]),     # version
                                 parts[-1],                 # signature
                                 dir                        # dir
                                ))

    def addPackage(self, package):
        # check if all features have been installed
        installed=True
        for obj in package.features:
            dir=package.dirName(obj)
            if not os.path.isdir(os.path.join(self.rootDir, dir)):
                installed=False
        if installed: return # nothing to do

        # add all dependencies
        for _,dep in package.deps.iteritems():
            self.addPackage(dep)

        # prepare package
        package.workDir = os.path.join(self.tmpDir, 'build.%s' % package.dirName())
        package._fetch()
        package._patch()

        # prepare world for build
        worldDir = tempfile.mkdtemp(dir=self.tmpDir)
        world = World(self, rootDir=worldDir)
        for _,dep in package.deps.iteritems():
            world.addPackage(dep)
        world.make()
        package._build(worldDir)
        world.unmake()

        sig=package.sig()
        # install, diff, and add to repo
        for obj in package.features:
            world.make()
            package._install(worldDir,obj)
            world.unmake()

            dir = package.dirName(obj)
            shutil.move(worldDir, os.path.join(self.rootDir, dir))
            self.objects.append((obj, package.version, sig, dir))

        # clean up
        #package._cleanup()

    def getObjPath(self, name=None, ver=None, sig=None):
        for oName, oVer, oSig, oDir in self.objects:
            if name and not name==oName: continue
            if ver  and not ver==oVer:   continue
            if sig  and not sig==oSig:   continue

            return os.path.join(self.rootDir, oDir)
        return None

class World(object):
    def __init__(self, repo, rootDir=None):
        self.repo = repo
        self.packages = {}
        self.rootDir = rootDir
        self.fileList = []

    def addPackage(self, package):
        def _doAdd(package):
            if not self.packages.has_key(package.sig()):
                self.packages[package.sig()] = (package, False) # not installed yet.
            for _, dep in package.deps.iteritems():
                _doAdd(dep)
                
        _doAdd(package)

    def make(self):
        '''make world, if any requested packages aren't installed yet,
           install them.'''

        def _make_package(package):
            for _, dep in package.deps.iteritems():
                _make_package(dep)          # make deps first

            for feature in package.features:
                oDir = self.repo.getObjPath(feature, sig=package.sig())
                lst = package._installWorld(self.rootDir, oDir, feature)
                self.fileList.extend(lst)
            self.packages[package.sig()] = (package,True)

        if len(self.fileList)>0:
            raise Error

        for d in ['.', 'bin', 'include', 'lib', 'share']:
            dir = os.path.join(self.rootDir, d)
            if not os.path.exists(dir):
                os.makedirs(dir)

        for _,(package, installed) in self.packages.iteritems():
            if not installed:
                print 'make %s' % ','.join(package.features)
                _make_package(package)

    def unmake(self):
        for f in self.fileList:
            os.unlink(f)
        self.fileList=[]

        for path, dirs, files in os.walk(self.rootDir, topdown=False):
            if len(dirs)==0 and len(files)==0:
                os.rmdir(path)

    def destroy(self):
        if os.path.exists(self.rootDir):
            shutil.rmtree(self.rootDir)

class Package(object):
    name = 'Unknown'
    version = '1.0'
    prereqs = []
    prereqs_src = []

    src_url = None

    def __init__(self, *args):
        self.deps = {}

        deps,kwargs=[],{}
        if len(args)>0: deps=args[0]
        if len(args)>1: kwargs=args[1]
        for dep in deps:
            self.deps[dep.name] = dep

        # possible options
        if not self.__class__.__dict__.has_key('optionList'):
            self.optionList = []

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
        maps = [self.__dict__, self.__class__.__dict__]
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

    def checkPreReq(self):
        avail = {}
        for _,dep in self.deps.iteritems():
            for f in dep.features:
                avail[f] = True
        for req in self.prereqs:
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

    def fetch(self):
        if self.src_url==None:
            return

        src_dir = os.path.join(self.workDir, 'src')
        if os.path.exists(src_dir):
            return

        src_file=None
        if self.src_url.startswith('http'):
            pass
        else:
            if not os.path.exists(self.src_url):
                raise Error
            src_file = self.src_url
            
        if tarfile.is_tarfile(src_file):
            tf = tarfile.open(src_file)
            tf.extractall(self.workDir)
        elif zipfile.is_zipfile(src_file):
            zf = zipfile.open(src_file)
            zf.extractall(self.workDir)

        src_dir = os.path.join(self.workDir, 'src')
        if os.path.lexists(src_dir):
            os.unlink(src_dir)
        os.symlink(os.listdir(self.workDir)[0], src_dir)

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

    def _subst_vars(self, lst, tgtDir):
        def _var(match):
            name=match.group(1)
            if name=='TGTDIR':      return tgtDir

        res = []
        for o in lst:
            res.append(re.sub('\$\{([a-zA-Z_]+)\}', _var, o))
        return res

class GNUPackage(Package):
    autoconf = ['autoconf',]
    conf_args = []

    def __init__(self, *args, **kwargs):
        super(GNUPackage, self).__init__(args, kwargs)

    def build(self, tgtDir):
        srcDir = os.path.join(self.workDir, 'src')

        # autoconf
        if not os.path.exists(os.path.join(srcDir, 'configure')):
            for cmd in self.autoconf:
                ret = subprocess.call(cmd, cwd=srcDir)
                if not ret==0:
                    raise Exception('Failed to execute %s' % str(cmd))

        # configure
        cmd = ['./configure']
        cmd.extend(self._opt_merge_lists('conf_args'))
        cmd = self._subst_vars(cmd, tgtDir)

        print cmd
        ret = subprocess.call(cmd, True, cwd=srcDir)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

        cmd = ['make', '-j4']
        ret = subprocess.call(cmd, cwd=srcDir)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src')
        cmd = ['make', 'install']

        print cmd
        ret = subprocess.call(cmd, cwd=srcDir)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

        # fix pkgconfig
        for f in glob.glob('%s/lib/pkgconfig/*.pc' % tgtDir):
            subTxtFile(f, tgtDir, 'JIG_WORLD_DIR')

    def installWorld(self, wldDir, objDir, obj):
        fileList = super(GNUPackage, self).installWorld(wldDir, objDir, obj)

        # fix pkgconfig
        for f in glob.glob('%s/lib/pkgconfig/*.pc' % objDir):
            tgtPath = os.path.join(wldDir, os.path.relpath(f, objDir))
            os.unlink(tgtPath)
            shutil.copy(f,tgtPath)
            subTxtFile(tgtPath, 'JIG_WORLD_DIR', wldDir)

        return fileList


