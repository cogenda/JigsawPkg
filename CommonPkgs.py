from jiglib.JigsawPkg import *
from jiglib.Packages import *

import os, os.path, shutil, glob, subprocess

# {{{ CGNSLib
class CGNSLib(GNUPackage):
    name = 'cgnslib'
    version = '2.5-5'
    src_url = '/home/public/software/science/cgnslib_2.5-5.tar.gz'
    conf_args = ['--prefix=${TGTDIR}', '--enable-64bit', '--enable-lfs']
# }}}

# {{{ Qt4
class Qt4(GNUPackage):
    name = 'Qt'
    featureList = ['Qt', 'Qt-redist']
    version = '4.7.2'
    src_url = '/home/public/software/Qt/qt-everywhere-opensource-src-4.7.2.tar.gz'
    conf_args = ['-opensource', '-confirm-license',
                 '-prefix',     '${TGTDIR}',
                 '-datadir',    '${TGTDIR}/share/qt4',
                 '-plugindir',  '${TGTDIR}/lib/qt4/plugins',
                 '-importdir',  '${TGTDIR}/lib/qt4/imports',
                 '-translationdir',  '${TGTDIR}/share/qt4/translations',
                 '-no-rpath', '-fast',
                 '-no-ssse3', '-no-sse4.1', '-no-sse4.2',
                 '-no-openvg', '-no-egl',
                 '-nomake', 'examples', '-nomake', 'demos', '-nomake', 'docs',
                 '-plugin-sql-sqlite',
                 '-system-zlib', '-qt-gif',
                 '-no-declarative', '-no-declarative-debug',
                 '-no-script', '-no-scripttools',
                 '-no-phonon', '-no-phonon-backend',
                 '-no-multimedia', '-no-audio-backend',
                 '-no-qt3support', '-no-dbus',
                 '-no-svg', '-no-webkit']
    dest_path_fixes = ['lib/pkgconfig/*.pc', 'lib/*.prl', 'lib/*.la']

    def install(self, tgtDir, obj):
        if obj=='Qt-redist':
            patterns = [('src/lib', 'lib', '*.so*'),
                        ('src/plugins', 'lib/qt4/plugins', '*'),
                        ('src/translations', 'share/qt4/translations', '*')
                        ]
            for src,dst,pat in patterns:
                srcDir = os.path.join(self.workDir, src)
                dstDir = os.path.join(tgtDir, dst)
                for path in glob.glob('%s/%s' % (srcDir,pat)):
                    tgtPath = os.path.join(dstDir, os.path.relpath(path, srcDir))
                    copyX(path, tgtPath)
        else:
            super(Qt4, self).install(tgtDir, obj)

# }}}

# {{{ CMake
class CMake(GNUPackage):
    name = 'cmake'
    version = '2.8.4'
    src_url = '/home/public/software/utils/cmake-2.8.4.tar.gz'
    conf_args = ['--prefix=${TGTDIR}']

# }}}

