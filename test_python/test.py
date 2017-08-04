# 15/02/2017
# Testing FlashWriteChecksum Tally
# - Extracting Bitstream from a .fpg file

'''
Now added the following, just to compare the METHODS of calculating the FlashWriteChecksum:
- calc_checksum_old: using f.read(2)
- calc_checksum_new: using bitstream[index:index+2]
'''

import os
import zlib
import logging
import struct
import binascii

LOGGER = logging.getLogger(__name__)
logging.basicConfig()

# Method to replicate cRoach3SpartanFlashReconfigApp::SwappedByte
# - Swaps the bits in the byte so that the UFP file format matches raw data format
def swapped_byte(input_byte):
    swapped_byte = 0x0;

    if((input_byte & 0x01) == 0x01):
        swapped_byte = swapped_byte | 0x80
    if((input_byte & 0x02) == 0x02):
        swapped_byte = swapped_byte | 0x40
    if((input_byte & 0x04) == 0x04):
        swapped_byte = swapped_byte | 0x20
    if((input_byte & 0x08) == 0x08):
        swapped_byte = swapped_byte | 0x10
    if((input_byte & 0x10) == 0x10):
        swapped_byte = swapped_byte | 0x08
    if((input_byte & 0x20) == 0x20):
        swapped_byte = swapped_byte | 0x04
    if((input_byte & 0x40) == 0x40):
        swapped_byte = swapped_byte | 0x02
    if((input_byte & 0x80) == 0x80):
        swapped_byte = swapped_byte | 0x01

    return swapped_byte

'''
=====================================================================================================
'''

def printwords(bitstream_one, bitstream_two, numWords=100):
	size = len(bitstream_one)

	for i in range(numWords):
		print(str(hex(bitstream_one[i])) + " \t " + str(hex(bitstream_two[i])))

'''
=====================================================================================================
'''

# Effectively want to compare for length of the shorter bitstream
# - If the lengths are equal then that's cool too
def compare_bitstreams(bitstream_one, bitstream_two):
	size_one = len(bitstream_one)
	size_two = len(bitstream_two)

	limit = 0	# max index to print to, otherwise we'd get an 'index out of range'

	# Because Python doesn't support switch-case statements
	one_bigger = False
	two_bigger = False

	if(size_one > size_two):
		print(str(size_one) + " > " + str(size_two))
		one_bigger = True
	elif(size_one < size_two):
		print(str(size_one) + " < " + str(size_two))
		two_bigger = True
	#else size_one == size_two, both flags stay false

	if(one_bigger):
		limit = size_two

		for i in range(limit):
			# Don't really need to print, just iterate until we find a mismatch in words
			if(bitstream_one[i] != bitstream_two[i]):
				# Found a mismatch in words
				print "Found a word mismatch at index: ", i
				print(str(bitstream_one[i]) + " != " + str(bitstream_two[i]))
	elif(two_bigger):
		limit = size_one

		for i in range(limit):
			# Don't really need to print, just iterate until we find a mismatch in words
			if(bitstream_one[i] != bitstream_two[i]):
				# Found a mismatch in words
				print "Found a word mismatch at index: ", i
				print(str(bitstream_one[i]) + " != " + str(bitstream_two[i]))

	else:
		# Both lengths are equal
		for i in range(size_one):
			# Don't really need to print, just iterate until we find a mismatch in words
			if(bitstream_one[i] != bitstream_two[i]):
				# Found a mismatch in words
				print "Found a word mismatch at index: ", i
				print(str(bitstream_one[i]) + " != " + str(bitstream_two[i]))






'''
=====================================================================================================
'''

def calc_checksum_from_bpi16(filename):
	# Need to change endianness
	unpacker = '<H'
	FlashWriteChecksum = 0x0
	two_bytes = 0
	wordlist = []
	
	filesize = os.path.getsize(filename)
	num_padding_bytes = filesize % 8192
	padding = True

	if num_padding_bytes == 0:
		# No padding required
		padding = False
	

	with open(filename,'rb') as f:
		for i in range(0, filesize, 2):
			two_bytes = struct.unpack(unpacker, f.read(2))[0]
			wordlist.append(two_bytes)
			FlashWriteChecksum = (FlashWriteChecksum + two_bytes) & 0xffff

	if padding:
		for i in range(num_padding_bytes/2):
			FlashWriteChecksum += 0xffff

	FlashWriteChecksum &= 0xffff
	return FlashWriteChecksum, wordlist


