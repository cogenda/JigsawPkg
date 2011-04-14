__all__ = ['Repository', 'World', 'Collection', 'BaseSystem']

import os, os.path, shutil, tempfile, glob
import re, string
from Packages import Package, SystemPackage
from Util import *
from Logger import *

# {{{ class Repository
class Repository(object):
    def __init__(self, rootDir, tmpDir='/tmp', **kwargs):
        self.rootDir = rootDir
        self.tmpDir = tmpDir
        self.objects = []

        logRepo = kwargs.get('logger', [])
        if not isinstance(logRepo, list):
            logRepo=[logRepo]
        logRepo.append(Logger(open(os.path.join(rootDir, 'output.log'), 'a'), 1))
        self.logger = MultiLogger(logRepo)

        self.scan()

    def scan(self):
        for dir in os.listdir(self.rootDir):
            path = os.path.join(self.rootDir,dir)
            if os.path.islink(path) or not os.path.isdir(path): continue
            if dir.startswith('tmp.'): continue   # temp dirs where packages are being built

            parts = dir.split('.')
            self.objects.append((parts[0],                  # name
                                 '.'.join(parts[1:-1]),     # version
                                 parts[-1],                 # signature
                                 dir                        # dir
                                ))

    def addPackage(self, package):
        if not isinstance(package, Package): 
            return

        # check if all features have been installed
        installed=True
        for obj in package.features:
            dir=self.getObjPath(obj, sig=package.sig())
            if dir==None: installed=False
        if installed: return # nothing to do

        deps = package.deps.values()
        # add all dependencies
        for dep in deps:
            self.addPackage(dep)

        package.workDir = os.path.join(self.tmpDir, 'build.%s' % package.dirName())

        # prepare world for build
        tgtDir   = os.path.join(self.rootDir, package.dirName())
        sig=package.sig()

        worlds=[None]*len(package.features)
        for i,obj in enumerate(package.features):
            if not self.getObjPath(obj, sig=package.sig())==None:
                continue # this feature has been installed

            worldDirName = 'tmp.%s'% package.dirName(obj)
            worldDir = os.path.join(self.rootDir, worldDirName)
            if os.path.exists(worldDir):
                shutil.rmtree(worldDir)
            os.makedirs(worldDir)
            if i==0:
                if os.path.lexists(tgtDir): os.unlink(tgtDir)
                os.symlink(worldDirName, tgtDir)   # first (default) feature uses tgtDir
                world = World(self, rootDir=tgtDir)
            else:
                world = World(self, rootDir=worldDir)

            for dep in deps:
                world.addPackage(dep)
            world.make()
            worlds[i] = world

        if not os.path.exists(package.workDir):
            os.makedirs(package.workDir)

        # log for building the package
        logPkg = Logger(open(os.path.join(package.workDir, 'output.log'), 'w+'))
        package.logger = MultiLogger([self.logger, logPkg])

        # build if necessary
        if not os.path.exists(os.path.join(package.workDir, 'finished')):

            # prepare package
            package._fetch()
            package._patch()

            package._build(tgtDir)
            writeFile(package.workDir, 'finished', '1') # mark it as finished

        # install, diff, and add to repo
        for i,obj in enumerate(package.features):
            if not self.getObjPath(obj, sig=package.sig())==None:
                continue # this feature has been installed

            world = worlds[i]
            package._install(world.rootDir,obj)
            world.unmake()

            dir = package.dirName(obj)
            if i==0:
                linkto = os.readlink(tgtDir)
                os.unlink(tgtDir)  # remove the symlink for default feature
                os.rename(os.path.join(self.rootDir, linkto), os.path.join(self.rootDir, dir))
            else:
                os.rename(world.rootDir, os.path.join(self.rootDir, dir))
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
# }}}

