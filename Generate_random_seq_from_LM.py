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


filename = 'model-br.en'
en_test = open(filename, 'r')
en_test_lines = en_test.readlines()
#print(en_test_lines)

prob_dict = {}
for p in en_test_lines:

    if p[0:2] not in prob_dict.keys():
        prob_dict[p[0:2]] = defaultdict(float)
    prob_dict[p[0:2]][p[2]] = float(p[4:-1])
    
    
def generate_random_sequence(distribution, N):
    ''' generate_random_sequence takes a distribution (represented as a
    dictionary of outcome-probability pairs) and a number of samples N
    and returns a list of N samples from the distribution.  
    This is a modified version of a sequence generator by fraxel on
    StackOverflow:
    http://stackoverflow.com/questions/11373192/generating-discrete-random-variables-with-specified-weights-using-scipy-or-numpy
    '''
    #As noted elsewhere, the ordering of keys and values accessed from
    #a dictionary is arbitrary. However we are guaranteed that keys()
    #and values() will use the *same* ordering, as long as we have not
    #modified the dictionary in between calling them.
    outcomes = np.array(list(distribution.keys()))
    probs = np.array(list(distribution.values()))
    #make an array with the cumulative sum of probabilities at each
    #index (ie prob. mass func)
    bins = np.cumsum(probs)
    #create N random #s from 0-1
    #digitize tells us which bin they fall into.
    #return the sequence of outcomes associated with that sequence of bins
    #(we convert it from array back to list first)
    return list(outcomes[np.digitize(random_sample(N), bins)])

generated_output = '##'
while len(generated_output) < 302:
    if generated_output[-1] == '#':
        if generated_output[-2] == '#':
            generated_output = generated_output + generate_random_sequence(prob_dict[generated_output[-2:]],1)[0]
            continue
        generated_output += '#'
        continue
    generated_output += generate_random_sequence(prob_dict[generated_output[-2:]],1)[0]

print(generated_output)
