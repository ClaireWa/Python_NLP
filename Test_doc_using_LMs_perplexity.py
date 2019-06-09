# -*- coding: utf-8 -*-


import re
import sys
from random import random
from math import log
from collections import defaultdict
import string as str
import copy
import numpy as np
from numpy.random import random_sample


file1 = 'training.en'
test = open(file1, 'r')
test_lines = test.readlines()

#print(test_lines)

file2 = 'model-br.en'
model = open(file2, 'r')
model_lines = model.readlines()
#print(en_test_lines)





def preprocess_line(line):
    good_chars = str.ascii_letters + '.' + str.digits + ' '
    output = line
    for i in range(len(line)):
        if line[i] not in good_chars:
            output = output.replace(line[i],'')

        if line[i] in str.digits:        
            output = output.replace(line[i],'0')
    output = output.lower()
    return output

#We call our preprocess_line function on the file we read in,
#and then we add '$$' to the beginning of each line, and '$' to the end
processed_lines = []
for x in range(len(test_lines)):
    processed_lines.append('##'+preprocess_line(test_lines[x])+'#')

prob_dict = {}
for p in model_lines:
    if p[0:2] not in prob_dict.keys():
        prob_dict[p[0:2]] = defaultdict(float)
    prob_dict[p[0:2]][p[2]] = float(p[4:-1])

def compute_perp(lines, probs):
    prob_list = []
    for y in range(len(lines)):
        for x in range(2, len(lines[y])):
    #        print(y,x)
            prob_list.append(probs[lines[y][x-2:x]][lines[y][x]])    
    prob_list = np.array(prob_list)
    
    log_probs = (-1)*np.log2(prob_list)
    avg_logs = np.mean(log_probs)
    perp = 2**avg_logs
    return perp

print('model-br.en perplexity:',compute_perp(processed_lines, prob_dict))

for c in range(len(prob_list)):
    if prob_list[c] == 0:
        print(c,prob_list[c])
