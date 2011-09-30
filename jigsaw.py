#!/bin/env python

import sys
import os
from jiglib.Logger import *
from jiglib.JigsawPkg import *
from jiglib import Settings

# {{{ loadCollection()
def loadCollection(name, opts=None):
    import os.path
    import imp, sys

    parts = name.split('.')
    path = parts[0:-1]
    name = parts[-1]

    dir, _ = os.path.split(os.path.abspath(__file__))
    paths = [os.path.join(dir, *path)]
    paths.extend(sys.path)

    fp, pathname, desc = imp.find_module(name, paths)
    coll = None
    try:
        Settings.collectionOpts = opts
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

    parser.add_option('--reloc', action='store', dest='reloc', default=None,
                      help='relocate the repo to this place.')
    parser.add_option('-v', '--verbose', default=False,
                      action='store_true', dest='verbose')
    parser.add_option('-o', action='append', dest='collOpts',
                      help='Options for the initializing the collection.')

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

collOpts={}
for x in options.collOpts:
  if ':' in x:
    k,v = x.split(':')
    collOpts[k]=v
  else:
    collOpts[x]=True

Coll = loadCollection(collName, opts=collOpts)
if Coll==None:
  print 'Could not load the collection %s' % collName
  sys.exit(-1)

detail_lvl=1
if options.verbose: detail_lvl=100

log = Logger(detail_lvl=detail_lvl)

base = BaseSystem(logger=log)
repo = Repository(options.repoDir, tmpDir=options.bldDir, logger=log)

coll = Coll(repo, base, logger=log, reloc=options.reloc)

if verb=='build':
  log.write('Start building collection %s' %collName)
  if not coll.build():
    sys.exit(-1)
  log.write('Finished building collection %s' %collName)
else:
  log.write('Start installing collection %s' %collName)
  if not coll.install(dest_dir):
    sys.exit(-1)
  log.write('Finished installing collection %s' %collName)

