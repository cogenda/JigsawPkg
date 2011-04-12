from JigsawPkg import *
from Packages import *
from Util import *

import os, os.path, shutil, glob, subprocess, tempfile
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

args=()
for arg in "$@"
do
    args[$i]="$arg"
    ((++i))
done
exec %s "${args[@]}"
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
        ret = subprocess.call(cmd, cwd=srcDir, env=env)
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

    def __init__(self, envsh, arch='intel64', **kwargs):
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

# }}}

# {{{ MKL Library
class MKL(Package):
    name = 'mkl'
    version = '1.0'
    features = ['mkl', 'mkl-redist']

    def __init__(self, envsh, arch='', **kwargs):
        self.INCDIR = None
        self.LIBDIR = None
        self.LDLIBDIR = None
        self.LIBPREFIX = kwargs.get('libPrefix', 'libmkl')
        self.INTERFACE = kwargs.get('interface', 'lp64')
        self.THREAD    = kwargs.get('thread', 'sequential')
        self.MPI       = kwargs.get('mpi', 'intelmpi')
        self.SCALAPACK = kwargs.get('scalapack', True)
        self.singleLib = kwargs.get('singleLib', True)
        self.LIBEXT = 'a'

        self.fileSingleLib = 'libmkl.a'

        if not os.path.exists(envsh):
            raise Exception

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
        if self.SCALAPACK:
            libs.append('${LIBPREFIX}_scalapack_${INTERFACE}.${LIBEXT}')
        libs.extend([
            '${LIBPREFIX}_solver_${INTERFACE}_${THREAD}.${LIBEXT}',
            '${LIBPREFIX}_intel_${INTERFACE}.${LIBEXT}',
            '${LIBPREFIX}_${THREAD}.${LIBEXT}',
            '${LIBPREFIX}_core.${LIBEXT}',
            '${LIBPREFIX}_blacs_${MPI}_${INTERFACE}.${LIBEXT}',
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
        print 'Combining libraries %s in %s' % (str(libs), tmpdir)
        for lib in libs:
            cmd = ['ar', 'x', lib]
            ret = subprocess.call(cmd, cwd=tmpdir)
            if not ret==0: raise Exception

        objs = os.listdir(tmpdir)

        cmd = ['ar', 'rcs', tflib]
        cmd.extend(objs)
        ret = subprocess.call(cmd, cwd=tmpdir)
        if not ret==0: raise Exception
        shutil.rmtree(tmpdir)

        os.rename(tflib, flib)
        print 'Combined library saved as %s' % flib

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
                '--download-hypre=1',
                ]
    conf_args_solver_mpi_append = [
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
                                '--download-mpich-device=ch3:nemesis']

    # epel MPICH2
    conf_args_mpich2_epel_append   = ['--with-mpi-dir=/usr']
    prereqs_src_mpich2_epel_append = ['sys:epel-release', 'sys:mpich2-devel']

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
        if 'mpich2_epel' in self.options:
            patterns = [('/usr/lib64/mpich2/lib', 'lib', '*.so*'),
                        ]
            for srcDir,dst,pat in patterns:
                dstDir = os.path.join(tgtDir, dst)
                for path in glob.glob('%s/%s' % (srcDir,pat)):
                    tgtPath = os.path.join(dstDir, os.path.relpath(path, srcDir))
                    copyX(path, tgtPath)

    # }}}

# }}}


