'''
This is a new python file created to test the 'ast' library
that will be used to extract docstrings from .py files
'''

#define CONSTANT_VALUE 1

def first_function():
	'''
	This is the first function in the test_docstrings.py file.
	The function has no parameters and will return True.
	'''

	return True

def second_function(first_parameter):
	'''
	This is the second function in the test_docstrings.py file.
	The function takes in one parameter, expected to be an integer,
	adds 1 to it and returns the answer.
	:param first_parameter - integer value
	:return: result = first_parameter + 1
	'''

	return first_parameter + 1

def third_function(something):

	return False