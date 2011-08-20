__all__=['CogendaTCAD']

from jiglib.JigsawPkg import *
from jiglib.Packages import *
from jiglib.CommonPkgs import *
from jiglib.Logger import *
import os

class Genius(WafPackage):
    name = 'Genius'
    version = '20110401'
    prereqs = ['petsc-redist']
    prereqs_src = ['petsc', 'cgnslib', 'vtk']
    src_url = ['http://github.com/cogenda/Genius-TCAD-Open/tarball/20110405',
               '/home/public/software/TCAD/genius-20110401-open.tar.bz2']

    def __init__(self, *args, **kwargs):
        super(Genius, self).__init__(*args, **kwargs)

        petsc = self.deps['petsc']
        self.waf_args = [
            '--prefix=${TGTDIR}/genius',
            '--version=%s' % self.version,
            '--with-petsc-dir=${TGTDIR}/petsc/%s' % petsc.arch,
            '--with-petsc-arch=',
            '--with-cgns-dir=${TGTDIR}',
            '--with-vtk-dir=${TGTDIR}',
            #'--with-vtk-ver=vtk-5.4',
            ]

    def install(self, tgtDir, obj):
        for d in ['bin', 'lib', 'examples']:
            dir = os.path.join(tgtDir, 'genius', d)
            if not os.path.exists(dir):
                os.makedirs(dir)

        super(Genius, self).install(tgtDir, obj)

    def installWorld(self, wldDir, objDir, obj):
        lst = super(Genius, self).installWorld(wldDir, objDir, obj)

        script='''#!/bin/bash
args=()
for arg in "$@"
do
    args[$i]="$arg"
    ((++i))
done

export PATH=${TGTDIR}/genius/bin:${TGTDIR}/bin:$PATH
if [[ "x$LD_LIBRARY_PATH" == "x" ]]
then
    export LD_LIBRARY_PATH=${TGTDIR}/lib
else
    export LD_LIBRARY_PATH=${TGTDIR}/lib:$LD_LIBRARY_PATH
fi
export GENIUS_DIR=${TGTDIR}/genius

exec genius.LINUX "${args[@]}"
'''
        script = self._subst_vars(script, {'TGTDIR':wldDir})

        writeFile(wldDir, 'genius/bin/genius', script, mode=0755)
        lst.append(os.path.join(wldDir, 'genius', 'bin', 'genius'))

        return lst

class CogendaTCAD(Collection):
    _cgnslib = CGNSLib(options=['pic'])
    _cmake = CMake()
    _vtk = VTK(_cmake)

    # petsc
    _petsc_gcc = Petsc(options=['nompi'])

    genius = Genius(_petsc_gcc, _cgnslib, _vtk)


