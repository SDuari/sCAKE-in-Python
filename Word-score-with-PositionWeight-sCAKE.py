#3.

import os
import numpy as np
import pandas as pd
from read_write_create import *

def invert_num(l):
    return [(1.0/x) for x in l if x!=0]

def get_node_weight(w, df_pos):
    
    w_weight = 0
    w_row = df_pos.loc[df_pos["words"] == w]
    
    if len(w_row["words"]) > 0:
        posi = list(w_row["positions"])[0]
        posi = posi[:-1]
        if(len(posi) >0):
            w_weight = sum(invert_num(posi))
    
    return w_weight

#------ main ------#
global cwd, path, data_path

cwd = os.getcwd()
path = cwd
data_path = cwd + "/data"

create_folder(cwd,"SCScore_W")
word_score_path = cwd + "/SCScore/"

print("Word-score-with-PositionWeight-sCake")
for every_file in (os.listdir(data_path)):
    
    print(every_file)
    file_name = every_file[:-4]
    #text = read_text_from_file(data_path,every_file)
    
    f_wordScore = read_text_from_file(cwd+"/SCScore/",file_name+".csv.sortedranked.IF.txt")
    
    with open(cwd+"/positions/"+file_name+".pkl", 'rb') as f:
        df_pos = pd.read_pickle(f, compression=None)
        
    df = pd.read_csv(word_score_path + file_name  +".csv.sortedranked.IF.txt")
    words = df["Name"]
    wscore = df["IF"]
    
    node_weight = [0] * len(words)
    for index in range(len(words)):
        node_weight[index] = get_node_weight(words[index], df_pos)
    
    new_score = list(wscore * node_weight)
    
    data = dict()
    data["Words"] = words
    data["Old_WScore"] = wscore
    data["Position_Weight"] = node_weight
    data["SCScore"] = new_score
    new_df = pd.DataFrame(data=data)
    new_df = new_df.sort_values("SCScore",ascending=False)
    
    new_df.to_csv(cwd+"/SCScore_W/"+ file_name +"_ranked_list.csv")
     
