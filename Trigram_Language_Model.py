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


filename = 'training.es'
en_test = open(filename, 'r')
en_test_lines = en_test.readlines()

file1 = 'test'
test = open(file1, 'r')
test_lines = test.readlines()

tri_counts=defaultdict(int) #counts of all trigrams in input
bi_counts = defaultdict(int) #counts of all bigrams in input

#The first for loop in our preprocess_line function removes all 
#characters that are not in [A-Za-z0-9. ]
#The second for loop replaces all digits with 0
#all remaining characters changed to lowercase
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
for x in range(len(en_test_lines)):
    processed_lines.append('$$'+preprocess_line(en_test_lines[x])+'$')

processed_test_lines = []
for x in range(len(test_lines)):
    processed_test_lines.append('$$'+preprocess_line(test_lines[x])+'$')



#This for loop calculates all the trigrams in the file, and their counts
for y in range(len(processed_lines)):
    for j in range(len(processed_lines[y])-(2)):
        trigram = processed_lines[y][j:j+3]
        tri_counts[trigram] += 1

#This for loop calculates all the bigrams in the file, and their counts
for y_ in range(len(processed_lines)):
    for j_ in range(len(processed_lines[y_])-(2)):
        bigram = processed_lines[y_][j_:j_+2]
        bi_counts[bigram] += 1

#all the characters that are allowed (used to create all POSSIBLE trigrams)
actual_good_chars = str.ascii_lowercase + '. 0$'

#These nested loops create all possible trigrams
#We have excluded any of the form '_$_' or '_$$'
all_tris = []
for a in range(len(actual_good_chars)):
    for b in range(len(actual_good_chars)):
        for c in range(len(actual_good_chars)):
            if (c == 29) and ((a != 29) and (b != 29)):
                continue
            if ((c==29) and (b==29)):
                continue
            
            all_tris.append(actual_good_chars[a] + actual_good_chars[c] + actual_good_chars[b])

#Create all possible bigrams, excluding any of the form '_$'
#Any of this form will have a probability of the next char being $ = 1
#This is set later on
all_bis = []
for a_ in range(len(actual_good_chars)):
    for b_ in range(len(actual_good_chars)-1):
        all_bis.append(actual_good_chars[a_] + actual_good_chars[b_])

#Add '$$' bigram - used to predict first letter in a line
all_bis.append('$$')

#Alpha for add-alpha smoothing
add_alpha = 0.7

#Dict which contains each trigram, its count in the text file after processing
#and the count of the bigram that it begins with
our_trigram_dict = {
                    'trigram': [],
                    'count': [],
                    'bigram_count': []}

#Dictionary assignment creates Shallow copy by default
f_tri_counts = copy.deepcopy(tri_counts)
f_bi_counts = copy.deepcopy(bi_counts)

#adds the trigram, its count and the count of the bigram to the dictionary created above
for t in range(len(all_tris)):
    our_trigram_dict['trigram'].append(all_tris[t])
    our_trigram_dict['count'].append(tri_counts[all_tris[t]])
    our_trigram_dict['bigram_count'].append(bi_counts[all_tris[t][:2]])

#function to calculate probability of the next character given the most recent 
#bigram
#with add alpha smoothing to estimate probabilities
def calc_prob(input_dict, alpha, v):
    estimates = {
                     'bigram': [],
                     'next_char': [],
                     'p': []}
    
    for i in range(len(input_dict['trigram'])):
        estimates['bigram'].append(input_dict['trigram'][i][:2])
        estimates['next_char'].append(input_dict['trigram'][i][-1])
        estimates['p'].append((input_dict['count'][i] + alpha)/(input_dict['bigram_count'][i] + (alpha*v)))
    return estimates

vocab_size = len(actual_good_chars)
est = calc_prob(our_trigram_dict, add_alpha, vocab_size)

#Add the probabilities of bigrams of the form '_$' being followed
#by another '$' (this creates the start of line marker '$$' to allow another line to be generated)
add_eol = {
               'bigram': [],
               'next_char': [],
               'p': []}

for x in range(len(actual_good_chars)-1):
    add_eol['bigram'].append(actual_good_chars[x]+'$')
    add_eol['next_char'].append('$')
    add_eol['p'].append(1)

for x in range(len(add_eol['bigram'])):
    est['bigram'].append(add_eol['bigram'][x])
    est['next_char'].append(add_eol['next_char'][x])
    est['p'].append(add_eol['p'][x])

#Write our model probabilities to the file 'a1q3.txt'
file = open('a1q3.txt', 'w')
for x in range(len(est['bigram'])):
    file.write(est['bigram'][x]+est['next_char'][x]+'\t'+'{}\n'.format(float(est['p'][x])))

#creates dictionary of sub dictionaries of: each bigram, the next character 
#possibilities (to make a trigram) and their probabilities of occurring 
new_prob_dict = {}
for bi in all_bis:
    sub_dict = defaultdict(float)
    for x in range(len(est['bigram'])):
        if est['bigram'][x] == bi:
            sub_dict[est['next_char'][x]] = est['p'][x]
    new_prob_dict[bi] = sub_dict

for x in range(len(actual_good_chars)-1):
    new_prob_dict[actual_good_chars[x]+'$'] = {'$': float(1)}

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

generated_output = '$$'
while len(generated_output) < 302:
    generated_output = generated_output + generate_random_sequence(new_prob_dict[generated_output[-2:]],1)[0]
print(generated_output)


def compute_perp(lines, probs):
    prob_list = []
    for y in range(len(lines)):
        for x in range(2, len(lines[y])):
    #        print(y,x)
            prob_list.append(probs[lines[y][x-2:x]][lines[y][x]])    
    prob_list = np.array(prob_list)
    
    log_probs = - np.log2(prob_list)
    avg_logs = np.mean(log_probs)
    perp = 2**avg_logs
    return perp

print(filename, 'model perplexity:', compute_perp(processed_test_lines, new_prob_dict))








# =============================================================================
# #here we make sure the user provides a training filename when
# #calling this program, otherwise exit with a usage error.
# if len(sys.argv) != 2:
#     print("Usage: ", sys.argv[0], "training.en")
#     sys.exit(1)
# 
# infile = sys.argv[1] #get input argument: the training file
# 
# 
# #Some example code that prints out the counts. For small input files
# #the counts are easy to look at but for larger files you can redirect
# #to an output file (see Lab 1).
# print("Trigram counts in ", infile, ", sorted alphabetically:")
# for trigram in sorted(tri_counts.keys()):
#     print(trigram, ": ", tri_counts[trigram])
# print("Trigram counts in ", infile, ", sorted numerically:")
# for tri_count in sorted(tri_counts.items(), key=lambda x:x[1], reverse = True):
#     print(tri_count[0], ": ", str(tri_count[1]))
# =============================================================================
