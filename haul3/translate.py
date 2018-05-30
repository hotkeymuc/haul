#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
	HAUL3
	HotKey's Amphibious Unambiguous Language
	
	This program translates a given HAUL3/Python file into a different language.
	
"""

import os

from haul.utils import *

from haul.langs.py.haulReader_py import *

from haul.langs.asm.haulWriter_asm import *
from haul.langs.bas.haulWriter_bas import *
from haul.langs.c.haulWriter_c import *
from haul.langs.java.haulWriter_java import *
from haul.langs.js.haulWriter_js import *
from haul.langs.json.haulWriter_json import *
from haul.langs.lua.haulWriter_lua import *
from haul.langs.opl.haulWriter_opl import *
from haul.langs.pas.haulWriter_pas import *
from haul.langs.py.haulWriter_py import *
from haul.langs.vbs.haulWriter_vbs import *


def put(t):
	print(t)


############################################################

def translate(source_filename, WriterClass, output_path=None, dialect=None):
	"Translates the input file using the given language's Writer"
	
	name = nameByFilename(source_filename)
	
	streamIn = StringReader(readFile(source_filename))
	reader = HAULReader_py(stream=streamIn, filename=source_filename)
	
	streamOut = StringWriter()
	if dialect is None:
		writer = WriterClass(streamOut)
	else:
		writer = WriterClass(streamOut, dialect=dialect)
	
	if output_path is None:
		output_filename = source_filename + '.' + writer.defaultExtension
	else:
		if not os.path.exists(output_path):
			os.makedirs(output_path)
		output_filename = output_path + '/' + name + '.' + writer.defaultExtension
	
	monolithic = True	# Use simple (but good) monolithic version (True) or a smart multi-pass streaming method (False)
	
	reader.seek(0)
	
	put('Translating input file "' + source_filename + '"...')
	
	try:
		writer.stream(reader, monolithic=monolithic)	# That's where the magic happens!
	except HAULParseError as e:
		put('Parse error: ' + str(e.message))
		#raise
	
	put('Writing output file "' + output_filename + '"...')
	writeFile(output_filename, streamOut.r)
	

source_file = 'examples/hello.py'
#source_file = 'examples/small.py'
#source_file = 'examples/infer.py'
#source_file = 'examples/complex.py'
#source_file = 'examples/classes.py'
#source_file = 'examples/shellmini.py'
#source_file = 'examples/vm.py'
#source_file = 'haul/haul.py'

output_path = 'build'

WRITER_CLASSES = [
	HAULWriter_asm,
	HAULWriter_bas,
	HAULWriter_c,
	HAULWriter_java,
	HAULWriter_js,
	HAULWriter_json,
	HAULWriter_lua,
	HAULWriter_opl,
	HAULWriter_pas,
	HAULWriter_py,
	HAULWriter_vbs,
]

WriterClass = WRITER_CLASSES[10]

translate(source_file, WriterClass, output_path)


put('translate.py ended.')