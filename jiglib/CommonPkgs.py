from JigsawPkg import *
from Packages import *
from Util import *

import os, os.path, shutil, glob, subprocess, tempfile

# {{{ CGNSLib
class CGNSLib(GNUPackage):
    name = 'cgnslib'
    version = '2.5-5'
    src_url = ['/home/public/software/science/cgnslib_2.5-5.tar.gz',
               'http://downloads.sourceforge.net/project/cgns/cgnslib_2.5/Release%205/cgnslib_2.5-5.tar.gz'
              ]
    conf_args = ['--prefix=${TGTDIR}', '--enable-64bit', '--enable-lfs']

    prereqs_src = ['sys:zlib-devel']

    optionList = ['pic']
    env_pic_append = {'CFLAGS': '-fPIC'}
# }}}

# {{{ Qt4
class Qt4(GNUPackage):
    name = 'Qt'
    featureList = ['Qt', 'Qt-redist']
    version = '4.7.2'
    src_url = ['/home/public/software/Qt/qt-everywhere-opensource-src-4.7.2.tar.gz',
               'http://get.qt.nokia.com/qt/source/qt-everywhere-opensource-src-4.7.2.tar.gz'
              ]
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
    src_url = ['/home/public/software/utils/cmake-2.8.4.tar.gz',
               'http://distfiles.macports.org/cmake/cmake-2.8.4.tar.gz',
               'http://www.cmake.org/files/v2.8/cmake-2.8.4.tar.gz',
              ]
    conf_args = ['--prefix=${TGTDIR}']

# }}}

# {{{ VTK
class VTK(CMakePackage):
    name = 'vtk'
    version = '5.4.2'
    src_url = ['/home/public/software/science/vtk-5.4.2.tar.gz',
               'http://distfiles.macports.org/vtk-devel/vtk-5.4.2.tar.gz',
               'http://www.vtk.org/files/release/v5.4/vtk-5.4.2.tar.gz',
              ]
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
                 '-DBUILD_SHARED_LIBS:BOOL=OFF',
                 '-DCMAKE_C_FLAGS:STRING=-O3 -DNDEBUG -fPIC',
                 '-DCMAKE_CXX_FLAGS:STRING=-O3 -DNDEBUG -fPIC'
                ]
    conf_cmd = ['cmake']
    prereqs_src = ['cmake']

    optionList = ['Qt']
    prereqs_Qt_append = ['Qt-redist']
    prereqs_src_Qt_append = ['Qt']
    conf_args_Qt_append = [
                 '-DVTK_USE_QVTK:BOOL=ON',
                 '-DDESIRED_QT_VERSION:STRING=4',
                 '-DQT_QMAKE_EXECUTABLE:FILEPATH=${TGTDIR}/bin/qmake',
                ]
# }}}

# {{{ Python
class Python(GNUPackage):
    name = 'python'
    featureList = ['python']
    version = '2.7.1'
    src_url = ['/home/public/software/python/Python-2.7.1.tar.bz2',
               'http://www.python.org/ftp/python/2.7.1/Python-2.7.1.tar.bz2'
              ]
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
    src_url = ['/home/public/software/python/sip-4.12.1.tar.gz',
               'http://www.riverbankcomputing.co.uk/static/Downloads/sip4/sip-4.12.1.tar.gz',
              ]
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
    src_url = ['/home/public/software/Qt/qwt-5.2.1.tar.bz2',
               '',
            ]
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
    src_url = ['ssh+git://git@hydrogen/QScintilla.git',
               'http://www.riverbankcomputing.co.uk/static/Downloads/QScintilla2/QScintilla-gpl-2.5.tar.gz',
              ]
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
    src_url = ['/home/public/software/python/PyQt-x11-gpl-4.8.3.tar.gz',
               'http://www.riverbankcomputing.co.uk/static/Downloads/PyQt4/PyQt-x11-gpl-4.8.3.tar.gz',
              ]
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
    src_url = ['/home/public/software/python/cournape-numscons-v0.12.0-0-gebb8b8a.tar.gz',
               'https://github.com/cournape/numscons/tarball/v0.12.0',
              ]
    prereqs = ['python']

# }}}

# {{{ Numpy
class Numpy(PythonPackage):
    name = 'python-numpy'
    version = '1.5.1'
    src_url = ['/home/public/software/python/numpy-1.5.1.tar.gz',
                'http://sourceforge.net/projects/numpy/files/NumPy/1.5.1/numpy-1.5.1.tar.gz'
              ]
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
    src_url = ['/home/public/software/python/scipy-0.9.0.tar.gz',
               'http://sourceforge.net/projects/scipy/files/scipy/0.9.0/scipy-0.9.0.tar.gz'
              ]
    prereqs = ['python', 'python-numpy']
    prereqs_src = ['python-numscons']
    build_args  = ['--jobs=4']
    build_cmd   = ['python', 'setupscons.py', 'scons']
    install_cmd = ['python', 'setupscons.py', 'scons']
    env = {'CPPFLAGS':  '-I/usr/include/atlas',
           'LDFLAGS':   '-L/usr/lib64/atlas'}
