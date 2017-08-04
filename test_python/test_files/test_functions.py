'''
Testing how python handles functions with optional arguments

'''

import os



def _check_target_func(target_function):
    """

    :param target_function:
    :return:
    """
    if isinstance(target_function, basestring):
        return target_function, (), {}
    try:
        len(target_function)
    except TypeError:
        return target_function, (), {}
    if len(target_function) == 3:
        return target_function
    elif len(target_function) == 1:
        target_function = (target_function[0], (), {})
    elif len(target_function) == 2:
        target_function = (target_function[0], target_function[1], {})
    else:
        raise RuntimeError('target_function tuple too long? - (name, (), {})')
    return target_function

'''
=============================================================================================
'''

def first_function(filename):
	# To simulate upload_to_ram
	# - Just going to print the filename for now (?)
	print(filename)

'''
=============================================================================================
'''

def second_function(param_one, param_two=2, param_three=False):
	# To simulate virtex_flash_reconfig

	print_str = str(param_one) + ' \t ' + str(param_two) + ' \t ' + str(param_three)
	print(print_str)

	return None