# {{{ VTK
class VTK(CMakePackage):
    name = 'vtk'
    version = '5.4.2'
    src_url = '/home/public/software/science/vtk-5.4.2.tar.gz'
    conf_args = [
                 '-DCMAKE_BUILD_TYPE:STRING=Release',
                 '-DCMAKE_INSTALL_PREFIX:PATH=${TGTDIR}',
                 '-DCMAKE_INCLUDE_PATH:PATH=${TGTDIR}/include',
                 '-DCMAKE_LIBRARY_PATH:PATH=${TGTDIR}/lib',
                 '-DBUILD_DOCUMENTATION:BOOL=OFF',
                 '-DBUILD_EXAMPLES:BOOL=OFF',
                 '-DBUILD_TESTING:BOOL=OFF',
                 '-DVTK_DEBUG_LEAKS:BOOL=OFF',
                 '-DVTK_USE_RPATH:BOOL=OFF',
                 '-DVTK_USE_X:BOOL=OFF',
                 '-DVTK_USE_GUISUPPORT:BOOL=ON',
                 '-DVTK_USE_INFOVIS:BOOL=ON',
                 '-DVTK_USE_PARALLEL:BOOL=OFF',
                 '-DVTK_USE_RENDERING:BOOL=ON',
                 '-DVTK_USE_VIEWS:BOOL=ON',
                 '-DVTK_USE_GL2PS:BOOL=OFF',
                 '-DVTK_USE_N_WAY_ARRAYS:BOOL=ON',
                 '-DVTK_USE_TK:BOOL=OFF',
                 '-DVTK_WRAP_JAVA:BOOL=OFF',
                 '-DVTK_WRAP_PYTHON:BOOL=OFF',
                 '-DVTK_WRAP_TCL:BOOL=OFF',
                 '-DVTK_USE_QVTK:BOOL=ON',
                 '-DDESIRED_QT_VERSION:STRING=4',
                 '-DQT_QMAKE_EXECUTABLE:FILEPATH=${TGTDIR}/bin/qmake',
                 '-DBUILD_SHARED_LIBS:BOOL=OFF',
                 '-DCMAKE_C_FLAGS:STRING=-O3 -DNDEBUG -fPIC',
                 '-DCMAKE_CXX_FLAGS:STRING=-O3 -DNDEBUG -fPIC'
                ]
    conf_cmd = ['cmake']
    prereqs = ['Qt-redist']
    prereqs_src = ['Qt', 'cmake']

# }}}

# {{{ Python
class Python(GNUPackage):
    name = 'python'
    featureList = ['python']
    version = '2.7.1'
    src_url = '/home/public/software/python/Python-2.7.1.tar.bz2'
    conf_args = ['--prefix=${TGTDIR}']
    optionList = ['shared']
    conf_args_shared_append = ['--enable-shared']

    def installWorld(self, wldDir, objDir, obj):
        lst = super(Python, self).installWorld(wldDir, objDir, obj)

        vername = '.'.join(self.version.split('.')[:2])

        for binname in ['python', 'python%s'%vername, 'python-config', 'python%s-config'%vername]:
            path = os.path.join(objDir, 'bin', binname)
            tgtPath = os.path.join(wldDir, 'bin', binname)
            os.unlink(tgtPath)
            script='''#!/bin/sh
export PYTHONHOME=%s
%s $*
''' % (wldDir, path)
            writeFile(wldDir, os.path.join('bin',binname), script, mode=0755)

        return lst

# }}}

# {{{ SIP
class SIP(GNUPackage):
    name = 'python-sip'
    version = '4.12.1'
    src_url = '/home/public/software/python/sip-4.12.1.tar.gz'
    env = {'PYTHONDONTWRITEBYTECODE':'1'}
    autoconf = None
    conf_cmd  = ['python', 'configure.py']
    conf_args = [
                 '--bindir=${TGTDIR}/bin',
                 '--destdir=${TGTDIR}/lib/python2.7/site-packages',
                 '--incdir=${TGTDIR}/include',
                ]
    prereqs = ['python']
    dest_path_fixes = ['lib/python2.7/site-packages/sipconfig.py']
# }}}

# {{{ Qwt
class Qwt(GNUPackage):
    name = 'Qwt'
    version = '5.2.1'
    src_url = '/home/public/software/Qt/qwt-5.2.1.tar.bz2'
    prereqs     = ['Qt-redist']
    prereqs_src = ['Qt']
    autoconf  = None
    conf_cmd  = ['qmake']

    def build(self, tgtDir):
        srcDir = os.path.join(self.workDir, 'src')

        fConfig = os.path.join(srcDir, 'qwtconfig.pri')
        subTxtFile(fConfig, r'INSTALLBASE\s*=.*', 'INSTALLBASE = %s'%tgtDir, mode='re')
        subTxtFile(fConfig, r'CONFIG\s*\+=\s*debug', 'CONFIG += release', mode='re')
        subTxtFile(fConfig, r'CONFIG\s*\+=\s*QwtDll', '#CONFIG += QwtDll', mode='re')
        subTxtFile(fConfig, r'CONFIG\s*\+=\s*QwtDesigner', '#CONFIG += QwtDesigner', mode='re')

        fConfig = os.path.join(srcDir, 'designer', 'designer.pro')
        subTxtFile(fConfig, '$$[QT_INSTALL_PLUGINS]', 
                   os.path.join(tgtDir, 'lib', 'qt4', 'plugins'))

        super(Qwt, self).build(tgtDir)