'''
=====================================================================================================
'''

'''
99% of the time will take in a .bin file
:param filename, of the .bin file to calculate checksum
:return checksum (tally) | wordlist, List of 16-bit words in the .bin file
'''

def calc_checksum_old(filename):
    two_bytes = ''
    one_word = 0x0000
    checksum = 0x0000
    padding = True
    num_padding_bytes = 0

    wordlist = []

    filesize = os.path.getsize(filename)
    #filesize = len(filename)

    # Check for padding
    if (filesize % 8192) == 0:
        # No padding required
        padding = False
    else:
        #padding = True
        num_padding_bytes = 8192 - (filesize % 8192)

    packer = struct.Struct('!H')

    with open(filename, 'rb') as f:
        for i in range(filesize/2):
            two_bytes = f.read(2)#.rstrip()
            #one_word = struct.unpack('!H', two_bytes)[0]
            one_word = packer.unpack(two_bytes)[0]
            wordlist.append(one_word)
            #checksum += one_word
            checksum = (checksum + one_word) & 0xffff

    if padding:
        print "PADDING"
        for i in range(num_padding_bytes/2):
        	checksum += 0xffff
            #checksum = (checksum + 0xffff) & 0xffff

    # Last thing to do, make sure it is a 16-bit word
    checksum &= 0xffff

    return checksum, wordlist

'''
=====================================================================================================
'''

def calc_checksum_new(filename):
    two_bytes = ''
    one_word = 0x0000
    checksum = 0x0000
    padding = True
    num_padding_bytes = 0

    wordlist = []

    # First, need to extract_bitstream
    bitstream = extract_bitstream(filename)
    filesize = len(bitstream)

    # Check for padding
    if (filesize % 8192) == 0:
        # No padding required
        padding = False
    else:
        #padding = True
        num_padding_bytes = 8192 - (filesize % 8192)


    for i in range(0, filesize, 2):
        two_bytes = bitstream[i:i+2]  # This is just getting a substring, need to convert to hex
        one_word = struct.unpack('!H', two_bytes)[0]
        wordlist.append(one_word)
        #checksum += one_word
        checksum = (checksum + one_word) & 0xffff

    if padding:
        print "PADDING"
        for i in range(num_padding_bytes/2):
            #checksum += 0xffff
            checksum = (checksum + 0xffff) #& 0xffff


    # Last thing to do, make sure it is a 16-bit word
    checksum &= 0xffff
    
    return checksum, wordlist

'''
=====================================================================================================
'''

