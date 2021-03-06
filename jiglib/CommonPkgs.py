__all__=[]

from JigsawPkg import *
from Packages import *
from Util import *
from Logger import *

import os, os.path, shutil, glob, tempfile
try:
    from hashlib import sha1
except:
    from sha import new as sha1


# {{{ CGNSLib
class CGNSLib(GNUPackage):
    name = 'cgnslib'
    version = '2.5-5'
    src_url = ['/home/public/software/science/cgnslib_2.5-5.tar.gz',
               'http://downloads.sourceforge.net/project/cgns/cgnslib_2.5/Release%205/cgnslib_2.5-5.tar.gz'
              ]
    conf_args = ['--prefix=${TGTDIR}', '--enable-64bit', '--enable-lfs']

    prereqs_src = ['sys:zlib-devel']

    optionList = ['pic', '32bit']
    env_pic_append = {'CFLAGS': '-fPIC'}

    conf_args_32bit_delete = ['--enable-64bit']
    env_32bit_append = {'CFLAGS': '-m32'}

__all__.append('CGNSLib')
# }}}

# {{{ Qt4
class Qt4(GNUPackage):
    name = 'Qt'
    featureList = ['Qt', 'Qt-redist']
    version = '4.7.4'
    src_url = ['/home/public/software/Qt/qt-everywhere-opensource-src-4.7.4.tar.gz',
               'http://get.qt.nokia.com/qt/source/qt-everywhere-opensource-src-4.7.4.tar.gz'
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
                 '-no-phonon', '-no-phonon-backend',
                 '-no-multimedia', '-no-audio-backend',
                 '-no-qt3support', '-no-dbus',
                 ]
    optionList = ['32bit', 'qt3']
    conf_args_32bit_append = ['-platform', 'linux-g++-32']
    conf_args_qt3_delete = ['-no-qt3support']

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

__all__.append('Qt4')
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

    optionList = ['32bit']
    env_32bit_append = {'CFLAGS': '-m32', 'CXXFLAGS': '-m32'}

__all__.append('CMake')
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
                 '-DCMAKE_BUILD_TYPE:STRING=RELEASE',
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
    prereqs_src = ['cmake', 'sys:libX11-devel', 'sys:mesa-libGL-devel', 'sys:libXt-devel']

    optionList = ['Qt', '32bit']
    prereqs_Qt_append = ['Qt-redist']
    prereqs_src_Qt_append = ['Qt']
    conf_args_Qt_append = [
                 '-DVTK_USE_QVTK:BOOL=ON',
                 '-DDESIRED_QT_VERSION:STRING=4',
                 '-DQT_QMAKE_EXECUTABLE:FILEPATH=${TGTDIR}/bin/qmake',
                ]

    conf_args_32bit_append = [
                 '-DCMAKE_C_FLAGS:STRING=-m32 -O3 -DNDEBUG -fPIC',
                 '-DCMAKE_CXX_FLAGS:STRING=-m32 -O3 -DNDEBUG -fPIC'
                ]

__all__.append('VTK')
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
    optionList = ['shared', '32bit']
    conf_args_shared_append = ['--enable-shared']

    env_32bit_append = {'CFLAGS': '-m32', 'LDFLAGS': '-m32'}

    # patches
    patches = [
    # {{{ python-config missed -L
r'''--- a/Misc/python-config.in  (revision 82663)
+++ b/Misc/python-config.in  (working copy)
@@ -49,8 +49,21 @@ for opt in opt_flags:
         # add the prefix/lib/pythonX.Y/config dir, but only if there is no
         # shared library in prefix/lib/.
         if opt == '--ldflags':
+            # Provide the location where the Python library is installed.
+            # We always provide it, because Python may have been installed
+            # at a non-standard location.
             if not getvar('Py_ENABLE_SHARED'):
-                libs.insert(0, '-L' + getvar('LIBPL'))
+                # There is no shared library in prefix/lib.  The static
+                # library is in prefix/lib/pythonX.Y/config.
+                #
+                # Note that we cannot use getvar('LIBPL') like we used to,
+                # because it provides the location at build time, which might
+                # be different from the actual location at runtime.
+                libdir = sysconfig.get_python_lib(standard_lib=True) + '/config'
+            else:
+                # The Python shared library is installed in prefix/lib.
+                libdir = sysconfig.PREFIX + '/lib'
+            libs.insert(0, '-L' + libdir)
             libs.extend(getvar('LINKFORSHARED').split())
         print ' '.join(libs)
''',
    # }}}
    # {{{ missing RTLD def
r'''--- a/Lib/plat-linux2/DLFCN.py    2004-07-18 14:16:08.000000000 +0800
+++ b/Lib/plat-linux2/DLFCN.py    2011-04-26 13:26:54.000000000 +0800
@@ -78,6 +78,7 @@
 RTLD_NOW = 0x00002
 RTLD_BINDING_MASK = 0x3
 RTLD_NOLOAD = 0x00004
+RTLD_DEEPBIND = 0x00008
 RTLD_GLOBAL = 0x00100
 RTLD_LOCAL = 0
 RTLD_NODELETE = 0x01000
''',
    # }}}
    ]

    # {{{ installWorld()
    def installWorld(self, wldDir, objDir, obj):
        lst = super(Python, self).installWorld(wldDir, objDir, obj)

        vername = '.'.join(self.version.split('.')[:2])

        for binname in ['python', 'python%s'%vername, 'python-config', 'python%s-config'%vername]:
            tgtPath = os.path.join(wldDir, 'bin', binname)
            path = os.path.join(objDir, 'bin', binname)
            if len(os.path.commonprefix([tgtPath, path]))>0:
                path = os.path.relpath(os.path.join(objDir, 'bin', binname),
                                       os.path.join(wldDir, 'bin'))
                path = '$DIR/'+path
            os.unlink(tgtPath)
            script='''#!/bin/bash
DIR=$(dirname ${BASH_SOURCE[0]})
source $DIR/setenv.sh
export PYTHONHOME=$BASEDIR

args=()
for arg in "$@"
do
    args[$i]="$arg"
    ((++i))
done
exec %s "${args[@]}"
''' % path
            writeFile(wldDir, os.path.join('bin',binname), script, mode=0755)

        return lst
    # }}}

__all__.append('Python')
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

    optionList = ['32bit']
    conf_args_32bit_append = ['--platform=linux-g++-32']

__all__.append('SIP')
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

__all__.append('Qwt')
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
        cmd_n_log(['qmake'], cwd=srcDir, env=env, logger=self.logger)

        # make
        cmd_n_log(self.make_cmd, cwd=srcDir, env=env, logger=self.logger)

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src', 'Qt4')
        vars = {'TGTDIR': tgtDir}
        env = self._commonEnv(vars)

        cmd_n_log(self.make_install_cmd, cwd=srcDir, env=env, logger=self.logger)