# }}}

# {{{ IntelCompiler
class IntelCompiler(SystemPackage):
    name = 'icc'
    version = '1.0'
    features = ['icc', 'icc-redist']

    def __init__(self, envsh, arch='intel64'):
        self.BINDIR = None
        self.LIBDIR = None
        self.LDLIBDIR = None
        self.LIBEXT = '.a'

        self.found = os.path.exists(envsh)

        tmpdir = tempfile.mkdtemp()
        str ='''#!/bin/sh
source %s %s
echo $PATH
echo $LIBRARY_PATH
echo $LD_LIBRARY_PATH
''' % (envsh, arch)

        writeFile(tmpdir, 'printenv.sh', str, 0755)
        output = subprocess.Popen(os.path.join(tmpdir,'printenv.sh'),
                                  cwd=tmpdir,
                                  stdout=subprocess.PIPE).communicate()[0]
        lines = output.split('\n')
        for i,(name,var) in enumerate([('PATH', 'BINDIR'),
                                       ('LIBRARY_PATH', 'LIBDIR'),
                                       ('LD_LIBRARY_PATH', 'LDLIBDIR')]):
            lst = lines[i].split(':')
            oldlst = os.environ.get(name, '').split(':')
            for dir in lst:
                if len(dir)==0: continue
                if not dir in oldlst:
                    self.__dict__[var] = dir
                    break

    def isAvailable(self):
        return self.found

    def _search_lib(self, dirs, f):
        for dir in dirs:
            path = os.path.join(dir,f)
            if os.path.exists(path):
                return path
        raise Exception('cannot find %s in %s' % (f, str(dirs)))

    def ifcore_libs(self):
        libs = []
        for lib in ['libifcoremt']:
            f = ''.join((lib, self.LIBEXT))
            libs.append(self._search_lib([self.LIBDIR], f))
        return libs

# }}}

# {{{ MKL Library
class MKL(SystemPackage):
    name = 'mkl'
    version = '1.0'
    features = ['mkl', 'mkl-redist']

    def __init__(self, envsh, arch=''):
        self.INCDIR = None
        self.LIBDIR = None
        self.LDLIBDIR = None
        self.LIBPREFIX = 'libmkl_'
        self.LIBSUFFIX = '_lp64'
        self.LIBEXT = '.a'

        self.found = os.path.exists(envsh)

        tmpdir = tempfile.mkdtemp()
        str ='''#!/bin/sh
source %s %s
echo $INCLUDE
echo $LIBRARY_PATH
echo $LD_LIBRARY_PATH
''' % (envsh, arch)

        writeFile(tmpdir, 'printenv.sh', str, 0755)
        output = subprocess.Popen(os.path.join(tmpdir,'printenv.sh'),
                                  cwd=tmpdir,
                                  stdout=subprocess.PIPE).communicate()[0]
        lines = output.split('\n')
        for i,(name,var) in enumerate([('INCLUDE', 'INCDIR'),
                                       ('LIBRARY_PATH', 'LIBDIR'),
                                       ('LD_LIBRARY_PATH', 'LDLIBDIR')]):
            lst = lines[i].split(':')
            oldlst = os.environ.get(name, '').split(':')
            for dir in lst:
                if len(dir)==0: continue
                if not dir in oldlst:
                    self.__dict__[var] = dir
                    break

    def isAvailable(self):
        return self.found

    def _search_lib(self, dirs, f):
        for dir in dirs:
            path = os.path.join(dir,f)
            if os.path.exists(path):
                return path
        raise Exception('cannot find %s in %s' % (f, str(dirs)))

    def basic_libs(self):
        libs = []
        for lib in ['intel', 'blas95', 'lapack95', 'blacs']:
            f = ''.join((self.LIBPREFIX, lib, self.LIBSUFFIX, self.LIBEXT))
            libs.append(self._search_lib([self.LIBDIR], f))
        for lib in ['core', 'sequential']:
            f = ''.join((self.LIBPREFIX, lib, self.LIBEXT))
            libs.append(self._search_lib([self.LIBDIR], f))
        return libs

    def scalapack_libs(self):
        libs = []
        for lib in ['scalapack']:
            f = ''.join((self.LIBPREFIX, lib, self.LIBSUFFIX, self.LIBEXT))
            libs.append(self._search_lib([self.LIBDIR], f))
        return libs
# }}}

