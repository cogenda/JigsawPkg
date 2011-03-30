__all__ = ['Repository', 'World']

import os, os.path, shutil, tempfile, glob
import re, string
from Packages import Package, SystemPackage
from Util import *

# {{{ class Repository
class Repository(object):
    def __init__(self, rootDir, tmpDir='/tmp'):
        self.rootDir = rootDir
        self.tmpDir = tmpDir
        self.objects = []

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

        # build if necessary
        if not os.path.exists(os.path.join(package.workDir, 'finished')):
            if not os.path.exists(package.workDir):
                os.makedirs(package.workDir)

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
    def __init__(self, repo, rootDir=None):
        self.repo = repo
        self.packages = {}
        self.rootDir = rootDir
        self.fileList = []

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

        def _activate_package(package):
            _, installed = self.packages[package.sig()]
            if installed: return

            for _, dep in package.deps.iteritems():
                _activate_package(dep)          # activate deps first

            features = package.features
            if package.name in features:    # the default feature is requested
                features = [package.name]   # no need to activate the component 

            for feature in features:
                print 'activating %s' % feature
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
            _activate_package(package)

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

# }}}