__all__.append('QScintilla')
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

    optionList = ['32bit']
    conf_args_32bit_append = ['LFLAGS+=-m32']

__all__.append('PyQt')
# }}}

# {{{ numscons
class numscons(PythonPackage):
    name = 'python-numscons'
    version = '0.12.0'
    src_url = ['/home/public/software/python/cournape-numscons-v0.12.0-0-gebb8b8a.tar.gz',
               'https://github.com/cournape/numscons/tarball/v0.12.0',
              ]
    prereqs = ['python']

__all__.append('numscons')
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
    build_cmd   = ['python', 'setupscons.py', 'scons', '--fcompiler=gfortran']
    install_cmd = ['python', 'setupscons.py', 'scons', '--fcompiler=gfortran']
    env = {'CPPFLAGS':  '-I/usr/include/atlas',
           'LDFLAGS':   '-L/usr/lib64/atlas'}

__all__.append('Numpy')
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
    build_cmd   = ['python', 'setupscons.py', 'scons', '--fcompiler=gfortran']
    install_cmd = ['python', 'setupscons.py', 'scons', '--fcompiler=gfortran']
    env = {'CPPFLAGS':  '-I/usr/include/atlas',
           'LDFLAGS':   '-L/usr/lib64/atlas'}

__all__.append('Scipy')
# }}}

# {{{ matplotlib
class Matplotlib(PythonPackage):
    name = 'python-matplotlib'
    version = '1.0.0'
    src_url = ['/home/public/software/python/matplotlib-1.0.0.tar.gz',
               'http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.0/matplotlib-1.0.0.tar.gz',
              ]
    prereqs = ['python', 'python-numpy']
    prereqs_src = ['sys:libpng-devel', 'sys:freetype-devel']
    env = {'LDFLAGS': '-L${TGTDIR}/lib'}

__all__.append('Matplotlib')
# }}}

# {{{ pyparsing
class PyParsing(PythonPackage):
    name = 'python-pyparsing'
    version = '1.5.5'
    src_url = ['/home/public/software/python/pyparsing-1.5.5.tar.gz',
               'http://sourceforge.net/projects/pyparsing/files/pyparsing/pyparsing-1.5.5/pyparsing-1.5.5.tar.gz',
              ]
    prereqs = ['python']

__all__.append('PyParsing')
# }}}

# {{{ setuptools
class SetupTools(Package):
    name = 'python-setuptools'
    version = '0.6c11'
    src_url = ['/home/public/software/python/setuptools-0.6c11-py2.7.egg',
               'http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg',
              ]
    prereqs = ['python']

    def fetch(self):
        if self.src_url==None:
            return

        src_file, _ = self._getFile(self.src_url)
        shutil.copy(src_file, self.workDir)

    def install(self, tgtDir, obj):
        vars = {'TGTDIR': tgtDir}
        env = self._commonEnv(vars)

        ret = cmd_n_log(['sh', 'setuptools-0.6c11-py2.7.egg'],
                        cwd=self.workDir, env=env,
                        logger=self.logger)


__all__.append('SetupTools')
# }}}

# {{{ openopt
class OpenOpt(PythonPackage):
    name = 'python-OpenOpt'
    version = '0.34'
    src_url = ['/home/public/software/python/OpenOpt.34.zip',
               'http://openopt.org/images/3/33/OpenOpt.zip',
              ]
    prereqs = ['python', 'python-numpy', 'python-setuptools']
    build_cmd = None

    def installWorld(self, wldDir, objDir, obj):
        fileList = super(OpenOpt, self).installWorld(wldDir, objDir, obj)

        fnPth = os.path.join(wldDir, 'lib', 'python2.7', 'site-packages', 'easy-install.pth')
        fin = open(fnPth, 'r')
        lines = fin.readlines()
        fin.close()
        if os.path.islink(fnPth):
            os.unlink(fnPth)

        fout = open(fnPth, 'w')
        for l in lines[:-1]:
            fout.write(l)
        fout.write('./openopt-0.34-py2.7.egg\n')
        fout.write(lines[-1])
        fout.close()

        return fileList

__all__.append('OpenOpt')
# }}}

# {{{ IntelCompiler
class IntelCompiler(SystemPackage):
    name = 'icc'
    version = '1.0'
    featureList = ['icc', 'icc-redist']

    def __init__(self, envsh, arch='intel64', **kwargs):
        self.BINDIR = None
        self.LIBDIR = None
        self.LDLIBDIR = None
        self.LIBEXT = '.a'
        self._setDefault('logger', std_logger)

        self.found = os.path.exists(envsh)

        tmpdir = tempfile.mkdtemp()
        str ='''#!/bin/bash
source %s %s
echo $PATH
echo $LIBRARY_PATH
echo $LD_LIBRARY_PATH
''' % (envsh, arch)

        writeFile(tmpdir, 'printenv.sh', str, 0755)
        lines = cmd_n_log(os.path.join(tmpdir,'printenv.sh'),
                           cwd=tmpdir, logger=self.logger)
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

        super(IntelCompiler, self).__init__(**kwargs)

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

__all__.append('IntelCompiler')
# }}}

