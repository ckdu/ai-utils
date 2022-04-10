# This code is mostly not mine, I forked it
# I used it to learn how to run a basic neural network for text classification

import nltk
from nltk.stem.lancaster import LancasterStemmer
import os
import json
import datetime
import numpy as np
import time
import hickle as hkl
from numba import jit

stemmer = LancasterStemmer()

################################################

training_data = []
allRanks = []

for hklFileName in os.listdir('output'):
    if hklFileName.split(".")[1] == "hkl" and not "useless" in hklFileName:
        os.chdir('output')
        allRanks.append(hkl.load(hklFileName).tolist())
        os.chdir('../')

os.chdir('../')

for oneRank in allRanks:
    i = 0
    for tData in oneRank:
        if i < 30:
            training_data.append(tData)
        i += 1

print ("%s users in training data" % len(training_data))

################################################

words = []
ranks = []
documents = []
ignore_words = ['?']
for pattern in training_data:
    w = nltk.word_tokenize(pattern['messages'])
    words.extend(w)
    documents.append((w, pattern['rank']))
    if pattern['rank'] not in ranks:
        ranks.append(pattern['rank'])

words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
words = list(set(words))

ranks = list(set(ranks))

print (len(documents), "documents")
print (len(ranks), "ranks", ranks)
print (len(words), "unique stemmed words", words)

################################################

training = []
output = []

output_empty = [0] * len(ranks)

for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    training.append(bag)
    output_row = list(output_empty)
    output_row[ranks.index(doc[1])] = 1
    output.append(output_row)

i = 0
w = documents[i][0]
print ([stemmer.stem(word.lower()) for word in w])
print (training[i])
print (output[i])

################################################

def sigmoid(x):
    output = 1/(1+np.exp(-x))
    return output

def sigmoid_output_to_derivative(output):
    return output*(1-output)
 
def clean_up_messages(messages):
    messages_words = nltk.word_tokenize(messages)
    messages_words = [stemmer.stem(word.lower()) for word in messages_words]
    return messages_words

def bow(messages, words, show_details=False):
    messages_words = clean_up_messages(messages)
    bag = [0]*len(words)  
    for s in messages_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)

    return(np.array(bag))

def think(messages, show_details=False):
    x = bow(messages.lower(), words, show_details)
    if show_details:
        print ("messages:", messages, "\n bow:", x)
    l0 = x
    l1 = sigmoid(np.dot(l0, synapse_0))
    l2 = sigmoid(np.dot(l1, synapse_1))
    return l2

################################################

def train(X, y, hidden_neurons=10, alpha=1, epochs=50000, dropout=False, dropout_percent=0.5):

    print ("Training with %s neurons, alpha:%s, dropout:%s %s" % (hidden_neurons, str(alpha), dropout, dropout_percent if dropout else '') )
    print ("Input matrix: %sx%s    Output matrix: %sx%s" % (len(X),len(X[0]),1, len(ranks)) )
    np.random.seed(1)

    last_mean_error = 1
    synapse_0 = 2*np.random.random((len(X[0]), hidden_neurons)) - 1
    synapse_1 = 2*np.random.random((hidden_neurons, len(ranks))) - 1

    prev_synapse_0_weight_update = np.zeros_like(synapse_0)
    prev_synapse_1_weight_update = np.zeros_like(synapse_1)

    synapse_0_direction_count = np.zeros_like(synapse_0)
    synapse_1_direction_count = np.zeros_like(synapse_1)

    for j in iter(range(epochs+1)):

        layer_0 = X
        layer_1 = sigmoid(np.dot(layer_0, synapse_0))
                
        if(dropout):
            layer_1 *= np.random.binomial([np.ones((len(X),hidden_neurons))],1-dropout_percent)[0] * (1.0/(1-dropout_percent))

        layer_2 = sigmoid(np.dot(layer_1, synapse_1))

        layer_2_error = y - layer_2

        if (j% 10000) == 0 and j > 5000:
            if np.mean(np.abs(layer_2_error)) < last_mean_error:
                print ("delta after "+str(j)+" iterations:" + str(np.mean(np.abs(layer_2_error))) )
                last_mean_error = np.mean(np.abs(layer_2_error))
            else:
                print ("break:", np.mean(np.abs(layer_2_error)), ">", last_mean_error )
                break
                
        layer_2_delta = layer_2_error * sigmoid_output_to_derivative(layer_2)

        layer_1_error = layer_2_delta.dot(synapse_1.T)

        layer_1_delta = layer_1_error * sigmoid_output_to_derivative(layer_1)
        
        synapse_1_weight_update = (layer_1.T.dot(layer_2_delta))
        synapse_0_weight_update = (layer_0.T.dot(layer_1_delta))
        
        if(j > 0):
            synapse_0_direction_count += np.abs(((synapse_0_weight_update > 0)+0) - ((prev_synapse_0_weight_update > 0) + 0))
            synapse_1_direction_count += np.abs(((synapse_1_weight_update > 0)+0) - ((prev_synapse_1_weight_update > 0) + 0))        
        
        synapse_1 += alpha * synapse_1_weight_update
        synapse_0 += alpha * synapse_0_weight_update
        
        prev_synapse_0_weight_update = synapse_0_weight_update
        prev_synapse_1_weight_update = synapse_1_weight_update
    
    now = datetime.datetime.now()

    synapse = {'synapse0': synapse_0.tolist(), 'synapse1': synapse_1.tolist(),
               'datetime': now.strftime("%Y-%m-%d %H:%M"),
               'words': words,
               'ranks': ranks
              }
    synapse_file = "synapses.json"

    with open(synapse_file, 'w') as outfile:
        json.dump(synapse, outfile, indent=4, sort_keys=True)
    print ("saved synapses to:", synapse_file)

################################################

X = np.array(training)
y = np.array(output)

start_time = time.time()

train(X, y, hidden_neurons=180, alpha=0.1, epochs=100, dropout=True, dropout_percent=0.25)

elapsed_time = time.time() - start_time
print ("processing time:", elapsed_time, "seconds")

################################################

ERROR_THRESHOLD = 0
synapse_file = 'synapses.json' 
with open(synapse_file) as data_file: 
    synapse = json.load(data_file) 
    synapse_0 = np.asarray(synapse['synapse0']) 
    synapse_1 = np.asarray(synapse['synapse1'])

def classify(messages, show_details=False):
    results = think(messages, show_details)

    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD ] 
    results.sort(key=lambda x: x[1], reverse=True) 
    return_results =[[ranks[r[0]],r[1]] for r in results]
    print ("%s \n classification: %s" % (messages, return_results))
    return return_results

while True:
    messagesInp = input("Enter messages: ")
    classify(messagesInp)

#classify("ex", show_details=True)
