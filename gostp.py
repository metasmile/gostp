#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os, time, datetime,re,argparse,textwrap, subprocess
from datetime import date, timedelta
from time import mktime
from os.path import expanduser
import shutil
import json
import glob
from apngen.apngen import convert_to_apng
import codecs

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

def main():
	__STP_PATH__ = os.path.dirname(__file__)
	__STP_APP_PATH__ = os.path.join(__STP_PATH__, 'stpapp')
	__STP_CONFIG__ = {
		"stp_app_path": "app",
		"stp_allowing_stickerpack_exts": ["png","gif","jpg"]
	}

	app_template_config_dict = {
		"__stp_appname__": "stpnewapp",
		"__stp_appdisplayname__": "New Sticker Pack",
		"__stp_appname_ext__": "stpnewapp_pack",
		"__stp_bundleid__": "com.stells.stpnewapp",
		"__stp_bundleid_ext__": "com.stells.stpnewapp.pack"
	}

	src_path = '/Users/blackgene/Documents/hallo_src/'
	if not os.path.exists(src_path):
		print "[!] Source path does not exist."
		sys.exit(1)

	dest_path = '/Users/blackgene/Documents/gostp_new_test/'
	if not os.path.exists(dest_path):
		print "[i] Destination path does not exist. Creating ..."
		os.makedirs(dest_path)

	dest_app_path = os.path.join(dest_path, __STP_CONFIG__["stp_app_path"])

	#phase -1: clean up
	print "[i] Clean up ..."
	__CLEANING_TARGET_PATH__ = [
		os.path.join(__STP_APP_PATH__, "DerivedData"),
		os.path.join(dest_app_path, "DerivedData")
	]
	for clean_dir in __CLEANING_TARGET_PATH__:
		if os.path.exists(clean_dir):
			shutil.rmtree(clean_dir)

	#phase 0: build APNGs
	print "[i] Compiling APNGs and copying ..."
	convert_to_apng(src_path, dest_path)

	print "[i] Generating Xcode Project ..."
	#phase 1: copy
	if os.path.exists(dest_app_path):
		shutil.rmtree(dest_app_path)
	if shutil.copytree(__STP_APP_PATH__,dest_app_path):
		print "[!] Failed to initialize"
		sys.exit(1)

	#phase 2: replace file names
	for path, subdirs, files in list(os.walk(dest_app_path, topdown=True)):
		file = os.path.basename(path)
		if path==dest_app_path or file.startswith('.'):
			continue

		for k, v in [(i,app_template_config_dict[i]) for i in app_template_config_dict]:
			if k in file:
				new_path = path.replace(k, v)
				os.rename(path, new_path)

	#phase 3: replace file content
	for path, subdirs, files in list(os.walk(dest_app_path, topdown=True)):
		if path==dest_app_path:
			continue

		for file_in_path in [os.path.join(path, f) for f in files]:
			file = os.path.basename(file_in_path)
			if file.startswith('.'):
				continue

			with open(file_in_path) as chkfile:
				if not istextfile(chkfile):
					continue
				chkfile.close()

			rcur = codecs.open(file_in_path, 'r','utf-8')
			wlines = []
			for line in rcur.readlines():
				for k, v in [(i,app_template_config_dict[i]) for i in app_template_config_dict]:
					if k in line:
						line = line.replace(k,v)
				wlines.append(line)
			rcur.close()

			wcur = codecs.open(file_in_path, 'w','utf-8')
			wcur.writelines(wlines)
			wcur.close()

	#phase 4: insert sticker files
	stickerpack_path = os.path.join(dest_app_path, "StickerPackExtension", "Stickers.xcstickers", "StickerPack.stickerpack")
	if not os.path.exists(stickerpack_path):
		print "[i] Destination sticker pack path does not exist. Creating ..."
		os.makedirs(stickerpack_path)

	# listing and copy APNGs
	__TEMP_STICKER_PACK_NAME__ = "__stickername__.sticker"
	__TEMP_STICKER_PACK_PATH__ = os.path.join(stickerpack_path, __TEMP_STICKER_PACK_NAME__)
	__TEMP_STICKER_PACK_CONTENTS_PATH__ = os.path.join(__TEMP_STICKER_PACK_PATH__, "Contents.json")
	__TEMP_STICKER_PACK_CONTENTS__ = json.load(codecs.open(__TEMP_STICKER_PACK_CONTENTS_PATH__,"r","utf-8"))

	sticker_image_src_path_list = sum([glob.glob(e) for e in [os.path.join(dest_path,"*."+ext) for ext in __STP_CONFIG__["stp_allowing_stickerpack_exts"]]], [])
	for sticker_image_src_path in sticker_image_src_path_list:
		sticker_filename = os.path.basename(sticker_image_src_path)
		sticker_name = os.path.splitext(sticker_filename)[0]
		sticker_pack_filename = sticker_name+".sticker"
		sticker_image_dest_path = os.path.join(stickerpack_path, sticker_pack_filename)
		#make sticker pack dir
		if not os.path.exists(sticker_image_dest_path):
			os.makedirs(sticker_image_dest_path)
		#copy image file
		shutil.copyfile(sticker_image_src_path, os.path.join(sticker_image_dest_path, sticker_filename))
		#generate Contents.json by Stickerpacks
		stickerpack_contents =  dict(__TEMP_STICKER_PACK_CONTENTS__)
		stickerpack_contents["properties"]["filename"] = sticker_filename
		with codecs.open(os.path.join(sticker_image_dest_path, "Contents.json"),"w","utf-8") as w:
			w.write(json.dumps(stickerpack_contents, sort_keys=True, indent=4))
			w.close()
	#clean temp file
	if os.path.exists(__TEMP_STICKER_PACK_PATH__):
		shutil.rmtree(__TEMP_STICKER_PACK_PATH__)

	#generate root Contents.json of Stickerpack
	stickerpack_contents_path = os.path.join(stickerpack_path, "Contents.json")
	stickerpack_contents = json.load(codecs.open(stickerpack_contents_path,"r","utf-8"))
	stickerpack_contents["stickers"] = [{"filename": os.path.basename(e)} for e in glob.glob(os.path.join(stickerpack_path,"*.sticker"))]

	with codecs.open(stickerpack_contents_path,"w","utf-8") as w:
		w.write(json.dumps(stickerpack_contents, sort_keys=True, indent=4))
		w.close()

	return


def istextfile(fileobj, blocksize=512):
	PY3 = sys.version_info[0] == 3
	int2byte = (lambda x: bytes((x,))) if PY3 else chr
	_text_characters = (
	        b''.join(int2byte(i) for i in range(32, 127)) +
	        b'\n\r\t\f\b')

	block = fileobj.read(blocksize)
	if b'\x00' in block:
		return False
	elif not block:
		return True

	nontext = block.translate(None, _text_characters)
	return float(len(nontext)) / len(block) <= 0.30

if __name__ == '__main__':
	main()
