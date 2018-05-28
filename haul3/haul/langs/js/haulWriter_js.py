#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""

TODO:
	* None --> undefined
	* provide:
		print(...) --> console.log
		str(...) --> ...toString()
	* check environment:
		Browser
		nodejs
		JScript
		
	* self --> this is currently handled by manipulating the name space. That's kind of uncool.

"""

import datetime
import copy

from haul.haul import *

def put(t):
	print('HAULWriter_js:\t' + str(t))


INFIX_TRANS = {
	'and':	'&&',
	'or':	'||',
	'not':	'!',
	'&':	'&',
	'|':	'|',
	'^':	'^',
	'%':	'%',
	'+':	'+',
	'-':	'-',
	'*':	'*',
	'/':	'/',
	'<':	'<',
	'>':	'>',
	'<=':	'<=',
	'>=':	'>=',
	'==':	'==',
	'!=':	'!=',
	'<<':	'<<',
	'>>':	'>>',
}
INFIX_KEYS = INFIX_TRANS.keys()


DIALECT_NORMAL = 0
DIALECT_WRAP_MAIN = 1

class HAULWriter_js(HAULWriter):
	"Writes JavaScript code"
	
	# Translation of (internal) infix representation to language functions
	
	def __init__(self, streamOut, dialect=DIALECT_NORMAL):
		HAULWriter.__init__(self, streamOut)
		self.defaultExtension = 'js'
		self.dialect = dialect
		self.writeComment('Translated from HAUL3 to JavaScript on ' + str(datetime.datetime.now()) )
		
	def writeComment(self, t):
		"Add a comment to the file"
		self.streamOut.put('// ' + t + '\n')
		
	def writeIndent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def writeNamespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			self.writeIndent(indent)
			self.write('// Namespace "' + str(ns) + '"\n')
			for id in ns.ids:
				#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
				self.writeIndent(indent)
				self.write('//@' + str(id.kind) + ' ' + str(id.name) + ' ' + str(id.data_type) + '\n')
				
				if (id.name == 'this'):
					continue
				
				# Introduce variable (with const value)
				if (id.kind == K_VARIABLE):
					self.writeIndent(indent)
					self.write('var ' + str(id.name))
					if (id.data_value != None):
						self.write(' = ')
						self.writeValue(id.data_value)
					self.write(';\n')
		
	def writeFunc(self, f, indent=0, parentClassName=None):
		f.destination = self.streamOut.size	# Record offset in output stream
		
		# No need to declare arguments
		#self.writeNamespace(f.namespace, indent)	# Namespace outside function
		self.writeComment('Namespace skipped (function args)')
		
		name = f.id.name
		if (not parentClassName == None):
			if (name == A_INIT):
				name = parentClassName
			else:
				if name == '__repr__': name = 'toString'
				name = parentClassName + '.prototype.' + name
		
		self.writeIndent(indent)
		self.write('var ')
		self.write(name)
		self.write(' = function(')
		j = 0
		for i in xrange(len(f.args)):
			if (i == 0) and (not parentClassName == None):
				# skip first "self"
				continue
				
			if (j > 0): self.write(', ')
			#self.writeExpression(args[i])
			self.writeVar(f.args[i])
			j += 1
		self.write(') {\n')
		
		#self.writeNamespace(f.namespace, indent+1)	# Namespace inside function
		self.writeBlock(f.block, indent+1)
		
		self.writeIndent(indent)
		self.write('};\n')
		
	def writeModule(self, m, indent=0):
		m.destination = self.streamOut.size	# Record offset in output stream
		
		self.write('//### Module "' + m.name + '"\n')
		for im in m.imports:
			self.write('//import ')
			self.write(str(im))
			self.write('\n')
			
		#self.write('### Module namespace...\n')
		self.writeNamespace(m.namespace, indent)
		
		self.write('//### Classes...\n')
		for typ in m.classes:
			self.writeClass(typ, indent)
		
		self.write('//### Funcs...\n')
		for func in m.funcs:
			self.writeFunc(func, indent)
		
		self.write('//### Root Block (main function):\n')
		if (self.dialect == DIALECT_WRAP_MAIN):
			self.write('function main() {\n');
			if (m.block):
				self.writeBlock(m.block, indent+1)
			self.write('}\n');
		else:
			if (m.block):
				self.writeBlock(m.block, indent)
		
		
	
	def writeClass(self, c, indent=0):
		c.destination = self.streamOut.size	# Record offset in output stream
		
		self.writeIndent(indent)
		self.write('//# Class "' + c.id.name + '"\n')
		
		
		# Because we will mess up the namespace
		nsOld = c.namespace
		c.namespace = copy.copy(nsOld)
		
		if (c.namespace):
			# Fix self --> this
			selfId = c.namespace.get_id(A_SELF, kind=K_VARIABLE)
			if not selfId == None:
				selfId.name = 'this'
			
			#self.writeIndent(indent+1)
			#self.write('### Class namespace...\n')
			self.writeNamespace(c.namespace, indent+0)
		
		#@TODO: Initializer?
		for func in c.funcs:
			self.writeFunc(func, indent+0, parentClassName=c.id.name)
		
		# Restore sanity
		c.namespace = nsOld
		#self.write('# End-of-Type "' + t.id.name + '"\n')
		
	def writeBlock(self, b, indent=0):
		b.destination = self.streamOut.size	# Record offset in output stream
		#self.write("# Block \"" + b.name + "\"\n")
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				#self.writeIndent(indent)
				#self.write('### Block namespace...\n')
				self.writeNamespace(b.namespace, indent)
		
		for instr in b.instrs:
			#self.writeIndent(indent)
			self.writeInstr(instr, indent)
			#self.write(';')
			#self.write('\n')
			
	def writeInstr(self, i, indent):
		i.destination = self.streamOut.size	# Record offset in output stream
		
		#put(' writing instruction: ' + str(i))
		if (i.comment):
			self.writeIndent(indent)
			self.writeComment(i.comment)
			
		if (i.control):
			self.writeIndent(indent)
			self.writeControl(i.control, indent)
			self.write('\n')
		if (i.call):
			self.writeIndent(indent)
			self.writeCall(i.call)
			self.write(';\n')
		
	def writeControl(self, c, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0): self.write('else ')
				self.write('if (')
				
				self.writeExpression(c.exprs[j])
				self.write(') {\n')
				self.writeBlock(c.blocks[j], indent+1)
				self.writeIndent(indent)
				self.write('}')
				if (j < len(c.blocks)):
					self.write(' ')
				else:
					self.write('\n')
				j += 1
			
			if (j < len(c.blocks)):
				self.writeIndent(indent)
				self.write('else {\n')
				self.writeBlock(c.blocks[j], indent+1)
				self.writeIndent(indent)
				self.write('}\n')
		
		elif (c.controlType == C_FOR):
			self.write('for (')
			self.writeExpression(c.exprs[0])
			
			self.write(' in ')
			self.writeExpression(c.exprs[1])
			"""
			#@FIXME: Dirty hack to handle xrange (only simplest case)
			if (c.exprs[1].call.id.name == 'xrange'):
				self.write(' = 0; ')
				self.writeExpression(c.exprs[0])
				self.write(' < ')
				self.writeExpression(c.exprs[1].call.args[0])
				self.write('; ')
				self.writeExpression(c.exprs[0])
				self.write('++')
			"""
			
			self.write(') {\n')
			self.writeBlock(c.blocks[0], indent+1)
			self.writeIndent(indent)
			self.write('}\n')
		elif (c.controlType == C_WHILE):
			self.write('while (')
			self.writeExpression(c.exprs[0])
			self.write(') {\n')
			self.writeBlock(c.blocks[0], indent+1)
			self.writeIndent(indent)
			self.write('}\n')
		elif (c.controlType == C_RETURN):
			self.write('return')
			if (len(c.exprs) > 0):
				self.write(' ')
				self.writeExpression(c.exprs[0])
			self.write(';')
		elif (c.controlType == C_BREAK):
			self.write('break;')
		elif (c.controlType == C_CONTINUE):
			self.write('continue;')
		elif (c.controlType == C_RAISE):
			self.write('throw ')
			self.writeExpression(c.exprs[0])
			self.write(';')
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
			self.write('[')
			self.writeExpressionList(c.args, 1, level)
			self.write(']')
			
		elif i == I_ARRAY_CONSTRUCTOR.name:
			self.write('[')
			self.writeExpressionList(c.args, 0, level)
			self.write(']')
			
		elif i == I_DICT_CONSTRUCTOR.name:
			self.write('{')
			i = 0
			while (i < len(c.args)):
				if (i > 0): self.write(',\t')
				self.writeExpression(c.args[i], level=level)
				i += 1
				self.write(': ')
				self.writeExpression(c.args[i], level=level)
				i += 1
			self.write('}')
			
		elif i == I_OBJECT_CALL.name:
			self.writeExpression(c.args[0], 0)
			self.write('(')
			self.writeExpressionList(c.args, 1, 0)
			self.write(')')
			
		elif i == I_OBJECT_LOOKUP.name:
			self.writeExpression(c.args[0], 0)
			self.write('.')
			self.writeExpression(c.args[1], 0)
		
		elif (i in INFIX_KEYS):
			self.writeExpression(c.args[0], level)	# level-1
			
			#if (i in HAULWriter_py.INFIX):
			#	self.write(' ' + HAULWriter_py.INFIX[i] + ' ')
			#else:
			self.write(' ' + INFIX_TRANS[i] + ' ')
			
			self.writeExpression(c.args[1], level)	# level-1
		
		else:
			# Write a standard call
			
			# Check if it is a constructor call
			ns = c.id.namespace
			iid = ns.find_id(i)
			if (iid.kind == K_CLASS):
				# If ns.findId returns kind=K_FUNCTION it is a standard call, if it is K_CLASS it is an instantiation (call of constructor)!
				self.write('new ')
			
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
			self.write("'" + v.data + "'")	#@TODO: Escaping!
		else:
			self.write(str(v))	#.data
			
	def writeVar(self, v, isClass=False):
		self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')