# {{{ MKL Library
class MKL(Package):
    name = 'mkl'
    version = '1.0'
    featureList = ['mkl', 'mkl-redist']

    def __init__(self, envsh, arch='intel64', **kwargs):
        self.INCDIR = None
        self.LIBDIR = None
        self.LDLIBDIR = None
        self.LIBPREFIX = kwargs.get('libPrefix', 'libmkl')
        self.arch=arch
        if arch=='intel64':
            self.INTERFACE = kwargs.get('interface', 'lp64')
        else:
            self.INTERFACE = ''
        self.THREAD    = kwargs.get('thread', 'sequential')
        self.MPI       = kwargs.get('mpi', 'intelmpi')
        self.SCALAPACK = kwargs.get('scalapack', True)
        self.singleLib = kwargs.get('singleLib', True)
        self.LIBEXT = 'a'
        self._setDefault('logger', std_logger)

        self.fileSingleLib = 'libmkl.a'

        if not os.path.exists(envsh):
            raise Exception

        tmpdir = tempfile.mkdtemp()
        str ='''#!/bin/bash
source %s
echo $INCLUDE
echo $LIBRARY_PATH
echo $LD_LIBRARY_PATH
''' % envsh

        writeFile(tmpdir, 'printenv.sh', str, 0755)
        lines = cmd_n_log(os.path.join(tmpdir,'printenv.sh'),
                           cwd=tmpdir, logger=self.logger)
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

        super(MKL, self).__init__(**kwargs)

    def sig(self):
        lst = [self.name, self.version, self.INTERFACE, self.THREAD, self.MPI,
               str(self.SCALAPACK)]
        return sha1(','.join(lst)).hexdigest()[0:7]

    def _search_lib(self, dirs, f):
        for dir in dirs:
            path = os.path.join(dir,f)
            if os.path.exists(path):
                return path
        raise Exception('cannot find %s in %s' % (f, str(dirs)))


    def libFileList(self):
        vars = {'LIBPREFIX': self.LIBPREFIX,
                'INTERFACE': self.INTERFACE,
                'THREAD':    self.THREAD,
                'MPI':       self.MPI,
                'LIBEXT':    self.LIBEXT}

        libs = []
        if self.arch=='intel64':
            if self.SCALAPACK:
                libs.append('${LIBPREFIX}_scalapack_${INTERFACE}.${LIBEXT}')
            libs.extend([
                '${LIBPREFIX}_solver_${INTERFACE}_${THREAD}.${LIBEXT}',
                '${LIBPREFIX}_intel_${INTERFACE}.${LIBEXT}',
                '${LIBPREFIX}_${THREAD}.${LIBEXT}',
                '${LIBPREFIX}_core.${LIBEXT}',
                '${LIBPREFIX}_blacs_${MPI}_${INTERFACE}.${LIBEXT}',
                   ])
        else:
            if self.SCALAPACK:
                libs.append('${LIBPREFIX}_scalapack_core.${LIBEXT}')
            libs.extend([
                '${LIBPREFIX}_solver_${THREAD}.${LIBEXT}',
                '${LIBPREFIX}_intel.${LIBEXT}',
                '${LIBPREFIX}_${THREAD}.${LIBEXT}',
                '${LIBPREFIX}_core.${LIBEXT}',
                '${LIBPREFIX}_blacs_${MPI}.${LIBEXT}',
                   ])

        libs = substVars(libs, vars)

        lst = []
        for f in libs:
            lst.append(self._search_lib([self.LIBDIR], f))

        return lst

    def install(self, tgtDir, obj):
        if not self.singleLib:
            return
        
        tflib = os.path.join(tgtDir, 'lib', 'tmp.%s'%self.fileSingleLib)
        flib = os.path.join(tgtDir, 'lib', self.fileSingleLib)
        if os.path.exists(flib): return [flib]   # already installed
        if os.path.exists(tflib): os.unlink(tflib)

        libs = self.libFileList()

        tmpdir = tempfile.mkdtemp()
        self.logger.write('Combining libraries %s in %s' % (str(libs), tmpdir))
        for lib in libs:
            cmd_n_log(['ar', 'x', lib], cwd=tmpdir, logger=self.logger)

        objs = os.listdir(tmpdir)

        while len(objs)>0:
            tlst = objs[:5000]
            cmd = ['ar', 'rcs', tflib]
            cmd.extend(tlst)
            cmd_n_log(cmd, cwd=tmpdir, logger=self.logger)

            objs = objs[5000:]

        shutil.rmtree(tmpdir)

        os.rename(tflib, flib)
        self.logger.write('Combined library saved as %s' % flib)

__all__.append('MKL')
# }}}

# {{{ MPICH2
class MPICH2(GNUPackage):
    name = 'mpich2'
    featureList = ['mpich2', 'mpich2-redist']
    version='1.4.1-p1-2'
    src_url = ['/home/public/software/cluster/mpich2-1.4.1p1.tar.gz',
               'http://www.mcs.anl.gov/research/projects/mpich2/downloads/tarballs/1.4.1p1/mpich2-1.4.1p1.tar.gz',
              ]
    make_cmd = ['gmake']

    env = {'CFLAGS': '-fPIC', 'CXXFLAGS': '-fPIC', 'FFLAGS': '-fPIC'}
    conf_args = ['--prefix=${TGTDIR}', '--enable-fast', '--enable-smpcoll', '--with-pm=hydra', '--with-device=ch3:nemesis']
    optionList = ['shared', '32bit']

    conf_args_shared_append = ['--enable-shared', '--disable-rpath']

    env_32bit_append = {'CFLAGS': '-m32 -fPIC', 'CXXFLAGS': '-m32 -fPIC',
                        'FFLAGS': '-m32 -fPIC', 'LDFLAGS': '-m32'}

    # {{{ install()
    def install(self, tgtDir, obj):
        if obj=='mpich2':
            return super(MPICH2, self).install(tgtDir, obj)
        elif obj=='mpich2-redist':
            # mpich2-redist

            binDir = os.path.join(self.workDir, 'src', 'src', 'pm', 'hydra', '.libs')
            patterns = [(binDir, 'bin', 'mpiexec.hydra'),
                        (binDir, 'bin', 'hydra_nameserver'),
                        (binDir, 'bin', 'hydra_persist'),
                        (binDir, 'bin', 'hydra_pmi_proxy'),
                        ]

            libDir = os.path.join(self.workDir, 'src', 'lib')
            if 'shared' in self.options:
                patterns.append((libDir, 'lib', '*.so*'))

            for srcDir,dst,pat in patterns:
                dstDir = os.path.join(tgtDir, dst)
                for path in glob.glob('%s/%s' % (srcDir,pat)):
                    tgtPath = os.path.join(dstDir, os.path.relpath(path, srcDir))
                    copyX(path, tgtPath)

            os.symlink('mpiexec.hydra', os.path.join(tgtDir, 'bin', 'mpiexec'))
            os.symlink('mpiexec.hydra', os.path.join(tgtDir, 'bin', 'mpirun'))

            # {{{ script
            script='''#!/bin/bash
schd_name() {
    if   [[ "x" != "x${LSB_JOBID}" ]]; then
        echo "LSF"; exit;
    elif [[ "x" != "x${SLURM_JOB_ID}" ]]; then
        echo "SLURM"; exit;
    else
        echo "UNKNOWN"; exit
    fi
}

schd_job_id() {
    case $(schd_name) in
        LSF     ) echo ${LSB_JOBID}    ;;
        SLURM   ) echo ${SLURM_JOB_ID} ;;
        *       ) echo $(hostname):$$  ;;
    esac
}

prepare_mpi() {
    split_str() {
        while IFS=$2 read -ra ADDR; do
            for i in "${ADDR[@]}"; do
                echo "$i"
            done
        done <<< "$1"
    }

    do_lsf_mfile() {
        while [ $# -gt 0 ]
        do
            echo $1:$2
            shift 2
        done
    }

    do_slurm_mfile() {
        [[ "x$SLURM_JOB_NODELIST" == "x" ]] && LNODE=$SLURM_NODELIST || LNODE=$SLURM_JOB_NODELIST
        [[ "x$SLURM_JOB_CPUS_PER_NODE" == "x" ]] && NPROC=$SLURM_CPUS_ON_NODE || NPROC=$SLURM_JOB_CPUS_PER_NODE
        LNODE=( $(split_str "$LNODE" ",") )
        NPROC=$(split_str "$NPROC" ",")

        cnt=0
        for tok in $NPROC
        do
            if [[ "$tok" =~ '([0-9]+)\\(x([0-9]+)\\)' ]]
            then
                nproc=${BASH_REMATCH[1]}
                nnode=${BASH_REMATCH[2]}
            else
                nproc=$tok
                nnode=1
            fi
        
            let endcnt=$cnt+$nnode-1
            for i in $(seq $cnt $endcnt)
            do
                echo ${LNODE[$i]}:$nproc
            done
            let cnt=$cnt+$nnode
        done
    }

    case $(schd_name) in
        LSF     )
            mfile=hosts.$(schd_job_id)
            [[ ! -f $mfile ]] && do_lsf_mfile ${LSB_MCPU_HOSTS} > $mfile
            echo $mfile
            exit 0
            ;;
        SLURM   )
            # invoked with srun: only rank0 process should continue to start mpiexec
            [[ $SLURM_PROCID -gt 0 ]] && exit 255

            mfile=hosts.$(schd_job_id)
            [[ ! -f $mfile ]] && do_slurm_mfile > $mfile
            echo $mfile
            exit 0
            ;;
        *       )
            # do nothing with host file...
            echo 0
            exit 0
            ;;
    esac
}

cleanup_mpi() {
    case $(schd_name) in
        LSF     )
            mfile=hosts.$(schd_job_id)
            [[ -f $mfile ]] && rm $mfile
            ;;
        SLURM   )
            mfile=hosts.$(schd_job_id)
            [[ -f $mfile ]] && rm $mfile
            ;;
        *       )
            ;;
    esac
}

count_mpi_proc() {
    mfile=$1
    cnt=0
    for n in $(cut -f2 -d: $mfile)
    do 
        let cnt+=$n; 
    done
    echo $cnt
}
'''
			# }}}
            writeFile(tgtDir, os.path.join('etc', 'profile.d', 'mpich2.sh'), script, mode=0755)
    # }}}