def simult_checksum_calc(bitstream_one, bitstream_two):	
	
	if(len(bitstream_one) != len(bitstream_two)):
		print "NOPE"
		return 0, 0	

	filesize = len(bitstream_one)  # should be the same for both Bitstreams

	padding = True
	checksum_one = 0#0x0000
	checksum_two = 0#0x0000

	original_checksum = 43665

	num_padding_bytes = 0

	if (filesize % 4096) == 0:  # Using 4096 now and not 8192 because dealing with Words
		# No padding required
		padding = False
	else:
		num_padding_bytes = filesize % 4096
		num_padding_bytes *= 2


	for i in range(filesize):
		checksum_one = (checksum_one + bitstream_one[i]) & 0xffff
		checksum_two = (checksum_two + bitstream_two[i]) & 0xffff

		'''
		if(checksum_one == original_checksum or checksum_two == original_checksum):
			print "Reached value at index: ", i
			print(str(hex(bitstream_one[i])) + " \t " + str(hex(bitstream_two[i])))
			return checksum_one, checksum_two
		'''

		if(checksum_one != checksum_two):
			#temp_one = str(bitstream_one[i])
			#temp_two = str(bitstream_two[i])

			print("CHECKSUMS DEVIATED at index: ", i)
			print(str(hex(bitstream_one[i])) + " != " + str(hex(bitstream_two[i])))
			print(str(checksum_one) + " != " + str(checksum_two))

	
	if padding:		
		print "PADDING"

		for i in range(num_padding_bytes):
			checksum_one = (checksum_one + 0xffff) & 0xffff
			checksum_two = (checksum_two + 0xffff) & 0xffff

			'''
			if(checksum_one == original_checksum or checksum_two == original_checksum):
				print "Reached value at index: ", i
				print(str(hex(bitstream_one[i])) + " \t " + str(hex(bitstream_two[i])))
				return checksum_one, checksum_two
			'''

			if(checksum_one != checksum_two):
				#temp_one = str(bitstream_one[i])
				#temp_two = str(bitstream_two[i])

				print("CHECKSUMS DEVIATED at index: ", i)
				print(str(bitstream_one[i]) + " != " + str(bitstream_two[i]))
				print(str(checksum_one) + " != " + str(checksum_two))

	# What to do after that?

	return checksum_one, checksum_two

'''
=====================================================================================================
'''


def extract_bitstream(filename, extract_to_disk=False):
	# get design name
    name = os.path.splitext(filename)[0]

    fpg_file = open(filename, 'r')
    fpg_contents = fpg_file.read()
    fpg_file.close()

    # scan for the end of the fpg header
    end_of_header = fpg_contents.find('?quit')

    assert (end_of_header != -1), 'Not a valid fpg file!'

    bitstream_start = fpg_contents.find('?quit') + len('?quit') + 1

    # exract the bitstream portion of the file
    bitstream = fpg_contents[bitstream_start:]

    # check if bitstream is compressed using magic number for gzip
    if bitstream.startswith('\x1f\x8b\x08'):
        # decompress
        bitstream = zlib.decompress(bitstream, 16 + zlib.MAX_WBITS)

    # write binary file to disk?
    if extract_to_disk:

        # write to bin file
        bin_file = open(name + '.bin', 'wb')
        bin_file.write(bitstream)
        bin_file.close()
        LOGGER.info('Output binary filename: {}'.format(name + '.bin'))

    return bitstream


'''
=====================================================================================================
'''


def check_bitstream(bitstream, binfile=False):	
    if binfile:
        # Open the file
        filecontents = open(bitstream, 'rb')
        contents = filecontents.read()
        print(len(contents))
        filecontents.close()
    else:
        contents = bitstream

    valid_string = '\xff\xff\x00\x00\x00\xdd\x88\x44\x00\x22\xff\xff'

    #bpi16_string = '\xff\xff\x00\x00\xdd\x00\x44\x88\x22\x00\xff'
    bpi16_string = '\xff\xff\x00\x00\xdd\x00D\x88"\x00\xff\xff'

    # check if the valid header substring exists
    if contents.find(valid_string) == 30:
        return True
    else:
        read_header = contents[30:42]
        if read_header == bpi16_string:
            # BPI16 .bin file input
            LOGGER.error("A BPIx16 .bin file has been input")
        else:
            LOGGER.error(
                "Incompatible bitstream detected.\nExpected header: {}"
                "\nRead header: {}".format(repr(valid_string), repr(read_header)))
        return False

'''
=====================================================================================================
'''

