'''
This file is used as a library to access, grab, and store the
function names and docstrings of an input filename
'''

import ast, os

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

def grab_docstrings(filename):
	'''
	Function used to grab the function_definitions as well as their
	associated docstrings, and write them to an output textfile
	- function_docstrings.txt
	:param filename - of the input file to analyse
	:return - Boolean - Success/Fail - True/False - 1/0
	'''

	try:
		file_contents = open(filename,'r').read()
		module = ast.parse(file_contents)

		# Get function definitions
		function_definitions = [node for node in module.body if isinstance(node, ast.FunctionDef)]

		# Define string constants to be used in formatting output text
		separator_1 = '\n======'
		separator_2 = '\n------\n'
		newline = '\n'

		header_2 = '##'
		header_3 = '###'

		# Open output file function_docstrings.txt to write to
		output_filename = 'function_docstrings_' + os.path.splitext(filename)[0] + '.txt'
		output_file = open(output_filename,'w')

		file_header = 'Function Definitions and associated docstrings for: {} \n'.format(filename)
		output_file.write(file_header)

		sequence = []
		method_counter = 1

		for f in function_definitions:
			function_desc = ast.get_docstring(f)

			# Need to split up function_desc according to [docstirng, param_1, ..., return]
			details_list = function_desc.split(':param')

			if details[0] == '':
				# No real docstring, which is a problem
				default_string = 'Unfortunately there isn\'t any real explanation for this method... '\
							'yet\n'


			# Check if the return data was mentioned
			return_data = details_list[-1].split(':return:')
			if len(return_data) > 1:
				# We have a return mention, but is there a description?
				if len(return_data[-1]) > 0:
					# Empty return type explanation

				else:
			else:

			if function_desc is None:
				function_desc = '(empty)'

			function_title = '{} {}. {} {}'.format(header_3, method_counter, f.name, header_3)
			sequence = [function_title, function_desc, separator_2]
			
			# output_file.writelines(sequence)
			output_file.write(newline.join(sequence))
			
			method_counter += 1

		# Close the output_file
		output_file.close()

		return True

	except IOError:
		errmsg = 'Error opening or writing to file.\n'
		print(errmsg)

		return False
	except:
		errmsg = "Unexpected error"
		print(errmsg)
    	raise