__all__.append('MPICH2')
# }}}

# {{{ MVAPICH2
class MVAPICH2(GNUPackage):
    name = 'mvapich2'
    featureList = ['mvapich2', 'mvapich2-redist']
    version='1.7.2-1'
    src_url = ['/home/public/software/cluster/mvapich2-1.7.tgz',
                'http://mvapich.cse.ohio-state.edu/download/mvapich2/mvapich2-1.7.tgz',
              ]
    make_cmd = ['gmake']
    
    env = {'CFLAGS': '-fPIC', 'CXXFLAGS': '-fPIC', 'FFLAGS': '-fPIC'}
    conf_args = ['--prefix=${TGTDIR}', '--enable-fast', '--enable-smpcoll', '--with-pm=hydra']
    optionList = ['shared', '32bit', 'smp', 'ib']

    conf_args_shared_append = ['--enable-shared', '--disable-rpath']

    env_32bit_append = {'CFLAGS': '-m32 -fPIC', 'CXXFLAGS': '-m32 -fPIC',
                        'FFLAGS': '-m32 -fPIC', 'LDFLAGS': '-m32'}

    conf_args_smp_append = ['--with-device=ch3:nemesis']
    conf_args_ib_append = ['--with-device=ch3:nemesis:ib,tcp']

    patches = [
# {{{ 1. Export LD_LIBRARY_PATH so that osu_benchmark can find the shared libraries
'''--- a/Makefile.in     2011-11-21 14:15:18.000000000 +0800
+++ b/Makefile.in     2011-11-21 14:24:24.000000000 +0800
@@ -332,7 +332,7 @@
 	@if [ "@BUILD_TVDLL@" = "yes" ] ; then \\
 	( cd src/mpi/debugger && $(MAKE) ./libtvmpich2.@SHLIB_EXT@ ) ; fi
 	@if [ -s lib/pkglist.new ] ; then mv -f lib/pkglist.new lib/pkglist ; fi
-	( { test -d osu_benchmarks || mkdir osu_benchmarks; } && cd osu_benchmarks && $(master_top_srcdir)/osu_benchmarks/configure --prefix=@prefix@ CC=../bin/mpicc CPPFLAGS='-I ../include' LDFLAGS='-L ../lib -Wl,-rpath=@prefix@/lib' && $(MAKE) )
+	( { test -d osu_benchmarks || mkdir osu_benchmarks; } && cd osu_benchmarks && $(master_top_srcdir)/osu_benchmarks/configure --prefix=@prefix@ CC=../bin/mpicc CPPFLAGS='-I ../include' LDFLAGS='-L ../lib -Wl,-rpath=@prefix@/lib' LD_LIBRARY_PATH=../lib:$(LD_LIBRARY_PATH) && $(MAKE) )
 	@echo "Make completed"
 
 # The test on lib/.mpich2created lets us delete the local lib directory
''', # }}}
    ]

    # {{{ install()
    def install(self, tgtDir, obj):
        if obj=='mvapich2':
            return super(MVAPICH2, self).install(tgtDir, obj)
        elif obj=='mvapich2-redist':
            # mvapchi2-redist

            binDir = os.path.join(self.workDir, 'src', 'src', 'pm', 'hydra', '.libs')
            patterns = [(binDir, 'bin', 'mpiexec.hydra'),
                        (binDir, 'bin', 'hydra_nameserver'),
                        (binDir, 'bin', 'hydra_persist'),
                        (binDir, 'bin', 'hydra_pmi_proxy'),
                        ]

            libDir = os.path.join(self.workDir, 'src', 'lib')
            if 'shared' in self.options:
                patterns.append((libDir, 'lib', '*.so*'))

            for srcDir,dst,pat in patterns:
                dstDir = os.path.join(tgtDir, dst)
                for path in glob.glob('%s/%s' % (srcDir,pat)):
                    tgtPath = os.path.join(dstDir, os.path.relpath(path, srcDir))
                    copyX(path, tgtPath)

            os.symlink('mpiexec.hydra', os.path.join(tgtDir, 'bin', 'mpiexec'))
            os.symlink('mpiexec.hydra', os.path.join(tgtDir, 'bin', 'mpirun'))

            # {{{ script
            script='''#!/bin/bash
schd_name() {
    if   [[ "x" != "x${LSB_JOBID}" ]]; then
        echo "LSF"; exit;
    elif [[ "x" != "x${SLURM_JOB_ID}" ]]; then
        echo "SLURM"; exit;
    else
        echo "UNKNOWN"; exit
    fi
}

schd_job_id() {
    case $(schd_name) in
        LSF     ) echo ${LSB_JOBID}    ;;
        SLURM   ) echo ${SLURM_JOB_ID} ;;
        *       ) echo $(hostname):$$  ;;
    esac
}

prepare_mpi() {
    split_str() {
        while IFS=$2 read -ra ADDR; do
            for i in "${ADDR[@]}"; do
                echo "$i"
            done
        done <<< "$1"
    }

    do_lsf_mfile() {
        while [ $# -gt 0 ]
        do
            echo $1:$2
            shift 2
        done
    }

    do_slurm_mfile() {
        [[ "x$SLURM_JOB_NODELIST" == "x" ]] && LNODE=$SLURM_NODELIST || LNODE=$SLURM_JOB_NODELIST
        [[ "x$SLURM_JOB_CPUS_PER_NODE" == "x" ]] && NPROC=$SLURM_CPUS_ON_NODE || NPROC=$SLURM_JOB_CPUS_PER_NODE
        LNODE=( $(split_str "$LNODE" ",") )
        NPROC=$(split_str "$NPROC" ",")

        cnt=0
        for tok in $NPROC
        do
            if [[ "$tok" =~ '([0-9]+)\\(x([0-9]+)\\)' ]]
            then
                nproc=${BASH_REMATCH[1]}
                nnode=${BASH_REMATCH[2]}
            else
                nproc=$tok
                nnode=1
            fi
        
            let endcnt=$cnt+$nnode-1
            for i in $(seq $cnt $endcnt)
            do
                echo ${LNODE[$i]}:$nproc
            done
            let cnt=$cnt+$nnode
        done
    }

    case $(schd_name) in
        LSF     )
            mfile=hosts.$(schd_job_id)
            [[ ! -f $mfile ]] && do_lsf_mfile ${LSB_MCPU_HOSTS} > $mfile
            echo $mfile
            exit 0
            ;;
        SLURM   )
            # invoked with srun: only rank0 process should continue to start mpiexec
            [[ $SLURM_PROCID -gt 0 ]] && exit 255

            mfile=hosts.$(schd_job_id)
            [[ ! -f $mfile ]] && do_slurm_mfile > $mfile
            echo $mfile
            exit 0
            ;;
        *       )
            # do nothing with host file...
            echo 0
            exit 0
            ;;
    esac
}

cleanup_mpi() {
    case $(schd_name) in
        LSF     )
            mfile=hosts.$(schd_job_id)
            [[ -f $mfile ]] && rm $mfile
            ;;
        SLURM   )
            mfile=hosts.$(schd_job_id)
            [[ -f $mfile ]] && rm $mfile
            ;;
        *       )
            ;;
    esac
}

count_mpi_proc() {
    mfile=$1
    cnt=0
    for n in $(cut -f2 -d: $mfile)
    do 
        let cnt+=$n; 
    done
    echo $cnt
}
'''
			# }}}

            writeFile(tgtDir, os.path.join('etc', 'profile.d', 'mvapich2.sh'), script, mode=0755)
    # }}}