# }}}

# {{{ QScintilla
class QScintilla(GNUPackage):
    name = 'QScintilla'
    version = '2.4-dev'
    src_url = 'ssh+git://git@hydrogen/QScintilla.git'
    prereqs     = ['Qt-redist']
    prereqs_src = ['Qt']

    def build(self, tgtDir):
        srcDir = os.path.join(self.workDir, 'src', 'Qt4')
        vars = {'TGTDIR': tgtDir}

        env = self._commonEnv(vars)

        def _fix_pro(name, val):
            subTxtFile(os.path.join(srcDir,'qscintilla.pro'),
                       '$$[%s]' % name, val)
        _fix_pro('QT_INSTALL_LIBS',         os.path.join(tgtDir, 'lib'))
        _fix_pro('QT_INSTALL_HEADERS',      os.path.join(tgtDir, 'include'))
        _fix_pro('QT_INSTALL_TRANSLATIONS', os.path.join(tgtDir, 'share/qt4/translations'))
        _fix_pro('QT_INSTALL_DATA',         os.path.join(tgtDir, 'share/qt4'))

        # configure
        cmd = ['qmake']
        print cmd
        ret = subprocess.call(cmd, True, cwd=srcDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

        cmd = self.make_cmd
        ret = subprocess.call(cmd, cwd=srcDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src', 'Qt4')
        vars = {'TGTDIR': tgtDir}
        env = self._commonEnv(vars)

        cmd = self.make_install_cmd

        print cmd
        ret = subprocess.call(cmd, cwd=srcDir, env=env)
        if not ret==0:
            raise Exception('Failed to execute %s' % str(cmd))

# }}}

# {{{ PyQt
class PyQt(GNUPackage):
    name = 'python-pyqt'
    version = '4.8.3'
    src_url = '/home/public/software/python/PyQt-x11-gpl-4.8.3.tar.gz'
    autoconf = None
    env = {'PYTHONDONTWRITEBYTECODE':'1'}
    conf_cmd  = ['python', 'configure.py']
    conf_args = ['--confirm-license', '--no-designer-plugin', '--no-sip-files',
                 '--bindir=${TGTDIR}/bin',
                 '--destdir=${TGTDIR}/lib/python2.7/site-packages',
                ]
    prereqs = ['python-sip', 'Qt-redist']
    prereqs_src = ['Qt']

# }}}

# {{{ numscons
class numscons(PythonPackage):
    name = 'python-numscons'
    version = '0.12.0'
    src_url = '/home/public/software/python/cournape-numscons-v0.12.0-0-gebb8b8a.tar.gz'
    prereqs = ['python']

# }}}

# {{{ Numpy
class Numpy(PythonPackage):
    name = 'python-numpy'
    version = '1.5.1'
    src_url = '/home/public/software/python/numpy-1.5.1.tar.gz'
    prereqs = ['python']
    prereqs_src = ['python-numscons']
    build_args  = ['--jobs=4']
    build_cmd   = ['python', 'setupscons.py', 'scons']
    install_cmd = ['python', 'setupscons.py', 'scons']
    env = {'CPPFLAGS':  '-I/usr/include/atlas',
           'LDFLAGS':   '-L/usr/lib64/atlas'}
# }}}

# {{{ Scipy
class Scipy(PythonPackage):
    name = 'python-scipy'
    version = '0.9.0'
    src_url = '/home/public/software/python/scipy-0.9.0.tar.gz'
    prereqs = ['python', 'python-numpy']
    prereqs_src = ['python-numscons']
    build_args  = ['--jobs=4']
    build_cmd   = ['python', 'setupscons.py', 'scons']
    install_cmd = ['python', 'setupscons.py', 'scons']
    env = {'CPPFLAGS':  '-I/usr/include/atlas',
           'LDFLAGS':   '-L/usr/lib64/atlas'}
# }}}

ICC_DIR = '/opt/intel/Compiler/11.1/038'
ICC_BIN_DIR = os.path.join(ICC_DIR, 'bin', 'intel64')
ICC_LIB_DIR = os.path.join(ICC_DIR, 'lib', 'intel64')
MKL_DIR = '/opt/intel/mkl/10.2.0.013'
MKL_INC_DIR = os.path.join(MKL_DIR, 'include')
MKL_LIB_DIR = os.path.join(MKL_DIR, 'lib', 'em64t')

MKL_LIB_PREFIX = 'libmkl_'
LIB_EXT = '.a'
MKL_LIB_SUFFIX = '_lp64'


# {{{ Petsc
class Petsc(GNUPackage):
    name = 'petsc'
    version = '3.1-p8'
    src_url = '/home/public/software/petsc/petsc-lite-3.1-p8.tar.gz'
    conf_cmd  = ['python', 'configure']
    conf_args_common = [
                '--with-mpi-dir=/usr',
                '--download-parmetis=1',
                '--download-mumps=1',
                '--download-superlu=1',
                '--download-superlu_dist=1',
                '--download-hypre=1',
                '--with-debugging=0',
                '--with-shared=0',
                '--with-x=0',
                '--with-pic=1']

    # icc
    conf_args_icc_append = ['--with-vendor-compilers=intel']

    # default
    conf_args_default_append = [
                '--download-f-blas-lapack=1',
                '--download-blacs=1',
                '--download-scalapack=1',
                ]
    # MKL
    MKL_LIBS= [ '%s/%s%s%s%s' % (MKL_LIB_DIR, MKL_LIB_PREFIX, lib, MKL_LIB_SUFFIX, LIB_EXT)
                    for lib in ['intel', 'blas95', 'lapack95', 'blacs'] ]
    MKL_LIBS.extend( ['%s/%s%s%s' % (MKL_LIB_DIR, MKL_LIB_PREFIX, lib, LIB_EXT)
                    for lib in ['core', 'sequential'] ] )

    MKL_SCALAPACK_LIBS = [
                '%s/%s%s%s%s' % (MKL_LIB_DIR, MKL_LIB_PREFIX, lib, MKL_LIB_SUFFIX, LIB_EXT)
                    for lib in ['scalapack'] ]
    MKL_SCALAPACK_LIBS.append( '%s/libifcoremt%s' % ( ICC_LIB_DIR, LIB_EXT ) )

    conf_args_mkl_append = [
                '--with-blacs-include=%s'       % MKL_INC_DIR,
                '--with-blas-include=%s'        % MKL_INC_DIR,
                '--with-scalapack-include=%s'   % MKL_INC_DIR
                ]
    conf_args_mkl_append.extend( [
                '--with-blacs-lib=[%s]'           % ','.join(MKL_LIBS),
                '--with-blas-lapack-lib=[%s]'     % ','.join(MKL_LIBS),
                '--with-scalapack-lib=[%s]'       % ','.join(MKL_SCALAPACK_LIBS),
                ] )

    prereqs_src = ['python']
    dest_path_fixes = ['conf/*']

    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('options'):
            kwargs['options'] = ['default']

        options = kwargs['options']
        if 'icc' in options:
            if 'mkl' in options:
                self.arch = 'linux-icc'
            else:
                self.arch = 'linux-icc-nomkl'
        else:
            self.arch = 'linux-gcc'
        
        self.conf_args = list(self.conf_args_common)
        self.conf_args.extend([
            '--prefix=%s/petsc/%s'   %  ('${TGTDIR}', self.arch)
            ])

        super(Petsc, self).__init__(*args, **kwargs)

    def _commonEnv(self, vars):
        env = super(Petsc, self)._commonEnv(vars)

        env['PATH']             = '%s:%s' % (ICC_BIN_DIR, env.get('PATH',''))
        env['LD_LIBRARY_PATH']  = '%s:%s' % (':'.join([ICC_LIB_DIR, MKL_LIB_DIR]),
                                             env.get('LD_LIBRARY_PATH',''))

        env['PETSC_DIR']        = os.path.join(self.workDir, 'src')
        env['PETSC_ARCH']       = self.arch

        return env

# }}}