def convert_hex_to_bin(hex_file, extract_to_disk=False, return_num_words=False):
    # TODO: error checking/handling
    """
    Converts a hex file to a bin file with little endianness for programming to sdram, also pads
    to 4096 word boundary
    :param hex_file: file name of hex file to be converted
    :param extract_to_disk: flag whether or not bin file is extracted to harddisk
    :return: bitsream
    """

    f_in = open(hex_file, 'rb')  # read from
    bitstream = ''  # blank string for bitstream

    packer = struct.Struct(
        "<H")  # for packing fpga image data into binary string use little endian

    size = os.path.getsize(hex_file)

    # group 4 chars from the hex file to create 1 word in the bin file
    # see how many packets of 4096 words we can create without padding
    # 16384 = 4096 * 4 (since each word consists of 4 chars from the hex file)
    # each char = 1 nibble = 4 bits
    for i in range(size / 16384):
        # create packets of 4096 words
        for j in range(4096):
            word = f_in.read(4)
            bitstream += packer.pack(int(word, 16))  # pack into binary string

    # entire file not processed yet. Remaining data needs to be padded to a 4096 word boundary
    # in the hex file this equates to 4096*4 bytes

    # get the last packet (required padding)
    last_pkt = f_in.read().rstrip()  # strip eof '\r\n' before padding
    num_words = len(bitstream) + len(last_pkt)
    print(str(len(last_pkt)))

    last_pkt += 'f' * (16384 - len(last_pkt))  # pad to 4096 word boundary

    # close the file
    f_in.close()

    # handle last data chunk
    for i in range(0, 16384, 4):
        word = last_pkt[i:i + 4]  # grab 4 chars to form word
        bitstream += packer.pack(int(word, 16))  # pack into binary string

    if extract_to_disk:
        out_file_name = os.path.splitext(hex_file)[0] + '.bin'
        f_out = open(out_file_name, 'wb')  # write to
        f_out.write(bitstream)
        f_out.close()
        LOGGER.info('Output binary filename: {}'.format(out_file_name))

    if return_num_words:
    	return bitstream, num_words
    else:
    	return bitstream


def convert_hex_to_bin_new(hexfile_contents, extract_to_disk=False):
    # TODO: error checking/handling
    """
    Converts a hex file to a bin file with little endianness for programming to sdram, also pads
    to 4096 word boundary
    :param hexfile_contents: The actual contents of the hexfile
    :param extract_to_disk: flag whether or not bin file is extracted to harddisk
    :return: bitsream
    """
    
    bitstream = ''  # blank string for bitstream

    packer = struct.Struct(
        "<H")  # for packing fpga image data into binary string use little endian

    size = len(hexfile_contents)
    num_word_blocks = size / 16384

    # group 4 chars from the hex file to create 1 word in the bin file
    # see how many packets of 4096 words we can create without padding
    # 16384 = 4096 * 4 (since each word consists of 4 chars from the hex file)
    # each char = 1 nibble = 4 bits
    block_counter = 1
    for i in range(num_word_blocks):
        # create packets of 4096 words
        temp_counter = i * block_counter
        for j in range(4096):
            word = hexfile_contents[temp_counter:temp_counter+4]
            bitstream += packer.pack(int(word, 16))  # pack into binary string
        block_counter += 1

    # entire file not processed yet. Remaining data needs to be padded to a 4096 word boundary
    # in the hex file this equates to 4096*4 bytes

    # get the last packet (required padding)

    last_pkt = bitstream[-(size - (num_word_blocks * 16384)):]
    last_pkt = last_pkt.rstrip()  # strip eof '\r\n' before padding
    #last_pkt += 'f' * (16384 - len(last_pkt))  # pad to 4096 word boundary

    # handle last data chunk
    for i in range(0, len(last_pkt), 4):
        word = last_pkt[i:i + 4]  # grab 4 chars to form word
        bitstream += packer.pack(int(binascii.hexlify(word), 16))  # pack into binary string
        #bitstream += struct.pack('<H', int(word,16))

    if extract_to_disk:
        out_file_name = os.path.splitext(hex_file)[0] + '.bin'
        f_out = open(out_file_name, 'wb')  # write to
        f_out.write(bitstream)
        f_out.close()
        LOGGER.info('Output binary filename: {}'.format(out_file_name))

    return bitstream

'''
=====================================================================================================
'''

def compare_hex_to_bin(hexfile_contents, binfile_contents):
	'''
	This will effectively be VerifyWords(), from VirtexFlashReconfig
	Need a separate function because we will change endianness of Hexfile Word
	and compare on the fly

	** Need to find out what's up with the differences in Bitstream lengths!
	   -> 
	'''


'''
=====================================================================================================
'''