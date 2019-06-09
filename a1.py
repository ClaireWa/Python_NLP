# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 16:31:58 2018

@author: luke_
"""

#Here are some libraries you're likely to use. You might want/need others as well.
import re
import sys
from random import random
from math import log
from collections import defaultdict
import string as str

tri_counts=defaultdict(int) #counts of all trigrams in input

testline = 'This is a "test line" and it has 4 stránge charactó:rs in it$'
#this function currently does nothing.
def preprocess_line(line):
    
    good_chars = str.ascii_letters + '.' + str.digits + ' '
    output = line

    for i in range(len(line)):
        if line[i] not in good_chars:
            output = output.replace(line[i],'')
            #print(line[i] + ' ' + 'replaced')
            #print(output)
        
        if line[i] in str.digits:
            
            output = output.replace(line[i],'0')
            #print(line[i] + ' ' + 'changed to 0')
            #print(output)
            
    output = output.lower()
    return output

print(testline)
print('Processing...')
print(preprocess_line(testline))

'''
    START
        OF 
            OUR 
                TERRIBLE 
                        CODE
'''
'''
filename = "a1-training_data/training.en"
eng_test = open(filename, 'r')
eng_test_lines = eng_test.readlines()

#print(eng_test_lines)

for i in range(len(eng_test_lines)):
    print('Line ' + str(i+1) + ': ' + eng_test_lines[i])
'''
























'''
#here we make sure the user provides a training filename when
#calling this program, otherwise exit with a usage error.
if len(sys.argv) != 2:
    print("Usage: ", sys.argv[0], "<training_file>")
    sys.exit(1)

infile = sys.argv[1] #get input argument: the training file

#This bit of code gives an example of how you might extract trigram counts
#from a file, line by line. If you plan to use or modify this code,
#please ensure you understand what it is actually doing, especially at the
#beginning and end of each line. Depending on how you write the rest of
#your program, you may need to modify this code.
with open(infile) as f:
    for line in f:
        line = preprocess_line(line) #doesn't do anything yet.
        for j in range(len(line)-(3)):
            trigram = line[j:j+3]
            tri_counts[trigram] += 1

#Some example code that prints out the counts. For small input files
#the counts are easy to look at but for larger files you can redirect
#to an output file (see Lab 1).
print("Trigram counts in ", infile, ", sorted alphabetically:")
for trigram in sorted(tri_counts.keys()):
    print(trigram, ": ", tri_counts[trigram])
print("Trigram counts in ", infile, ", sorted numerically:")
for tri_count in sorted(tri_counts.items(), key=lambda x:x[1], reverse = True):
    print(tri_count[0], ": ", str(tri_count[1]))
    '''