__all__.append('MVAPICH2')
# }}}

# {{{ Petsc
class Petsc(GNUPackage):
    name = 'petsc'
    featureList = ['petsc', 'petsc-redist']
    version = '3.1-p8'
    src_url = ['/home/public/software/petsc/petsc-lite-3.1-p8.tar.gz',
               'http://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-lite-3.1-p8.tar.gz'
              ]
    conf_cmd  = ['./configure']
    conf_args_common = [
                '--with-debugging=0',
                '--with-shared=0',
                '--with-x=0',
                '--with-pic=1'
                ]
    conf_args_solver_append = [
                '--download-superlu=1',
                ]
    conf_args_solver_mpi_append = [
                '--download-hypre=1',
                '--download-mumps=1',
                '--download-parmetis=1',
                '--download-superlu_dist=1',
                ]

    # icc
    conf_args_icc_append = ['--with-vendor-compilers=intel',
                            '--CFLAGS=-O2 -unroll -axSSE4.2,SSE4.1,SSSE3 -msse3',
                            '--CXXFLAGS=-O2 -unroll -axSSE4.2,SSE4.1,SSSE3 -msse3',
                            '--FFLAGS=-O2 -unroll -axSSE4.2,SSE4.1,SSSE3 -msse3',
                           ]
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
                '--with-scalapack-lib=[${MKL_LIBS}]',
                ]
    prereqs_src_mkl_append = ['mkl']

    # }}}

    # {{{ MPI library
    # no MPI support
    conf_args_nompi_append = ['--with-mpi=0',]

    # download and compile MPICH2
    conf_args_mpich2_append =  ['--download-mpich=1',
                                '--download-mpich-pm=mpd',
                                '--download-mpich-device=ch3:nemesis']

    # epel MPICH2
    conf_args_mpich2_epel_append   = ['--with-mpi-dir=/usr']
    prereqs_src_mpich2_epel_append = ['sys:epel-release', 'sys:mpich2-devel']

    # mpich2
    conf_args_mpich2_append   = ['--with-mpi-dir=${TGTDIR}']
    prereqs_mpich2_append = ['mpich2-redist']
    prereqs_src_mpich2_append = ['mpich2']

    # mvapchi2
    conf_args_mvapich2_append   = ['--with-mpi-dir=${TGTDIR}']
    prereqs_mvapich2_append = ['mvapich2-redist']
    prereqs_src_mvapich2_append = ['mvapich2']

    # }}}

    # {{{ patches
    patches = [
# {{{ 1. Free-up excess memory allocation for Aij matrix
r'''--- petsc-3.1-p7/src/mat/impls/aij/seq/aij.c    2010-03-25 22:13:15.000000000 +0800
+++ petsc-3.1-p5/src/mat/impls/aij/seq/aij.c    2011-02-18 22:21:22.000000000 +0800
@@ -688,6 +688,8 @@
   PetscInt       m = A->rmap->n,*ip,N,*ailen = a->ilen,rmax = 0;
   MatScalar      *aa = a->a,*ap;
   PetscReal      ratio=0.6;
+  PetscInt       *new_i, *new_j;
+  MatScalar      *new_a;

   PetscFunctionBegin;
   if (mode == MAT_FLUSH_ASSEMBLY) PetscFunctionReturn(0);
@@ -721,6 +723,19 @@
     SETERRQ3(PETSC_ERR_PLIB, "Unused space detected in matrix: %D X %D, %D unneeded", m, A->cmap->n, fshift);
   }

+  if(a->maxnz > a->nz)
+  {
+    ierr = PetscMalloc3(a->nz,MatScalar,&new_a,a->nz,PetscInt,&new_j,A->rmap->n+1,PetscInt,&new_i);CHKERRQ(ierr);
+    ierr = PetscMemcpy(new_a,a->a,a->nz*sizeof(MatScalar));CHKERRQ(ierr);
+    ierr = PetscMemcpy(new_i,a->i,(A->rmap->n+1)*sizeof(PetscInt));CHKERRQ(ierr);
+    ierr = PetscMemcpy(new_j,a->j,a->nz*sizeof(PetscInt));CHKERRQ(ierr);
+    ierr = MatSeqXAIJFreeAIJ(A,&a->a,&a->j,&a->i);CHKERRQ(ierr);
+    a->a = new_a;
+    a->i = new_i;
+    a->j = new_j;
+    a->maxnz = a->nz;
+  }
+
   ierr = MatMarkDiagonal_SeqAIJ(A);CHKERRQ(ierr);
   ierr = PetscInfo4(A,"Matrix size: %D X %D; storage space: %D unneeded,%D used\n",m,A->cmap->n,fshift,a->nz);CHKERRQ(ierr);
   ierr = PetscInfo1(A,"Number of mallocs during MatSetValues() is %D\n",a->reallocs);CHKERRQ(ierr);
''',# }}}
    ]
    if version2int(version)<=version2int('3.2'):
        patches.extend(
            [
# {{{ 2. Dirty trick to fix petscfix.h, NOT NECESSARY for petsc-dev
r'''--- a/config/BuildSystem/config/framework.py      2011-04-09 23:21:04.000000000 +0800
+++ b/config/BuildSystem/config/framework.py   2011-04-10 17:51:45.000000000 +0800
@@ -803,9 +803,9 @@
     for child in self.childGraph.vertices:
       self.outputPrototypes(f, child, 'Cxx')
     f.write('extern "C" {\n')
-    self.outputPrototypes(f, self, 'extern C')
+    self.outputPrototypes(f, self, 'C')
     for child in self.childGraph.vertices:
-      self.outputPrototypes(f, child, 'extern C')
+      self.outputPrototypes(f, child, 'C')
     f.write('}\n')
     f.write('#else\n')
     self.outputPrototypes(f, self, 'C')
''',
# }}}
            ])
    # }}}

    # {{{ __init__()
    def __init__(self, *args, **kwargs):
        options = kwargs.get('options', [])
        if not 'solver' in options:
            options.append('solver')

        if not ( 'mpich2_epel'  in options or
                 'mpich2_dl'    in options or
                 'mpich2'       in options or
                 'mvapich2'     in options or
                 'nompi'        in options ):
            options.append('mpich2_dl') # default to download mpich2

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

        self.dest_path_fixes = ['petsc/%s/conf/*' % self.arch]

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

            env['MPICH_CC']  = 'icc'
            env['MPICH_CXX'] = 'icpc'
            env['MPICH_F77'] = 'ifort'
            env['MPICH_F90'] = 'ifort'
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
            if mkl.singleLib:
                vars['MKL_LIB_DIR'] = os.path.join(vars['TGTDIR'], 'lib')
                vars['MKL_LIBS']    = os.path.join(vars['TGTDIR'], 'lib', mkl.fileSingleLib)
            else:
                vars['MKL_LIB_DIR'] = mkl.LIBDIR
                vars['MKL_LIBS']    = ','.join(mkl.libFileList())

        return super(Petsc, self)._subst_vars(lst_or_dict, vars)
    # }}}

    # {{{ install
    def install(self, tgtDir, obj):
        if obj=='petsc':
            super(Petsc, self).install(tgtDir, obj)

        # petsc-redist
        if 'mpich2_epel' in self.options or \
           'mpich2_dl' in self.options:

            if 'mpich2_epel' in self.options:
                patterns = [('/usr/lib64/mpich2/lib', 'lib', '*.so*'),
                            ('/usr/bin', 'bin', 'mpi*.py*'),
                            ('/usr/bin', 'bin', 'mpd*.py*'),
                            ]
            else:
                binDir = '%s/petsc/%s/bin' % (self.workDir, self.arch)
                patterns = [(binDir, 'bin', 'mpi*.py*'),
                            (binDir, 'bin', 'mpd*.py*'),
                            ]

            for srcDir,dst,pat in patterns:
                dstDir = os.path.join(tgtDir, dst)
                for path in glob.glob('%s/%s' % (srcDir,pat)):
                    tgtPath = os.path.join(dstDir, os.path.relpath(path, srcDir))
                    copyX(path, tgtPath)

            # symlinks
            if 'mpich2_epel' in self.options:
                patterns = [('/usr/bin', 'bin', 'mpi*.py'),
                            ('/usr/bin', 'bin', 'mpd*.py'),
                            ]
            else:
                binDir = '%s/petsc/%s/bin' % (self.workDir, self.arch)
                patterns = [(binDir, 'bin', 'mpi*.py*'),
                            (binDir, 'bin', 'mpd*.py*'),
                            ]
            for srcDir,dst,pat in patterns:
                dstDir = os.path.join(tgtDir, dst)
                for path in glob.glob('%s/%s' % (srcDir,pat)):
                    tgtPath = os.path.join(dstDir, os.path.relpath(path, srcDir))
                    ldst = os.path.join(dstDir, os.path.splitext(os.path.basename(path))[0])
                    lsrc = os.path.basename(tgtPath)
                    os.symlink(lsrc, ldst)

            # {{{ script
            script='''#!/bin/bash
prepare_mpi() {
  MPDTRACE_EXEC=mpdtrace
  MPD_EXEC=mpd

  $MPDTRACE_EXEC > /dev/null
  if [[ $? -ne 0 ]]
  then
    echo "Info: mpd is not running. Trying to start mpd..."

    # Create .mpd.conf if necessary
    if [ ! -f $HOME/.mpd.conf ]
    then
      echo "MPD_SECRETWORD=cogenda228998791" > $HOME/.mpd.conf
      chmod 600 $HOME/.mpd.conf
    fi
    $MPD_EXEC --daemon
    sleep 2
    if [[ $? -ne 0 ]]
    then
      echo "Error: can not start mpd."
      exit 1
    fi
  fi
}
'''
            # }}}
            writeFile(tgtDir, os.path.join('etc', 'profile.d', 'mpich2.sh'), script, mode=0755)

            patterns = ['bin/*.py']
            for pat in patterns:
                for path in glob.glob(os.path.join(tgtDir,pat)):
                    if os.path.islink(path): continue
                    subTxtFile(path, 'python2.4', 'python')


    # }}}