# {{{ Petsc
class Petsc(GNUPackage):
    name = 'petsc'
    version = '3.1-p8'
    src_url = ['/home/public/software/petsc/petsc-lite-3.1-p8.tar.gz',
               'http://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-lite-3.1-p8.tar.gz'
              ]
    conf_cmd  = ['python', 'configure']
    conf_args_common = [
                '--with-debugging=0',
                '--with-shared=0',
                '--with-x=0',
                '--with-pic=1'
                ]
    conf_args_solver_append = [
                '--download-superlu=1',
                '--download-hypre=1',
                ]
    conf_args_solver_mpi_append = [
                '--download-mumps=1',
                '--download-parmetis=1',
                '--download-superlu_dist=1',
                ]

    # icc
    conf_args_icc_append = ['--with-vendor-compilers=intel']
    prereqs_src_icc_append = ['icc']

    # {{{ Linear Algebra libraries

    # download and compile linear algebra lib
    conf_args_netlib_nompi_append = ['--download-f-blas-lapack=1']
    conf_args_netlib_append = [
                '--download-f-blas-lapack=1',
                '--download-blacs=1',
                '--download-scalapack=1',
                ]
    # TODO epel Atlas library

    # MKL
    conf_args_mkl_append = [
                '--with-blacs-include=${MKL_INC_DIR}',
                '--with-blas-include=${MKL_INC_DIR}',
                '--with-scalapack-include=${MKL_INC_DIR}',
                '--with-blacs-lib=[${MKL_LIBS}]',
                '--with-blas-lapack-lib=[${MKL_LIBS}]',
                '--with-scalapack-lib=[${MKL_SCALAPACK_LIBS}]',
                ]
    prereqs_src_mkl_append = ['mkl']

    # }}}

    # {{{ MPI library
    # no MPI support
    conf_args_nompi_append = ['--with-mpi=0',]

    # download and compile MPICH2
    conf_args_mpich2_append =  ['--download-mpich=1',
                                '--download-mpich-device=ch3:nemesis']

    # epel MPICH2
    conf_args_mpich2_epel_append   = ['--with-mpi-dir=/usr']
    prereqs_src_mpich2_epel_append = ['sys:epel-release', 'sys:mpich2-devel']

    # }}}

    dest_path_fixes = ['conf/*']

    # {{{ __init__()
    def __init__(self, *args, **kwargs):
        options = kwargs.get('options', ['solver'])
        if not ( 'mpich2_epel'  in options or
                 'mpich2'       in options or
                 'nompi'        in options ):
            options.append('mpich2') # default to download mpich2

        if not ( 'mkl'    in options or
                 'netlib' in options ):
            if 'nompi' in  options:
                options.append('netlib_nompi') # default linear algebra lib w/o mpi
            else:
                options.append('netlib') # default linear algebra lib

        if not 'nompi' in options:
            options.append('solver_mpi')

        kwargs['options'] = options

        if 'icc' in options:
            if 'mkl' in options:
                self.arch = 'linux-icc'
            else:
                self.arch = 'linux-icc-nomkl'
        else:
            self.arch = 'linux-gcc'
        
        self.conf_args = self.conf_args_common
        self.conf_args.extend(
            [ '--prefix=%s/petsc/%s'   %  ('${TGTDIR}', self.arch) ])

        super(Petsc, self).__init__(*args, **kwargs)
    # }}}

    # {{{ _commonEnv()
    def _commonEnv(self, vars):
        env = super(Petsc, self)._commonEnv(vars)

        paths, ld_paths = [], []
        if 'icc' in self.options:
            icc = self.deps['icc']
            paths.append(icc.BINDIR)
            ld_paths.append(icc.LDLIBDIR)
        if 'mkl' in self.options:
            mkl = self.deps['mkl']
            ld_paths.append(mkl.LDLIBDIR)

        paths.extend(env.get('PATH','').split(':'))
        ld_paths.extend(env.get('LD_LIBRARY_PATH','').split(':'))
        env['PATH']             = ':'.join(paths)
        env['LD_LIBRARY_PATH']  = ':'.join(ld_paths)

        env['PETSC_DIR']        = os.path.join(self.workDir, 'src')
        env['PETSC_ARCH']       = self.arch

        return env
    # }}}

    # {{{ _subst_vars
    def _subst_vars(self, lst_or_dict, vars):
        if 'icc' in self.options:
            icc = self.deps['icc']
            vars['ICC_BIN_DIR'] = icc.BINDIR
            vars['ICC_LIB_DIR'] = icc.LIBDIR
        if 'mkl' in self.options:
            mkl = self.deps['mkl']
            vars['MKL_INC_DIR'] = mkl.INCDIR
            vars['MKL_LIB_DIR'] = mkl.LIBDIR
            vars['MKL_LIBS']    = ','.join(mkl.basic_libs())

            libs = list(mkl.scalapack_libs())
            libs.extend(icc.ifcore_libs())
            vars['MKL_SCALAPACK_LIBS'] = ','.join(libs)

        return super(Petsc, self)._subst_vars(lst_or_dict, vars)
    # }}}

# }}}


