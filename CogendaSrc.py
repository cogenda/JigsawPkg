from jiglib.Package import *

import os, os.path, shutil

class CGNSLib(GNUPackage):
    name = 'cgnslib'
    version = '2.5-5'
    src_url = '/home/public/software/science/cgnslib_2.5-5.tar.gz'
    conf_args = ['--prefix=${TGTDIR}', '--enable-64bit', '--enable-lfs']
    def __init__(self):
        super(CGNSLib, self).__init__()

class Qt4(GNUPackage):
    name = 'Qt'
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
    def __init__(self):
        super(Qt4, self).__init__()

#class VTK(CMakePackage):
#    pass

repo = Repository('/home/hash/build/jigpkg/repo', tmpDir='/home/hash/tmp/buildtmp')

cgnslib = CGNSLib()
qt4 = Qt4()

repo.addPackage(cgnslib)
repo.addPackage(qt4)

