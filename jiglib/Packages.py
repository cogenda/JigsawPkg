__all__ = ['GNUPackage', 'CMakePackage', 'PythonPackage']

import os, os.path, shutil, tempfile, glob
import subprocess, re, string

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

    def _commonEnv(self, tgtDir):
        env = dict(os.environ, **self.env)
        env['PATH'] = '%s:%s' % (os.path.join(tgtDir,'bin'), env.get('PATH',''))
        env['LD_LIBRARY_PATH'] = '%s:%s' % (os.path.join(tgtDir,'lib'), env.get('LD_LIBRARY_PATH',''))
        return self._subst_vars(env, tgtDir)

    def build(self, tgtDir):
        srcDir = os.path.join(self.workDir, 'src')

        env = self._commonEnv(tgtDir)

        # autoconf
        if not os.path.exists(os.path.join(srcDir, 'configure')) and self.autoconf:
            for cmd in self.autoconf:
                ret = subprocess.call(cmd, cwd=srcDir, env=env)
                if not ret==0:
                    raise Exception('Failed to execute %s' % str(cmd))

        # configure
        cmd = self.conf_cmd
        cmd.extend(self._opt_merge_lists('conf_args'))
        cmd = self._subst_vars(cmd, tgtDir)

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
        cmd = self.make_install_cmd

        env = self._commonEnv(tgtDir)

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

    def _commonEnv(self, tgtDir):
        env = dict(os.environ, **self.env)
        env['PATH'] = '%s:%s' % (os.path.join(tgtDir,'bin'), env.get('PATH',''))
        env['LD_LIBRARY_PATH'] = '%s:%s' % (os.path.join(tgtDir,'lib'), env.get('LD_LIBRARY_PATH',''))
        return self._subst_vars(env, tgtDir)

    def build(self, tgtDir):
        srcDir = os.path.join(self.workDir, 'src')
        bldDir = os.path.join(self.workDir, 'build')
        if os.path.exists(bldDir): shutil.rmtree(bldDir)
        os.makedirs(bldDir)

        env = self._commonEnv(tgtDir)

        # configure
        cmd = self.conf_cmd
        cmd.extend(self._opt_merge_lists('conf_args'))
        cmd = self._subst_vars(cmd, tgtDir)
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
        cmd = self.make_install_cmd

        env = self._commonEnv(tgtDir)

        print cmd
        ret = subprocess.call(cmd, cwd=bldDir, env=env)
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

    def _commonEnv(self, tgtDir):
        env = dict(os.environ, **self.env)
        #env['PYTHONHOME'] = tgtDir
        #env['PYTHONDONTWRITEBYTECODE'] = '1'
        env['PATH'] = '%s:%s' % (os.path.join(tgtDir,'bin'), env.get('PATH',''))
        env['LD_LIBRARY_PATH'] = '%s:%s' % (os.path.join(tgtDir,'lib'), env.get('LD_LIBRARY_PATH',''))
        return self._subst_vars(env, tgtDir)

    def build(self, tgtDir):
        srcDir = os.path.join(self.workDir, 'src')

        env = self._commonEnv(tgtDir)

        # build
        cmd = self.build_cmd
        cmd.extend(self._opt_merge_lists('build_args'))
        cmd.append(self.build_verb)
        cmd = self._subst_vars(cmd, tgtDir)

        print cmd
        ret = subprocess.call(cmd, True, cwd=srcDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src')

        env = self._commonEnv(tgtDir)

        # install
        cmd = self.install_cmd
        cmd.extend(self._opt_merge_lists('install_args'))
        cmd.append(self.install_verb)
        cmd = self._subst_vars(cmd, tgtDir)

        print cmd
        ret = subprocess.call(cmd, True, cwd=srcDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

# }}}

