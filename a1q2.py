# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 17:25:27 2018

@author: luke_
"""
filename = "model-br.en"
eng_test = open(filename, 'r')
eng_test_lines = eng_test.readlines()

for x in range(10):
    print(len(eng_test_lines[x]))
    
print(len(eng_test_lines))
    
our_model = {
        'trigram' : [],
        'prob' : []}

#for x in range(len(eng_test_lines)):
#    our_model['trigram'].append(eng_test_lines[x][0:3])
#    our_model['prob'].append(eng_test_lines[x][4:13])
#    print('trigram:', our_model['trigram'][x],'\tprob:', our_model['prob'][x])

#print(our_model['prob'][1])
#print(float(our_model['prob'][1]))