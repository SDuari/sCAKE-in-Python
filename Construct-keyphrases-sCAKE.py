4.

import os
import re
import nltk
import numpy as np
import pandas as pd
from read_write_create import *

def clean_text(text):
    
    text = text.strip()
    text = text.lower()
    
    numbers_ex = re.compile("[0-9]+(-[0-9]+)?")
    text = re.sub(numbers_ex, '', text)
    
    #hyphen_ex = re.compile("[-]")
    #text = re.sub(hyphen_ex, ' ', text)
    
    #punctuation_ex = re.compile("[^a-z- ]")
    punctuation_ex = re.compile("[^a-z ]")
    text = re.sub(punctuation_ex, '', text)
    
    words = nltk.word_tokenize(text)
    #words = [i for i in words if i not in stopwords]
    
    return list(set(words))


def get_Predicted_KP_all(words_list):
    
    s = ' '.join(words_list)
    s = s.split("*")
    s = [x.strip() for x in s] 
    s = [x for x in s if x!='']
    s = list(set(s))
    return s

global cwd, path, data_path

cwd = os.getcwd()
path = cwd
data_path = cwd + "/data/"
word_score_w_path = cwd + "/SCScore_W/"
save_path = cwd + "/KP-Preds"
newline_ex = re.compile("\n")

create_folder(cwd,"KP-Preds")

print("Construct-keyphrases-sCake")
for every_file in (os.listdir(data_path)):
    
    print(every_file)
    file_name = every_file[:-4]
    
    text = read_text_from_file(data_path,every_file)
    text = re.sub(newline_ex, ' ', text)
    
    score_df = pd.read_csv(word_score_w_path + file_name  +"_ranked_list.csv")
    
    words = clean_text(text)
    
    pred_keys = list(score_df["Words"])
    pred_keys = pred_keys[:len(pred_keys)/3]
    
    words = ["*" if word not in pred_keys else word for word in words]
    
    if(len(words)) > 0:
        pred_kp = get_Predicted_KP_all(words)
        
    pred_kp = list(set(pred_kp))
    write_list_to_file(save_path, file_name+"-all-one-third-L3.txt",pred_kp)
    