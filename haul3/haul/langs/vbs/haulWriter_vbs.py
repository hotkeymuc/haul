#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime

from haul.haul import *

def put(t):
	print('HAULWriter_vbs:\t' + str(t))


PAT_INFIX = [
	'+', '-', '/', '*', '%',
	'&', 'and', 'or', '|', '||', '^'
	'>', '<', '==', '>=', '<=',
]


class HAULWriter_vbs(HAULWriter):
	"Writes Visual BASIC code"
	
	def __init__(self, streamOut):
		HAULWriter.__init__(self, streamOut)
		#self.defaultExtension = 'bas'
		self.defaultExtension = 'vbs'
		self.writeComment('Translated from HAUL3 to Visual BASIC on ' + str(datetime.datetime.now()) )
		
	def writeComment(self, t):
		"Add a comment to the file"
		#self.streamOut.put('REM ' + t + '\n')
		self.streamOut.put('\' ' + t + '\n')
		
	def writeIndent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def writeNamespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			self.writeIndent(indent)
			self.writeComment('Namespace "' + str(ns) + '"')
			for id in ns.ids:
				#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
				if (id.name == 'res'): continue	# Do not (re-)declare result
				if (id.kind == 'var'):
					self.writeIndent(indent)
					#self.write('#@' + str(id.kind) + ' ' + str(id.name) + ' ' + str(id.data_type) + '\n')
					#self.write('DIM ' + str(id.name))
					self.write('DIM ' + str(id.name))
					self.write('	\' AS ')
					self.writeType(id.data_type)
					self.write('\n')
		
	def writeFunc(self, f, indent=0):
		f.destination = self.streamOut.size	# Record offset in output stream
		
		#self.writeNamespace(f.namespace, indent)
		
		self.writeIndent(indent)
		self.write('FUNCTION ')
		self.write(f.id.name)
		self.write('(')
		for i in xrange(len(f.args)):
			if (i > 0): self.write(', ')
			#self.writeExpression(args[i])
			self.writeVar(f.args[i])
			"""
			id = f.namespace.find_id(f.args[i].name)
			if (id == None):
				#self.writeComment('UnknownType')
				pass
			else:
				self.write(' AS ')
				self.writeType(id.data_type)
			"""
		self.write(')')
		
		self.write('\n')
		
		#self.writeNamespace(f.namespace, indent+1)
		self.writeBlock(f.block, indent+1)
		
		self.writeIndent(indent)
		self.write('END FUNCTION\n')
		
	def writeModule(self, m, indent=0):
		m.destination = self.streamOut.size	# Record offset in output stream
		
		self.writeComment('### Module "' + m.name + '"')
		for im in m.imports:
			self.write('\'INCLUDE ')
			self.write(str(im))
			self.write('\n')
			
		#self.write('### Module namespace...\n')
		self.writeNamespace(m.namespace, indent)
		
		self.writeComment('### Classes...')
		for typ in m.classes:
			self.writeClass(typ, indent)
		
		self.writeComment('### Funcs...')
		for func in m.funcs:
			self.writeFunc(func, indent)
		
		self.writeComment('### Root Block (main function):')
		if (m.block):
			self.writeBlock(m.block, indent)
		
	def writeClass(self, c, indent=0):
		c.destination = self.streamOut.size	# Record offset in output stream
		
		#self.write('# Class "' + t.id.name + '"\n')
		self.writeIndent(indent)
		self.write('class ')
		self.write(c.id.name)
		self.write(':\n')
		
		if (c.namespace):
			#self.writeIndent(indent+1)
			#self.write('### Class namespace...\n')
			self.writeNamespace(c.namespace, indent+1)
		
		#@TODO: Initializer?
		for func in c.funcs:
			self.writeFunc(func, indent+1)
		
		#self.write('# End-of-Type "' + t.id.name + '"\n')
		
	def writeBlock(self, b, indent=0):
		b.destination = self.streamOut.size	# Record offset in output stream
		
		#self.write("# Block \"" + b.name + "\"\n")
		"""
		if (b.namespace and len(b.namespace.ids) > 0):
			#self.writeIndent(indent)
			#self.write('### Block namespace...\n')
			self.writeNamespace(b.namespace, indent)
		"""
		
		for instr in b.instrs:
			self.writeIndent(indent)
			self.writeInstr(instr, indent)
			self.write('\n')
			
	def writeInstr(self, i, indent):
		i.destination = self.streamOut.size	# Record offset in output stream
		
		#put(' writing instruction: ' + str(i))
		if (i.control): self.writeControl(i.control, indent)
		if (i.call):
			self.writeCall(i.call)
		
	def writeControl(self, c, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0): self.write('ELSE ')	#elif
				self.write('IF (')
				
				self.writeExpression(c.exprs[j])
				self.write(') THEN\n')
				self.writeBlock(c.blocks[j], indent+1)
				j += 1
			
			if (j < len(c.blocks)):
				self.writeIndent(indent)
				self.write('ELSE\n')
				self.writeBlock(c.blocks[j], indent+1)
			self.write('END IF\n')
		
		elif (c.controlType == C_FOR):
			self.write('FOR ')
			self.writeExpression(c.exprs[0])
			self.write(' in ')
			self.writeExpression(c.exprs[1])
			self.write('\n')
			self.writeBlock(c.blocks[0], indent+1)
			
			self.write('NEXT ')
			self.writeExpression(c.exprs[0])
			
		elif (c.controlType == C_RETURN):
			self.write('RETURN ')
			self.writeExpression(c.exprs[0])
			self.write('\n')
		else:
			self.write('CONTROL "' + str(c.controlType) + '"\n')
		
	def writeCall(self, c, level=0):
		i = c.id.name
		
		# Set-variable-instruction
		if i == I_VAR_SET.name:
			
			## Annotate type if available
			# if (c.args[0].var) and (not c.args[0].var.type == None): self.write('#@' + c.args[0].var.type.name + '\n')
			
			#self.writeVar(c.args[0].var)
			self.writeExpression(c.args[0], level)
			self.write(' = ')
			self.writeExpression(c.args[1], level)
		
		elif i == I_ARRAY_LOOKUP.name:
			self.writeExpression(c.args[0], level)
			self.write('(')
			self.writeExpressionList(c.args, 1, level)
			self.write(')')
			
		elif i == I_ARRAY_CONSTRUCTOR.name:
			self.write('(')
			self.writeExpressionList(c.args, 0, level)
			self.write(')')
			
		elif i == I_OBJECT_CALL.name:
			self.writeExpression(c.args[0], level)
			self.write('(')
			self.writeExpressionList(c.args, 1, level)
			self.write(')')
			
		elif i == I_OBJECT_LOOKUP.name:
			self.writeExpression(c.args[0], level)
			self.write('.')
			self.writeExpression(c.args[1], level)
		
		elif any(i in p for p in PAT_INFIX):
			self.writeExpression(c.args[0], level)	# level-1
			
			self.write(' ' + i + ' ')
			
			self.writeExpression(c.args[1], level)	# level-1
		
		else:
			# Write a standard call
			if (i == 'str'):
				i = '""+'
			
			if (level == 0):
				self.write('CALL ')
				self.write(i)
				self.write('(')
				self.writeExpressionList(c.args, 0, level)
				self.write(')')
			else:
				self.write(i)
				self.write('(')
				self.writeExpressionList(c.args, 0, level)
				self.write(')')
			
	def writeExpressionList(self, es, start, level):
		i = 0
		for i in xrange(len(es)-start):
			if (i > 0): self.write(', ')
			self.writeExpression(es[start+i], level=level)
	
	def writeExpression(self, e, level=0):
		if (e.value): self.writeValue(e.value)
		if (e.var): self.writeVar(e.var)
		if (e.call):
			if (level > 0): self.write('(')
			self.writeCall(e.call, level+1)
			if (level > 0): self.write(')')
			
	def writeValue(self, v):
		if (type(v.data) == str):
			self.write('"' + v.data + '"')	#@TODO: Escaping!
		else:
			self.write(str(v))	#.data
	
	def writeType(self, v):
		if (v == T_INTEGER):	v = 'INTEGER';
		elif (v == T_FLOAT):	v = 'SINGLE';
		elif (v == T_STRING):	v = 'STRING';
		self.write(str(v))
	
	def writeVar(self, v):
		self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')

