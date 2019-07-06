#1.

import os
import re
import nltk
import string
import numpy as np
import pandas as pd
import networkx as nx
from scipy import sparse
from nltk.stem import PorterStemmer 
from read_write_create import *
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer


def convert_text_to_sentences(text):
    return nltk.sent_tokenize(text)


def select_adj_noun(POS_tags):
    
    adj_ex = re.compile("JJ.?")
    noun_ex = re.compile("NN.?.?")
    
    selected_words = []
    for word, tag in POS_tags:
        if adj_ex.match(tag) or noun_ex.match(tag):
            selected_words.append(word)
    
    return selected_words


def create_graph_with_adjmat(adjacency_matrix, labels):
    
    num_of_nodes = len(adjacency_matrix)
    
    rows, cols = np.where(adjacency_matrix > 0)
    edges = zip(rows.tolist(), cols.tolist())
    
    nodes_with_labels = []
    for i in range(num_of_nodes):
        tup = (i,dict(labels=labels[i]))
        nodes_with_labels.append(tup)
    
    wted_edges = []
    for edge in edges:
        wt = adjacency_matrix[edge[0],edge[1]]
        tup = (edge[0],edge[1],wt)
        wted_edges.append(tup)
    
    gr = nx.Graph()
    gr.add_nodes_from(nodes_with_labels)
    gr.add_weighted_edges_from(wted_edges)
    
    ## to print graph
    #nx.draw(gr, node_size=500, labels=labels, with_labels=True)
    #plt.show()
    
    return gr

def create_graph_with_edgelist():
    return 1

global cwd, path, data_path

cwd = os.getcwd()
path = cwd
data_path = cwd + "/data/"
position_path = cwd + "/positions/"

create_folder(cwd,"graphs")
create_folder(cwd,"edgelists")

ps = PorterStemmer()
stopwords = read_list_from_file(path, "stopwords.txt")
roman_num_ex = re.compile("\\b[i|v|x|l|c|d|m]{1,3}\\b")
numbers_ex = re.compile("[0-9]+(-[0-9]+)?")
punctuation_ex = re.compile("[^a-z ]")
newline_ex = re.compile("\n")

print("Create-graph-sCake")
for every_file in (os.listdir(data_path)):
    
    file_name = every_file[:-4]
    print(every_file)
    
    with open(cwd+"/positions/"+file_name+".pkl", 'rb') as f:
        df_pos = pd.read_pickle(f, compression=None)
    
    text = read_text_from_file(data_path,every_file)
    text = re.sub(newline_ex, ' ', text)
    
    ## creating corpus s.t. two sentences are considered one document.
    sen = convert_text_to_sentences(text)
    
    doc = list()
    if len(sen) < 2:
        doc.append(sen[0])
    else:
        for i in range(len(sen)-1):
            two_sen = sen[i] + ". " + sen[i+1]
            doc.append(two_sen)
            
    ## cleaning the corpus
    corpus = []
    for sen in doc:
        new_sen = sen.strip()
        new_sen = new_sen.lower()
        new_sen = re.sub(numbers_ex, '', new_sen)
        new_sen = re.sub(punctuation_ex, '', new_sen)
        new_sen = re.sub(roman_num_ex, '', new_sen)
        sen_words = nltk.word_tokenize(new_sen)
        
        sen_words = [i for i in sen_words if i not in stopwords]       
        sen_words = [ps.stem(w) for w in sen_words]
        new_sen = ' '.join(sen_words)
        corpus.append(new_sen)
        
    words = df_pos["words"]
    selected_words = sorted(list(set(words)))
    
    ##create document-term matrix
    vectorizer = CountVectorizer(binary=True)
    X = vectorizer.fit_transform(corpus)
    features = vectorizer.get_feature_names()
    
    #only selected_words used
    ind_dict = dict((k,i) for i,k in enumerate(features))
    ins = list((set(ind_dict))&(set(selected_words)))
    indices = [ ind_dict[x] for x in ins ]
    
    dtm = (X[:,indices]).todense()
    
    ##create term-term matrix
    ttm = np.transpose(dtm)*dtm
    np.fill_diagonal(ttm, 0)
    
    df = pd.DataFrame(data=ttm)
    df.columns = ins
    
    #print(df)
    df.to_pickle(cwd+"/graphs/"+every_file[:-4]+".pkl")
    
    ##create graphs from ttm
    labels = dict((i,k) for i,k in enumerate(ins))
    
    G = create_graph_with_adjmat(ttm, labels)
    #edge_list = nx.generate_edgelist(G)
    edge_list = G.edges().data()
    
    edgelist = []
    for line in edge_list:
        tup = (labels[line[0]], labels[line[1]], line[2]['weight'])
        edgelist.append(tup)

    df = pd.DataFrame(edgelist)
    df.to_csv(cwd+"/edgelists/"+every_file[:-4]+".csv", sep='\t', header=False, index=False)
