#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

from haul.platforms.android.haulBuilder_android import *
from haul.platforms.arduino.haulBuilder_arduino import *
from haul.platforms.dos.haulBuilder_dos import *
from haul.platforms.gameboy.haulBuilder_gameboy import *
from haul.platforms.html.haulBuilder_html import *
from haul.platforms.java.haulBuilder_java import *
from haul.platforms.palmos.haulBuilder_palmos import *
from haul.platforms.psion.haulBuilder_psion import *
from haul.platforms.vtech.haulBuilder_vtech import *
from haul.platforms.webos.haulBuilder_webos import *



#source_filename = 'hello.py'
#source_filename = 'small.py'
#source_filename = 'shellmini.py'
#source_filename = 'hres_test.py'
#source_filename = 'hio_test.py'

perform_test_run = True


#builder = HAULBuilder_android()
#builder = HAULBuilder_arduino()
#builder = HAULBuilder_dos()
#builder = HAULBuilder_gameboy()
builder = HAULBuilder_html()
#builder = HAULBuilder_java()
#builder = HAULBuilder_palmos()
#builder = HAULBuilder_psion()
#builder = HAULBuilder_vtech()
#builder = HAULBuilder_webos()


#resources = [
#	os.path.join(source_path, 'hres_data1.txt'),
#	os.path.join(source_path, 'hres_data2.txt'),
#]

#builder.source_path = os.path.abspath('examples')
#builder.libs_path = 'libs'
#builder.data_path = 'data'
#builder.staging_path = 'staging'
#builder.output_path = 'build'


builder.add_lib('hio')
#builder.add_source('helper', 'examples/small.py', is_main=False)
builder.set_source('examples/hello.py')

#builder.translate()
#builder.compile()
#builder.package()
#builder.test()
builder.build(perform_test_run=perform_test_run)

üüüüüüüüüüüüüüü I am in the midst of changing the structure
@TODO: HAULTranslator? Just to "quickly" translate something. Can be re-used by builders!


#builder.finish()

put('build.py ended.')