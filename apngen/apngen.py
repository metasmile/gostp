#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, codecs, time, datetime,re,argparse,textwrap, subprocess
from datetime import date, timedelta
from time import mktime
from os.path import expanduser
from shutil import copyfile
import sys
import codecs
from os.path import expanduser
import glob
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

__INTERVALI_SPLITTER__ = "_"
__DEFAULT_INTERVAL__ = "0.2"

def is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

def convert_to_apng(src_path, dest_path, is_verbose=False):
    if is_verbose:
        print "Start to export...", src_path, "=>" ,dest_path

    filter_files = lambda f: os.path.splitext(f)[1][1:].strip().lower()=='png'
    dir_abs_path = lambda d: os.path.join(src_path,d)
    dirs = lambda d: os.listdir(d)
    filter_only_dirs = lambda f: os.path.isdir(dir_abs_path(f)) and not f.startswith('.')

    target_dirs = filter(filter_only_dirs, dirs(src_path))
    targets = []
    for d in target_dirs:
        _ds = d.split(__INTERVALI_SPLITTER__)
        if not len(_ds):
            continue

        _dirs = dirs(dir_abs_path(d))
        if not len(_dirs):
            continue

        _item = {}
        _item["dirname"] = d
        _item["dirpath"] = dir_abs_path(d)

        if len(_ds)>1 and is_float(_ds[-1]):
            _item["filename"] = __INTERVALI_SPLITTER__.join(_ds[0:-1])
            _item["interval"] = _ds[-1]
        else:
            _item["filename"] = __INTERVALI_SPLITTER__.join(_ds)
            _item["interval"] = __DEFAULT_INTERVAL__

        _item["files"] = _dirs
        targets.append(_item)

    FNULL = None if is_verbose else open(os.devnull, 'w')

    for item in targets:
        dirpath = item["dirpath"]
        packname = item["filename"]
        frame_interval = str(int(float(item["interval"])*1000))

        output_apng_file = os.path.join(dest_path, (packname+'.png'))

        src_pngs_path_glob = os.path.join(dirpath, '*.png')
        src_pngs_paths = glob.glob(src_pngs_path_glob)

        if len(src_pngs_paths)>1:
            subprocess.call(['apngasm','-o', output_apng_file, src_pngs_path_glob,'-d',frame_interval,'-F'], stdout=FNULL, stderr=subprocess.STDOUT)
        else:
            for dest_png_path in src_pngs_paths:
                subprocess.call(['mkdir', dest_path], stdout=FNULL, stderr=subprocess.STDOUT)
                subprocess.call(['cp','-f', dest_png_path, output_apng_file], stdout=FNULL, stderr=subprocess.STDOUT)

        if is_verbose:
            print output_apng_file

    return dest_path

def main():
    parser = argparse.ArgumentParser(description='Generate all png frames to APNGs.')
    #parser.add_argument('target', help='Target path',required=False)
    #parser.add_argument('-f','--force', type=bool, help='Something forceful.)', default=None, required=False, nargs='*')
    args = parser.parse_args()

    #print args.target
    #__force__= args.force is not None

    #path
    __src_path__ = os.getcwd()
    __src_dirname_scheme__ = os.path.basename(__src_path__).split('_src')
    __dest_dirname__ = __src_dirname_scheme__[0]

    if len(__src_dirname_scheme__)!=2:
        print 'Default source directory name must be "%s_src" instead of "%s"' % (__dest_dirname__,__dest_dirname__)
        sys.exit(1)

    __dest_path__ = os.path.join(os.path.join(__src_path__,'..'), __dest_dirname__)
    print convert_to_apng(__src_path__, __dest_path__)

if __name__ == '__main__':
    main()
