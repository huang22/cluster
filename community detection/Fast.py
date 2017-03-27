# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 16:55:27 2017

@author: huang
"""

import collections
import string
import random
import scipy.io as sio  
import matplotlib.pyplot as plt 
import networkx as nx

def loadData(filename):
    if filename == "footballEdges":
        a = sio.loadmat('Dataset/footballEdges.mat')
        data = a['footballEdges']
        labels = range(115)
    else:
        a = sio.loadmat('Dataset/Dataset.mat')
        data = a['Dataset']
        
        b = sio.loadmat('Dataset/labels.mat')
        labels = b['labels'][0]
    return data,labels


class Vertex():
    def __init__(self, vid, cid, nodes, weights=0):
        '''
        vid: vertex
        cid: community
        nodes: nodes in community
        weights: weights of edges
        '''
        self._vid = vid
        self._cid = cid
        self._nodes = nodes
        self._weights = weights 

class FastUnfolding():
    def __init__(self, G,filename):
        '''
        G: set of edge
        edge: total number of edge
        _cid_vertex: community set
        _vid_vertex: vertex set
        '''
        data,labels = loadData(filename)
        self._G = G
        self._edge = 0
        # community
        self._cid_vertex = {} 
        # vertex
        self._vid_vertex = {}  
        c1,c2,c3,c4 = [],[],[],[]
        for vid in self._G.keys():
            
            #self._cid_vertex[labels[0][vid]-1].add(vid)
            self._cid_vertex[vid] = set([vid])
            self._vid_vertex[vid] = Vertex(vid, vid, set([vid]))
            if filename == "Dataset":
                if labels[vid] == 1:
                    c1.append(vid)
                elif labels[vid] == 2:
                    c2.append(vid)
                elif labels[vid] == 3:
                    c3.append(vid)
                else:
                    c4.append(vid)
            
            # total edge number
            self._edge += sum([1 for neighbor in self._G[vid].keys()])
        self._edge = self._edge / 2
        if filename == "Dataset":
            for vid in self._G.keys():
                self._cid_vertex[vid].remove(vid)
                self._cid_vertex[labels[vid]-1].add(vid)
                self._vid_vertex[vid]._cid = labels[vid]-1
        
    def firstPass(self):
        '''
        first pass
        '''
        hasChanged = False
        
        while True:
            flag = True
            for v_vid in self._G.keys():
            	# community of this vertex
                v_cid = self._vid_vertex[v_vid]._cid
                # weights
                v_weights = sum(self._G[v_vid].values()) + self._vid_vertex[v_vid]._weights

                cid_Q = {}

                for w_vid in self._G[v_vid].keys():
                    w_cid = self._vid_vertex[w_vid]._cid
                    if w_cid in cid_Q:
                        continue
                    else:
                    	# sum of weights in community w_cid
                        tot = sum([sum(self._G[k].values())+self._vid_vertex[k]._weights for k in self._cid_vertex[w_cid]])
                        if w_cid == v_cid:
                            tot -= v_weights
                        v_weights_in = sum([v for k,v in self._G[v_vid].items() if k in self._cid_vertex[w_cid]])
                        delta_Q = v_weights_in / (2 * self._edge) - v_weights * tot / (2 * self._edge * self._edge)
                        cid_Q[w_cid] = delta_Q
                    
                cid,max_delta_Q = sorted(cid_Q.items(),key=lambda item:item[1],reverse=True)[0]
                # renew
                if max_delta_Q > 0.0 and cid != v_cid:   
                    self._vid_vertex[v_vid]._cid = cid
                    self._cid_vertex[cid].add(v_vid)
                    self._cid_vertex[v_cid].remove(v_vid)
                    flag = False
                    hasChanged = True
            if flag:
                break
        return hasChanged
    def secondPass(self):
        '''
        second pass
        '''
        cid_vertex = {}
        vid_vertex = {}
        for cid,vertex in self._cid_vertex.items():
            if len(vertex) == 0:
                continue
            # create new vertex
            newVertex = Vertex(cid, cid, set())
            for vid in vertex:
                newVertex._nodes.update(self._vid_vertex[vid]._nodes)
                newVertex._weights += self._vid_vertex[vid]._weights
                for k,v in self._G[vid].items():
                    if k in vertex:
                        newVertex._weights += v / 2.0
            cid_vertex[cid] = set([cid])
            vid_vertex[cid] = newVertex
        
        G = collections.defaultdict(dict)   
        for cid1,vertex1 in self._cid_vertex.items():
            if len(vertex1) == 0:
                continue
            for cid2,vertex2 in self._cid_vertex.items():
                if cid2 <= cid1 or len(vertex2) == 0:
                    continue
                edge_weight = 0.0
                for vid in vertex1:
                    for k,v in self._G[vid].items():
                        if k in vertex2:
                            edge_weight += v
                if edge_weight != 0:
                    G[cid1][cid2] = edge_weight
                    G[cid2][cid1] = edge_weight
        
        self._cid_vertex = cid_vertex
        self._vid_vertex = vid_vertex
        self._G = G 
        
    def getCommunities(self):
        '''
        get the final community
        '''
        communities = []
        for vertex in self._cid_vertex.values():
            if len(vertex) != 0:
                c = set()
                for vid in vertex:
                    c.update(self._vid_vertex[vid]._nodes)
                communities.append(c)
        return communities
    
    def run(self):
        '''
        first pass and then second pass
        '''   
        iter_time = 0
        while True and iter_time < 10:
            iter_time += 1
            hasChanged = self.firstPass()
            if hasChanged:
                self.secondPass()
            else:
                break
        return self.getCommunities()

if __name__ == '__main__':
    filename = "Dataset"#"footballEdges"#
    print filename
    data,labels = loadData(filename)
    G = collections.defaultdict(dict)
    pic1 = nx.Graph()
    index = 0
    if filename == "Dataset":
        for line in data:
            indexI = 0
            for i in line:
                if i == 1:
                    source = index
                    target = indexI
                    G[source][target] = 1.0
                    G[target][source] = 1.0
                    pic1.add_edge(source,target)
                indexI += 1
            index += 1
    else:
        for line in data:
            source = line[0] - 1
            target = line[1] - 1
            G[source][target] = 1.0
            G[target][source] = 1.0
            pic1.add_edge(source,target)
        
    nx.draw(pic1,with_labels=True)                               
    plt.show()    
         

    communities = FastUnfolding(G,filename).run()
    pic = nx.Graph()
    index = 0
    
    for c in communities:
        print "community "+str(index)+" :"
        print c
        index += 1
        for i in c:
            for j in c:
                pic.add_edge(i,j)
    nx.draw(pic,with_labels=True)                               
    plt.show()                           
    print "number of communities:"+str(index)
    