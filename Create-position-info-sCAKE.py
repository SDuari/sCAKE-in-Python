#0.

import os
import re
import nltk
import string
import pandas as pd
from read_write_create import *
from nltk.stem import PorterStemmer 

global cwd, path, data_path

cwd = os.getcwd()
path = cwd
data_path = cwd + "/data"
create_folder(cwd, "positions")

numbers_ex = re.compile("[0-9]+(-[0-9]+)?")
punctuation_ex = re.compile("[^a-z ]")
roman_num_ex = re.compile("\\b[i|v|x|l|c|d|m]{1,3}\\b")
stopwords = read_list_from_file(path, "stopwords.txt")
ps = PorterStemmer()

print("create-position-info-sCake")
for every_file in (os.listdir(data_path)):
    
    print(every_file)
    text = read_text_from_file(data_path,every_file)
    
    ## pre-processing text
    text = text.strip()
    text = text.lower()
    text = re.sub(numbers_ex, '', text)
    text = re.sub(punctuation_ex, '', text)
    text = re.sub(roman_num_ex, '', text)
    
    words = nltk.word_tokenize(text)
    words = [i for i in words if i not in stopwords]
    words = [ps.stem(i) for i in words]
    
    selected_words = list(set(words))
    
    ## end of pre-processing
    
    N = len(words) +1
    posi = list()
    t = list()
    tf = list()
    
    for w in selected_words:        
        posw = [i for i, word in enumerate(words) if w == word]
        w_freq = len(posw)+1
        posw.append(N)
        t.append(w)
        tf.append(w_freq)
        posi.append(posw)
  
    #print(posi)
    
    data = dict()
    data["words"] = t
    data["tf"] = tf
    data["positions"] = posi
    
    df = pd.DataFrame(data=data)
    df.to_pickle(cwd+"/positions/"+every_file[:-4]+".pkl")
    
    
    
    
    
    
    
    
    
    
    