__all__.append('Petsc')
# }}}

# {{{ Petsc32
class Petsc32(GNUPackage):
    name = 'petsc'
    featureList = ['petsc', 'petsc-redist']
    version = '3.2-p3'
    src_url = ['/home/public/software/petsc/petsc-lite-3.2-p3.tar.gz',
               'http://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-lite-3.2-p3.tar.gz'
              ]
    conf_cmd  = ['./configure']
    conf_args_common = [
                '--with-debugging=0',
                '--with-shared-libraries=0',
                '--with-x=0',
                '--with-pic=1'
                ]
    conf_args_solver_append = [
                '--download-superlu=1',
                ]
    conf_args_solver_mpi_append = [
                '--download-hypre=1',
                '--download-mumps=1',
                '--download-parmetis=1',
                '--download-superlu_dist=1',
                ]

    # icc
    conf_args_icc_append = ['--with-vendor-compilers=intel',
                            '--CFLAGS=-O2 -unroll -axSSE4.2,SSE4.1,SSSE3 -msse3',
                            '--CXXFLAGS=-O2 -unroll -axSSE4.2,SSE4.1,SSSE3 -msse3',
                            '--FFLAGS=-O2 -unroll -axSSE4.2,SSE4.1,SSSE3 -msse3',
                           ]
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
                '--with-scalapack-lib=[${MKL_LIBS}]',
                ]
    prereqs_src_mkl_append = ['mkl']

    # }}}

    # {{{ MPI library
    # no MPI support
    conf_args_nompi_append = ['--with-mpi=0',]

    # download and compile MPICH2
    conf_args_mpich2_append =  ['--download-mpich=1',
                                '--download-mpich-pm=mpd',
                                '--download-mpich-device=ch3:nemesis']

    # epel MPICH2
    conf_args_mpich2_epel_append   = ['--with-mpi-dir=/usr']
    prereqs_src_mpich2_epel_append = ['sys:epel-release', 'sys:mpich2-devel']

    # mpich2
    conf_args_mpich2_append   = ['--with-mpi-dir=${TGTDIR}']
    prereqs_mpich2_append = ['mpich2-redist']
    prereqs_src_mpich2_append = ['mpich2']

    # mvapchi2
    conf_args_mvapich2_append   = ['--with-mpi-dir=${TGTDIR}']
    prereqs_mvapich2_append = ['mvapich2-redist']
    prereqs_src_mvapich2_append = ['mvapich2']

    # }}}

    # {{{ patches
    patches = [
# {{{ 1. Free-up excess memory allocation for Aij matrix
r'''--- petsc-3.1-p7/src/mat/impls/aij/seq/aij.c    2010-03-25 22:13:15.000000000 +0800
+++ petsc-3.1-p5/src/mat/impls/aij/seq/aij.c    2011-02-18 22:21:22.000000000 +0800
@@ -688,6 +688,8 @@
   PetscInt       m = A->rmap->n,*ip,N,*ailen = a->ilen,rmax = 0;
   MatScalar      *aa = a->a,*ap;
   PetscReal      ratio=0.6;
+  PetscInt       *new_i, *new_j;
+  MatScalar      *new_a;

   PetscFunctionBegin;
   if (mode == MAT_FLUSH_ASSEMBLY) PetscFunctionReturn(0);
@@ -721,6 +723,19 @@
     SETERRQ3(PETSC_ERR_PLIB, "Unused space detected in matrix: %D X %D, %D unneeded", m, A->cmap->n, fshift);
   }

+  if(a->maxnz > a->nz)
+  {
+    ierr = PetscMalloc3(a->nz,MatScalar,&new_a,a->nz,PetscInt,&new_j,A->rmap->n+1,PetscInt,&new_i);CHKERRQ(ierr);
+    ierr = PetscMemcpy(new_a,a->a,a->nz*sizeof(MatScalar));CHKERRQ(ierr);
+    ierr = PetscMemcpy(new_i,a->i,(A->rmap->n+1)*sizeof(PetscInt));CHKERRQ(ierr);
+    ierr = PetscMemcpy(new_j,a->j,a->nz*sizeof(PetscInt));CHKERRQ(ierr);
+    ierr = MatSeqXAIJFreeAIJ(A,&a->a,&a->j,&a->i);CHKERRQ(ierr);
+    a->a = new_a;
+    a->i = new_i;
+    a->j = new_j;
+    a->maxnz = a->nz;
+  }
+
   ierr = MatMarkDiagonal_SeqAIJ(A);CHKERRQ(ierr);
   ierr = PetscInfo4(A,"Matrix size: %D X %D; storage space: %D unneeded,%D used\n",m,A->cmap->n,fshift,a->nz);CHKERRQ(ierr);
   ierr = PetscInfo1(A,"Number of mallocs during MatSetValues() is %D\n",a->reallocs);CHKERRQ(ierr);
''',# }}}
    ]
    if version2int(version)<=version2int('3.3'):
        patches.extend(
            [
# {{{ 2. Dirty trick to fix petscfix.h, NOT NECESSARY for petsc-dev
r'''--- a/config/BuildSystem/config/framework.py      2011-04-09 23:21:04.000000000 +0800
+++ b/config/BuildSystem/config/framework.py   2011-04-10 17:51:45.000000000 +0800
@@ -803,9 +803,9 @@
     for child in self.childGraph.vertices:
       self.outputPrototypes(f, child, 'Cxx')
     f.write('extern "C" {\n')
-    self.outputPrototypes(f, self, 'extern C')
+    self.outputPrototypes(f, self, 'C')
     for child in self.childGraph.vertices:
-      self.outputPrototypes(f, child, 'extern C')
+      self.outputPrototypes(f, child, 'C')
     f.write('}\n')
     f.write('#else\n')
     self.outputPrototypes(f, self, 'C')
''',
# }}}
            ])
    # }}}

    # {{{ __init__()
    def __init__(self, *args, **kwargs):
        options = kwargs.get('options', [])
        if not 'solver' in options:
            options.append('solver')

        if not ( 'mpich2_epel'  in options or
                 'mpich2_dl'    in options or
                 'mpich2'       in options or
                 'mvapich2'     in options or
                 'nompi'        in options ):
            options.append('mpich2_dl') # default to download mpich2

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

        self.dest_path_fixes = ['petsc/%s/conf/*' % self.arch]

        super(Petsc32, self).__init__(*args, **kwargs)
    # }}}

    # {{{ _commonEnv()
    def _commonEnv(self, vars):
        env = super(Petsc32, self)._commonEnv(vars)

        paths, ld_paths = [], []
        if 'icc' in self.options:
            icc = self.deps['icc']
            paths.append(icc.BINDIR)
            ld_paths.append(icc.LDLIBDIR)

            env['MPICH_CC']  = 'icc'
            env['MPICH_CXX'] = 'icpc'
            env['MPICH_F77'] = 'ifort'
            env['MPICH_F90'] = 'ifort'
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
            if mkl.singleLib:
                vars['MKL_LIB_DIR'] = os.path.join(vars['TGTDIR'], 'lib')
                vars['MKL_LIBS']    = os.path.join(vars['TGTDIR'], 'lib', mkl.fileSingleLib)
            else:
                vars['MKL_LIB_DIR'] = mkl.LIBDIR
                vars['MKL_LIBS']    = ','.join(mkl.libFileList())

        return super(Petsc32, self)._subst_vars(lst_or_dict, vars)
    # }}}

    # {{{ install
    def install(self, tgtDir, obj):
        if obj=='petsc':
            super(Petsc32, self).install(tgtDir, obj)

        # petsc-redist
        if 'mpich2_epel' in self.options or \
           'mpich2_dl' in self.options:

            if 'mpich2_epel' in self.options:
                patterns = [('/usr/lib64/mpich2/lib', 'lib', '*.so*'),
                            ('/usr/bin', 'bin', 'mpi*.py*'),
                            ('/usr/bin', 'bin', 'mpd*.py*'),
                            ]
            else:
                binDir = '%s/petsc/%s/bin' % (self.workDir, self.arch)
                patterns = [(binDir, 'bin', 'mpi*.py*'),
                            (binDir, 'bin', 'mpd*.py*'),
                            ]

            for srcDir,dst,pat in patterns:
                dstDir = os.path.join(tgtDir, dst)
                for path in glob.glob('%s/%s' % (srcDir,pat)):
                    tgtPath = os.path.join(dstDir, os.path.relpath(path, srcDir))
                    copyX(path, tgtPath)

            # symlinks
            if 'mpich2_epel' in self.options:
                patterns = [('/usr/bin', 'bin', 'mpi*.py'),
                            ('/usr/bin', 'bin', 'mpd*.py'),
                            ]
            else:
                binDir = '%s/petsc/%s/bin' % (self.workDir, self.arch)
                patterns = [(binDir, 'bin', 'mpi*.py*'),
                            (binDir, 'bin', 'mpd*.py*'),
                            ]
            for srcDir,dst,pat in patterns:
                dstDir = os.path.join(tgtDir, dst)
                for path in glob.glob('%s/%s' % (srcDir,pat)):
                    tgtPath = os.path.join(dstDir, os.path.relpath(path, srcDir))
                    ldst = os.path.join(dstDir, os.path.splitext(os.path.basename(path))[0])
                    lsrc = os.path.basename(tgtPath)
                    os.symlink(lsrc, ldst)

            # {{{ script
            script='''#!/bin/bash
prepare_mpi() {
  MPDTRACE_EXEC=mpdtrace
  MPD_EXEC=mpd

  $MPDTRACE_EXEC > /dev/null
  if [[ $? -ne 0 ]]
  then
    echo "Info: mpd is not running. Trying to start mpd..."

    # Create .mpd.conf if necessary
    if [ ! -f $HOME/.mpd.conf ]
    then
      echo "MPD_SECRETWORD=cogenda228998791" > $HOME/.mpd.conf
      chmod 600 $HOME/.mpd.conf
    fi
    $MPD_EXEC --daemon
    sleep 2
    if [[ $? -ne 0 ]]
    then
      echo "Error: can not start mpd."
      exit 1
    fi
  fi
}
'''
            # }}}
            writeFile(tgtDir, os.path.join('etc', 'profile.d', 'mpich2.sh'), script, mode=0755)

            patterns = ['bin/*.py']
            for pat in patterns:
                for path in glob.glob(os.path.join(tgtDir,pat)):
                    if os.path.islink(path): continue
                    subTxtFile(path, 'python2.4', 'python')


    # }}}

