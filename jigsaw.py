#!/bin/env python

import sys
import os
from jiglib.Logger import *
from jiglib.JigsawPkg import *

# {{{ loadCollection()
def loadCollection(name):
    import os.path
    import imp

    parts = name.split('.')
    path = parts[0:-1]
    name = parts[-1]


    dir, _ = os.path.split(os.path.abspath(__file__))
    path = os.path.join(dir, *path)

    fp, pathname, desc = imp.find_module(name, [path])
    coll = None
    try:
        mod = imp.load_module(name, fp, pathname, desc)
        for c in mod.__all__:
            cls = mod.__dict__[c]
            if issubclass(cls, Collection):
                coll = cls
                break
    finally:
        if fp: fp.close()
    return coll
# }}}

# {{{ parseOptions()
def parseOptions():
    from optparse import OptionParser

    usage = '''
    %prog [options] <collection> build
    %prog [options] <collection> install <dest dir>'''

    # Repository dir
    repoDir = os.environ.get('JIG_REPO_DIR', os.path.join(os.getcwd(), 'repo'))

    # temp dir for building
    bldDir  = os.environ.get('JIG_BLD_DIR',  '/tmp/jigsaw')


    parser = OptionParser(usage=usage)
    parser.add_option('--repo',   action='store', dest='repoDir',
                      default=repoDir, help='Repository directory.')
    parser.add_option('--build',  action='store', dest='bldDir',
                      default=bldDir, help='Temporary directory for building.')

    parser.add_option('-v', '--verbose', default=False,
                      action='store_true', dest='verbose')

    options, args = parser.parse_args()

    if len(args) < 2:
        parser.error('missing required argument')
    coll, verb = args[0:2]

    if verb == 'build':
        return coll, verb, None, options
    elif verb == 'install':
        if len(args)<3:
            parser.error('missing required argument')
        dest_dir = args[2]
        return coll, verb, dest_dir, options

# }}}
collName, verb, dest_dir, options = parseOptions()

from jiglib import Settings
if verb=='build':
  Settings.mode='src'     # must do it before loading the collection
else:
  Settings.mode='redist'

Coll = loadCollection(collName)
if Coll==None:
  print 'Could not load the collection %s' % collName
  sys.exit(-1)

detail_lvl=1
if options.verbose: detail_lvl=100

log = Logger(detail_lvl=detail_lvl)

base = BaseSystem(logger=log)
repo = Repository(options.repoDir, tmpDir=options.bldDir)

coll = Coll(repo, base, logger=log)

if verb=='build':
  log.write('Start building collection %s' %collName)
  coll.build()
  log.write('Finished building collection %s' %collName)
else:
  log.write('Start installing collection %s' %collName)
  coll.install(dest_dir)
  log.write('Finished installing collection %s' %collName)