# {{{ class World
class World(object):
    def __init__(self, repo, rootDir=None, **kwargs):
        self.repo = repo
        self.packages = {}
        self.rootDir = rootDir
        self.fileList = []

        self.logger = kwargs.get('logger', std_logger)

    def addPackage(self, package):
        def _doAdd(package):
            if not isinstance(package, Package):
                return
            if not self.packages.has_key(package.sig()):
                self.packages[package.sig()] = (package, False) # not installed yet.
            for _, dep in package.deps.iteritems():
                _doAdd(dep)
                
        _doAdd(package)

    def make(self):
        '''make world, if any requested packages aren't installed yet,
           install them.'''

        if len(self.fileList)>0:
            raise Error

        for d in ['.', 'bin', 'include', 'lib', 'share']:
            dir = os.path.join(self.rootDir, d)
            if not os.path.exists(dir):
                os.makedirs(dir)

        avails   = {}
        requests = {}

        # {{{ available & request
        def _available(package):
            for f in package.features:
                avails[f] = package
            for _,dep in package.deps.iteritems():
                _available(dep)
        
        def _requestDep(package):
            for f in package.prereqs:
                if f.startswith('sys:'):
                    continue # sys requirement
                requests[f] = True
            for _,dep in package.deps.iteritems():
                if isinstance(dep, Package):
                    _requestDep(dep)
        # }}}
        
        for _,(package, installed) in self.packages.iteritems():
            _available(package)
            for f in package.features:
                requests[f] = True
            _requestDep(package)

        to_install = {}
        for req in requests.keys():
            if not avails.has_key(req):
                raise Exception('Prerequisite %s not met', req)
            package = avails[req]
            if to_install.has_key(package):
                to_install[package].append(req)
            else:
                to_install[package] = [req]


        for package, features in to_install.iteritems():
            if package.features[0] in features:
                features = [package.features[0]] # first feature contains everything
            for feature in features:
                self.logger.write('activating %s' % feature)
                oDir = self.repo.getObjPath(feature, sig=package.sig())
                if isinstance(package, Package):
                    lst = package._installWorld(self.rootDir, oDir, feature)
                    self.fileList.extend(lst)
                elif isinstance(package, SystemPackage):
                    pass
                else:
                    raise TypeError
            self.packages[package.sig()] = (package,True)



    def unmake(self):
        for f in self.fileList:
            os.unlink(f)
        self.fileList=[]

        # clean-up empty dirs
        def _cleandir(path):
            empty=True
            for entry in os.listdir(path):
                ent_path = os.path.join(path, entry)
                if os.path.isdir(ent_path):
                    empty = _cleandir(ent_path) and empty
                else:
                    empty = False
            if empty and not path==self.rootDir:
                os.rmdir(path)
            return empty
        _cleandir(self.rootDir)


    def destroy(self):
        if os.path.exists(self.rootDir):
            shutil.rmtree(self.rootDir)

# }}}

# {{{ BaseSystem
class BaseSystem(object):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger', std_logger)

        relf = os.path.join('/etc', 'redhat-release')
        if not os.path.exists(relf):
            raise Exception('Only Redhat-based Linux is supported.')

        line = open(relf).readlines()[0]
        match = re.match(r'(?P<vendor>.*?)\s+release\s+(?P<version>[0-9\.]+)\s.*', line)
        if match==None:
            raise Exception('Version string not recognized')
        vendor, version = match.group('vendor'), match.group('version')

        if vendor=='CentOS' or vendor.startswith('Red Hat'):
            if version2int(version)<5000000:
                raise Exception('Need at least CentOS 5.0')
            self.logger.write('Found %s %s' % (vendor, version))
        else:
            raise Exception('We do not know %s %s' % (vendor, version))

        self.vendor, self.version = vendor, version

        import platform
        self.arch = platform.machine()
        if not self.arch=='x86_64':
            raise Exception('Only x86_64 system is supported')

        self.rpms = {}
        lines = cmd_n_log(['yum', 'list', 'installed'], logger=self.logger)
        for line in lines[2:]:
            try:
                name, ver, _ = line.split()
                self.rpms[name] = ver
            except:
                self.logger.write('unrecognized system package: ' + line)

    def hasPackage(self, package):
        if not isinstance(package, SystemPackage):
            raise TypeError

        try:
            return package.isAvailable()
        except NotImplementedError:
            # in base system
            name = '%s.%s' % (package.name, self.arch)
            if not self.rpms.has_key(name):
                return False

            ver = self.rpms[name]
            if version2int(ver) < version2int(package.version):
                return False

            package.version = ver   # the actual verson found
            return True

# }}}

# {{{ Collection
class Collection(object):
    def __init__(self, repo, baseSys, **kwargs):
        self.repo = repo
        self.baseSys = baseSys
        
        self.logger = kwargs.get('logger', std_logger)

    def packages(self):
        lst = []
        for k,v in self.__class__.__dict__.iteritems():
            if k.startswith('_'): continue
            if isinstance(v, Package):
                lst.append(v)
        return lst

    def systemPkgs(self):
        lst = []
        for k,v in self.__class__.__dict__.iteritems():
            if isinstance(v, SystemPackage):
                lst.append(v)
        for p in self.packages():
            for _,dep in p.deps.iteritems():
                if isinstance(dep, SystemPackage):
                    lst.append(dep)
        return lst


    def checkSysDeps(self):
        missList=[]
        for p in self.systemPkgs():
            if not self.baseSys.hasPackage(p):
                missList.append(p)
        if len(missList)>0:
            self.logger.write('The following system packages are required')
            for p in missList:
                self.logger.write('%20s   %s' % (p.name, p.version))
            return False
        return True

    def install(self, wldDir):
        world = World(self.repo, wldDir)

        if not self.checkSysDeps(): return

        for p in self.systemPkgs():
            p._installWorld(wldDir)
        for p in self.packages():
            world.addPackage(p)
        world.make()

        # write setenv script
        script='''#!/bin/sh
export PATH=${TGTDIR}/bin:$PATH
if [[ "x$LD_LIBRARY_PATH" == "x" ]]
then
    export LD_LIBRARY_PATH=${TGTDIR}/lib
else
    export LD_LIBRARY_PATH=${TGTDIR}/lib:$LD_LIBRARY_PATH
fi
'''
        script = substVars(script, {'TGTDIR':wldDir})

        writeFile(wldDir, 'bin/setenv.sh', script, mode=0755)



    def build(self):
        if not self.checkSysDeps(): return

        for p in self.packages():
            self.repo.addPackage(p)
# }}}