__all__.append('Petsc32')
# }}}

# {{{ LibSVM
class LibSVM(GNUPackage):
    name = 'libsvm'
    version = '3.1'
    src_url = ['/home/public/software/science/libsvm-3.1.tar.gz',
               'http://www.csie.ntu.edu.tw/~cjlin/libsvm/libsvm-3.1.tar.gz'
              ]
    autoconf = None
    conf_cmd = None
    make_cmd = ['gmake', 'all', 'lib']

    optionList = ['32bit']

    def build(self, tgtDir):
        srcDir = os.path.join(self.workDir, 'src')

        mkFile = os.path.join(srcDir, 'Makefile')
        if '32bit' in self.options:
            subTxtFile(mkFile, 'CFLAGS\s*=.*', 'CFLAGS = -Wall -Wconversion -O3 -fPIC -m32 ', mode='re')
        else:
            subTxtFile(mkFile, 'CFLAGS\s*=.*', 'CFLAGS = -Wall -Wconversion -O3 -fPIC ', mode='re')

        super(LibSVM, self).build(tgtDir)

    def install(self, tgtDir, obj):
        srcDir = os.path.join(self.workDir, 'src')
        self.build(tgtDir)
        for f in ['svm-train', 'svm-predict', 'svm-scale']:
            path    = os.path.join(self.workDir, 'src', f)
            tgtPath = os.path.join(tgtDir, 'bin', f)
            copyX(path, tgtPath)
        copyX(os.path.join(self.workDir, 'src', 'libsvm.so.2'),
              os.path.join(tgtDir, 'lib', 'libsvm.so'))

__all__.append('LibSVM')
# }}}

# {{{ KLayout
class KLayout(GNUPackage):
    name = 'klayout'
    version = '0.21.13'
    src_url = ['/home/public/software/EDA/klayout-0.21.13.tar.gz',
               'http://www.klayout.de/klayout-0.21.13.tar.gz',
              ]
    prereqs = ['Qt-redist']
    prereqs_src = ['Qt']

    autoconf = None
    conf_cmd = None
    make_cmd = ['./build.sh', '-qt', '${TGTDIR}', '-bin', '${TGTDIR}/bin']
    #make_cmd = ['./build.sh', '-qt', '${TGTDIR}', '-bin', '${TGTDIR}/bin', '-option', '-j2']
    make_install_cmd = None

    def __init__(self, *args, **kwargs):
        options = kwargs.get('options', [])

        if '32bit' in options:
            self.make_cmd.extend(['-platform','linux-32-gcc-release'])
        else:
            self.make_cmd.extend(['-platform','linux-64-gcc-release'])

        super(KLayout, self).__init__(*args, **kwargs)

__all__.append('KLayout')
# }}}

