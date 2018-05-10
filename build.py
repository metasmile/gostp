#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os, time, datetime, re, argparse, textwrap, subprocess
from datetime import date, timedelta
from time import mktime
from os.path import expanduser
import shutil
from distutils.dir_util import copy_tree
import json
import glob
from apngen.apngen import convert_to_apng
import codecs

sys.stdout = codecs.getwriter("utf8")(sys.stdout)
sys.stderr = codecs.getwriter("utf8")(sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Complie APNGs and then build a stickerpack with a valid xcode project.")

    parser.add_argument("src_path", help="Target source path. (default=./)", default="./", nargs="*")
    parser.add_argument("dest_path", help="Target destination path.", nargs="+")

    parser.add_argument("-n", "--name", help="App Name (Project Name)", nargs="*")
    parser.add_argument("-v", "--version", help="App Version String", nargs="*")
    parser.add_argument("--display-name", help="App Display Name", nargs="*")
    parser.add_argument("-i", "--bundle-id", help="App Bundle Id", nargs="*")
    parser.add_argument("--extension-name", help="Extension Name", nargs="*")
    parser.add_argument("-e", "--extension-bundle-id", help="Extension Bundle Id", nargs="*")

    parser.add_argument("--dest-relative-path", help="Destination app relative path", nargs="*")
    parser.add_argument("--grid-size", help="Sticker Grid Size", nargs="*")
    parser.add_argument("--clean-app", type=bool, help="Clean already built app files before start.", default=False,
                        nargs="*")

    args = vars(parser.parse_args())
    for ak, av in [(arg, args[arg]) for arg in args]:
        if isinstance(av, list):
            args[ak] = av[0] if len(av) else None

    __STP_PATH__ = os.path.dirname(__file__)
    __STP_APP_PATH__ = os.path.join(__STP_PATH__, "stpapp")
    __STP_CONFIG__ = {
        "stp_app_relative_path": args["dest_relative_path"] or "app",
        "stp_allowing_stickerpack_exts": ["png", "gif", "jpg"]
    }
    __STP_APP_CLEAN__ = args["clean_app"] is not False

    app_template_config_dict = {
        "__stp_appname__": args["name"] or "Sticker",
        "__stp_appdisplayname__": args["display_name"] or "Sticker",
        "__stp_version__": args["version"] or "1.0",
        "__stp_bundleid__": args["bundle_id"] or "com.gostp.sticker",

        "__stp_appname_ext__": args["extension_name"] or args["name"] + "Pack",
        "__stp_bundleid_ext__": args["extension_bundle_id"] or "com.gostp.sticker.pack"
    }

    dest_app_ext_name = app_template_config_dict["__stp_appname_ext__"]

    src_path = expanduser(args["src_path"])
    if not os.path.exists(src_path):
        print "[!] Source path does not exist."
        sys.exit(1)

    dest_path = expanduser(args["dest_path"])
    if not os.path.exists(dest_path):
        print "[i] Destination path does not exist. Creating ..."
        os.makedirs(dest_path)

    dest_app_path = os.path.join(dest_path, __STP_CONFIG__["stp_app_relative_path"])

    # get sticker grid size setting
    app_sticker_grid_size = args["grid_size"]
    if not app_sticker_grid_size in ["small", "regular", "large"]:
        app_sticker_grid_size = "regular"

    # phase -1: clean up
    print "[i] Clean up ..."
    __CLEANING_TARGET_PATH__ = [
        #caches
        os.path.join(__STP_APP_PATH__, "DerivedData")
        , os.path.join(dest_app_path, "DerivedData")
    ]
    for clean_dir in __CLEANING_TARGET_PATH__:
        if os.path.exists(clean_dir):
            shutil.rmtree(clean_dir)

    # phase 0: build APNGs
    print "[i] Compiling APNGs and copying ..."
    convert_to_apng(src_path, dest_path)

    print "[i] Generating Xcode Project ..."
    # phase 1: copy
    is_dest_app_exists = os.path.exists(dest_app_path)
    if is_dest_app_exists:
        if __STP_APP_CLEAN__:
            shutil.rmtree(dest_app_path)
            is_dest_app_exists = False

    if not is_dest_app_exists:
        if shutil.copytree(__STP_APP_PATH__, dest_app_path):
            print "[!] Failed to initialize"
            sys.exit(1)

    # phase 2: replace file names
    for dir, subdirs, files in list(os.walk(dest_app_path, topdown=False)):
        for path in [os.path.join(dir, f) for f in files] + [dir]:  # [!] rename subfile -> parent dir
            file = os.path.basename(path)

            if path == dest_app_path or file.startswith("."):
                continue

            for k, v in [(i, app_template_config_dict[i]) for i in app_template_config_dict]:
                if k in file:
                    new_path = path.replace(k, v)
                    os.rename(path, new_path)

    # phase 3: replace file content
    for path, subdirs, files in list(os.walk(dest_app_path, topdown=True)):
        if path == dest_app_path:
            continue

        for file_in_path in [os.path.join(path, f) for f in files]:
            file = os.path.basename(file_in_path)
            if file.startswith("."):
                continue

            with open(file_in_path) as chkfile:
                if not istextfile(chkfile):
                    continue
                chkfile.close()

            rcur = codecs.open(file_in_path, "r", "utf-8")
            wlines = []
            for line in rcur.readlines():
                for k, v in [(i, app_template_config_dict[i]) for i in app_template_config_dict]:
                    if k in line:
                        line = line.replace(k, v)
                wlines.append(line)
            rcur.close()

            wcur = codecs.open(file_in_path, "w", "utf-8")
            wcur.writelines(wlines)
            wcur.close()

    # phase 4: insert sticker files
    __TEMP_STICKER_PACK_DIR_NAME__ = "__stp_appname_ext__"
    __TEMP_STICKER_PACK_NAME__ = "__stickername__.sticker"

    src_stickerpack_path = os.path.join(__STP_APP_PATH__, __TEMP_STICKER_PACK_DIR_NAME__, "Stickers.xcstickers",
                                        "StickerPack.stickerpack")

    dest_stickerpack_path = os.path.join(dest_app_path, dest_app_ext_name, "Stickers.xcstickers",
                                         "StickerPack.stickerpack")
    if not os.path.exists(dest_stickerpack_path):
        print "[i] Destination sticker pack path does not exist. Creating ..."
        os.makedirs(dest_stickerpack_path)

    # phase 5: copy iconset if it has existed
    src_stickericon_path = os.path.join(src_path, "@iconset")
    if os.path.exists(src_stickericon_path):
        dest_stickericon_path = os.path.join(dest_app_path, dest_app_ext_name, "Stickers.xcstickers", "iMessage App Icon.stickersiconset")
        copy_tree(src_stickericon_path, dest_stickericon_path)

    # listing and copy APNGs
    __DEST_TEMP_STICKER_PACK_PATH__ = os.path.join(dest_stickerpack_path, __TEMP_STICKER_PACK_NAME__)

    __SRC_TEMP_STICKER_PACK_PATH__ = os.path.join(src_stickerpack_path, __TEMP_STICKER_PACK_NAME__)
    __SRC_STICKER_PACK_CONTENTS_PATH__ = os.path.join(__SRC_TEMP_STICKER_PACK_PATH__, "Contents.json")
    __SRC_STICKER_PACK_CONTENTS__ = json.load(codecs.open(__SRC_STICKER_PACK_CONTENTS_PATH__, "r", "utf-8"))

    sticker_image_src_path_list = sum([glob.glob(e) for e in [os.path.join(dest_path, "*." + ext) for ext in
                                                              __STP_CONFIG__["stp_allowing_stickerpack_exts"]]], [])
    for sticker_image_src_path in sticker_image_src_path_list:
        sticker_filename = os.path.basename(sticker_image_src_path)
        sticker_name = os.path.splitext(sticker_filename)[0]
        sticker_pack_filename = sticker_name + ".sticker"
        dest_sticker_image_path = os.path.join(dest_stickerpack_path, sticker_pack_filename)
        # make sticker pack dir
        if not os.path.exists(dest_sticker_image_path):
            os.makedirs(dest_sticker_image_path)
        # copy image file
        shutil.copyfile(sticker_image_src_path, os.path.join(dest_sticker_image_path, sticker_filename))
        # generate Contents.json by Stickerpacks
        stickerpack_contents = dict(__SRC_STICKER_PACK_CONTENTS__)
        stickerpack_contents["properties"]["filename"] = sticker_filename
        with codecs.open(os.path.join(dest_sticker_image_path, "Contents.json"), "w", "utf-8") as w:
            w.write(json.dumps(stickerpack_contents, sort_keys=True, indent=4))
            w.close()
    # clean temp file
    if os.path.exists(__DEST_TEMP_STICKER_PACK_PATH__):
        shutil.rmtree(__DEST_TEMP_STICKER_PACK_PATH__)

    # generate root Contents.json of Stickerpack
    src_stickerpack_contents_path = os.path.join(src_stickerpack_path, "Contents.json")
    src_stickerpack_contents = json.load(codecs.open(src_stickerpack_contents_path, "r", "utf-8"))

    # configure
    # "properties": {
    #      "grid-size": "large"
    #      "grid-size": "regular"
    #      "grid-size": "small"
    # },
    __GRID_SIZE_KEY__ = "grid-size"
    __PROPERTIES_KEY__= "properties"
    __STICKERS_KEY__ = "stickers"
    if not __PROPERTIES_KEY__ in src_stickerpack_contents:
        src_stickerpack_contents[__PROPERTIES_KEY__] = {}

    src_stickerpack_contents[__PROPERTIES_KEY__][__GRID_SIZE_KEY__] = app_sticker_grid_size
    src_stickerpack_contents[__STICKERS_KEY__] = [{"filename": os.path.basename(e)} for e in
                                            glob.glob(os.path.join(dest_stickerpack_path, "*.sticker"))]

    dest_stickerpack_contents_path = os.path.join(dest_stickerpack_path, "Contents.json")
    with codecs.open(dest_stickerpack_contents_path, "w", "utf-8") as w:
        w.write(json.dumps(src_stickerpack_contents, sort_keys=True, indent=4))
        w.close()

    return dest_app_path

def istextfile(fileobj, blocksize=512):
    PY3 = sys.version_info[0] == 3
    int2byte = (lambda x: bytes((x,))) if PY3 else chr
    _text_characters = (
            b"".join(int2byte(i) for i in range(32, 127)) +
            b"\n\r\t\f\b")

    block = fileobj.read(blocksize)
    if b"\x00" in block:
        return False
    elif not block:
        return True

    nontext = block.translate(None, _text_characters)
    return float(len(nontext)) / len(block) <= 0.30


if __name__ == "__main__":
    print main()
