#2.

from __future__ import division
from igraph import *
#from jgraph import *
import sys
import copy
import random
import numpy as np
import numpy.random as nprnd
import pandas as pd
import os
from read_write_create import *

def triangles(G,nodes=None):
    if nodes is None:
        nodes_nbrs = G.adj.items()
    else:
        nodes_nbrs= ( (n,G[n]) for n in G.nbunch_iter(nodes) )
    for v,v_nbrs in nodes_nbrs:
        vs=set(v_nbrs) -set([v])
        ntriangles=0
        for w in vs:
            ws=set(G[w])-set([w])
            ntriangles+=len(vs.intersection(ws))-2                           # checking for validity
        yield (v,len(vs),ntriangles)

def edge_support(G):
    neighbors=G.neighborhood()    #neighbors_iter
    nbrs=dict((v.index,set(neighbors[v.index])) for v in G.vs)
    support = {}
    for e in G.es:
        nod1,nod2 = e.source, e.target	
        nod1_nbrs = set(nbrs[nod1])-set([nod1])
        nod2_nbrs = set(nbrs[nod2])-set([nod2])
        sup = len(nod1_nbrs.intersection(nod2_nbrs))
        #G[nod1][nod2]['support'] = sup
        support[(nod1,nod2)] = sup
    #print ('support :', support)
    return support
        
def ktruss(G):   
    #G = G.simplify(combine_edges={"weight": "sum", "count":"sum"})    #assume graph is simple
    support = edge_support(G)
    edges=sorted(support,key=support.get)
    bin_boundaries=[0]
    curr_support=0
    for i,e in enumerate(edges):
        if support[e]>curr_support:
            bin_boundaries.extend([i]*(support[e]-curr_support))
            curr_support=support[e]
            
    edge_pos = dict((e,pos) for pos,e in enumerate(edges))
   
    truss={}         ## initial guesses for truss is support
    neighbors=G.neighborhood()    #neighbors_iter
    #print ('neighbors:', neighbors)
    nbrs=dict((v.index,(set(neighbors[v.index])-set([v.index]))) for v in G.vs)
    #nbrs=dict((v.index,set(neighbors[v.index])) for v in G.vs)
    #print ('nbrs:', nbrs)
    for e in edges:
      #print ('processing edge : ', e, 'support :', support[e], 'pos:', edge_pos[e])
      u,v =e[0], e[1]
      if not(u == v) :
        common_nbrs = set(nbrs[u]).intersection(nbrs[v])
        #print (u,v,'common_nbrs',common_nbrs)
        for w in common_nbrs:
            if (u,w) in support :             
               e1 = (u,w)
            else :
               e1 = (w,u)
            if (v,w) in support :
               e2 = (v,w)
            else:
               e2 = (w,v)
            pos=edge_pos[e1]
            if support[e1] > support[e] :
               bin_start=bin_boundaries[support[e1]]
               edge_pos[e1]=bin_start
               edge_pos[edges[bin_start]]=pos
               edges[bin_start],edges[pos]=edges[pos],edges[bin_start]
               bin_boundaries[support[e1]]+=1
            #print ('e1',e1,'support:',support[e1], 'pos:', pos, 'new pos:', edge_pos[e1])
            
            pos=edge_pos[e2]
            if support[e2] > support[e] :
               bin_start=bin_boundaries[support[e2]]
               edge_pos[e2]=bin_start
               edge_pos[edges[bin_start]]=pos
               edges[bin_start],edges[pos]=edges[pos],edges[bin_start]
               bin_boundaries[support[e2]]+=1
            #print ('e2',e2,'support:',support[e2], 'pos:', pos, 'new pos:', edge_pos[e2])
              
            support[e1] =  max(support[e], support[e1]-1)     
            support[e2] =  max(support[e], support[e2]-1)   
            
        truss[e] = support[e] + 2 
        nbrs[u].remove(v)
        nbrs[v].remove(u)
    #print ('Truss: ', truss)
    #print ('Sorted Truss: ', sorted(truss,key=truss.get))
    return truss
    
    
def getnodetrussness(graph):
    n = graph.vcount()
    ktrussdict = ktruss(graph)
    nodetruss = [0] * n
    for edge in graph.es:
      source = edge.source		
      target = edge.target
      if not (source == target) :
         t = ktrussdict[(source,target)]
      else:
         t = 0		  
      nodetruss[source] = max(nodetruss[source], t)
      nodetruss[target] = max(nodetruss[target], t)
    
    return nodetruss
    


def influencemeasure(graph):
    n = graph.vcount()
    degree = graph.degree()
    influence=[0] * n

    degree = graph.degree(mode='out')
    strength = graph.strength(weights = graph.es['weight'])
    if (sum(strength) == 0.0) :
       #print ('unweighted graph')
       graph.es['weight'] = [1.0] * graph.ecount()
       strength = graph.strength(weights = graph.es['weight'])
       
    vnames = [v["name"] for v in graph.vs]

    
    nodetruss = getnodetrussness(graph)
    maxtruss = max(nodetruss)
    entropy = [0] * n
    bridging = [0] * n
    diversity = [0] * n
    
    
    for v in graph.vs:
          ent = 0
          nbrtrusses = [nodetruss[w] for  w in graph.neighbors(v)]
          numneighbors = len(nbrtrusses)
          numclasses = len(set(nbrtrusses))
          if not(maxtruss-1) == 1:
          		ent = numclasses/maxtruss
          		
          entropy[v.index] = ent 
         
          bridging[v.index] = sum([strength[w] * nodetruss[w]  for w in graph.neighbors(v)])   
    influence = [1/(a*1.0) * b*(c+1) for a,b,c in zip(nodetruss,bridging,entropy)]   
    return influence, entropy, bridging, nodetruss


def SortedRankedToFile(graphname, vnames,centrality, measurename):
       #directory = inputdirectory+ graphname + "/"
       directory = outputdirectory
       #if not os.path.exists(directory):
           #os.makedirs(directory)
       n = len(vnames)
       data = zip(vnames,centrality)
       pddata =  pd.DataFrame(data, index=range(0,n), columns=["Name",measurename])
       #pddata.to_csv(directory + graphname +"."+measurename+".txt",index=False) 
       sortedcol = pddata.sort_values(by=measurename, ascending=False)
       sortedcol[measurename+'DenseRank'] = sortedcol[measurename].rank(method='dense',ascending=False)
       sortedcol[measurename+'MinRank'] = sortedcol[measurename].rank(method='min',ascending=False)
       outputfile = directory + graphname +".sortedranked."+measurename+".txt"
       #print (outputfile)
       sortedcol.to_csv(outputfile,index=False) 
       return


def getInfluence(graphname) :
       
       g = mysrcdir + '/' + graphname
       #print (g)
       
       directory = outputdirectory+ graphname + "/"
       #if not os.path.exists(directory):
           #os.makedirs(directory)
 
       timingoutputfile = directory + graphname +".InfluenceTiming"
       os.remove(timingoutputfile) if os.path.exists(timingoutputfile) else None 
       
       graph = Graph.Read_Ncol(g,directed=False,weights=True)
       graph.vs.select(_degree = 0).delete()
    
       graph.es['weight'] = [1.0] * graph.ecount() 
       
       strength = graph.strength(weights = graph.es['weight'])
       if (sum(strength) == 0.0):
          graph.es['weight'] = [1.0] * graph.ecount()     #assign weight 1 to each edge
          strength = graph.strength(weights = graph.es['weight'])
      
       n = graph.vcount()
       m = graph.ecount()
       #print ('weighted graph n,m: ', len(graph.vs), len(graph.es))
      
       vnames = [v["name"] for v in graph.vs]
       vindices = [v.index for v in graph.vs]
       
       #Timings = {}  
       
       #print ('Computing Influence')
       #start_time = time.time()
       influence,entropy,influencebridging, nodetruss =  influencemeasure(graph)   
       #Timings["IF"] = time.time() - start_time 
       measurename = "IF"
       SortedRankedToFile(graphname,vnames,influence,'IF' )
       return          


def getTopK(whichfile,k=10):
    data = pandas.read_csv(whichfile)  
    topk = data['Name'][:k]
    return topk



if __name__=='__main__':

    global outputdirectory, mysrcdir
    
    cwd = os.getcwd()
    create_folder(cwd,"SCScore")
    outputdirectory = cwd +'/SCScore/'
    mysrcdir = cwd + "/edgelists/"
    
    print("InfluenceEvaluation")
    myfiles = os.listdir(mysrcdir)
    for f in myfiles:
        print(f)
    	getInfluence(f)  
    
