# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 20:20:32 2017

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

class LPA():
    def __init__(self, G, max_iter = 10):
        '''
        G: set of edge
        node: number of nodes
        max_iter: max iteration
        '''
        self._G = G
        self._node = len(G.node) 
        self._max_iter = max_iter
        
    def getLabel(self,node_index):
        '''
        get max label of neighbors
        '''
        m = collections.defaultdict(int)
        for neighbor_index in self._G.neighbors(node_index):
            neighbor_label = self._G.node[neighbor_index]["label"]
            m[neighbor_label] += 1
        max_v = max(m.itervalues())
        return [item[0] for item in m.items() if item[1] == max_v]

    def renewLabels(self):
    	'''
    	renew labels
    	'''
        for i in range(len(self._G.nodes())):
            node = self._G.node[i]
            label = node["label"]
            maxLabels = self.getLabel(i)
            if(label not in maxLabels):
                newLabel = random.choice(maxLabels)
                node["label"] = newLabel

    def stop(self):
        '''
        if all node has the label same with its most neighbor
        then stop
        '''
        for i in range(self._node):
            node = self._G.node[i]
            label = node["label"]
            maxLabels = self.getLabel(i)
            if(label not in maxLabels):
                return False
        return True

    def getCommunities(self):
        '''
        get the final community
        '''
        communities = collections.defaultdict(lambda:list())
        for node in self._G.nodes(True):
            label = node[1]["label"]
            communities[label].append(node[0])
        return communities.keys(),communities.values()
    
    def run(self,labels):
        '''
        main function of LPA algorithm
        '''
        # initial labels
        for i in range(self._node):
            self._G.node[i]["label"] = labels[i]
            
        iter_time = 0
        # renew labels
        while(not self.stop() and iter_time<self._max_iter):
            self.renewLabels()
            iter_time += 1
        return self.getCommunities()
    
    
if __name__ == '__main__':
    G = nx.Graph()
    index = 0
    filename = "footballEdges"#"Dataset"#
    print filename
    data,labels = loadData(filename)
    if filename == "Dataset":
        for line in data:
            indexI = 0
            for i in line:
                if i == 1:
                    source = index
                    target = indexI
                    G.add_edge(source, target)
                indexI += 1
            index += 1
    else:
        for line in data:
            source = line[0] - 1
            target = line[1] - 1
            G.add_edge(source,target)
    nx.draw(G,with_labels=True)                               
    plt.show()    
   
    key,value = LPA(G).run(labels)
    pic = nx.Graph()
    index = 0
    
    for c in value:
        print "community "+str(key[index])+" :"
        print c
        index += 1
        for i in c:
            for j in c:
                pic.add_edge(i,j)
    nx.draw(pic,with_labels=True)                               
    plt.show()  
    print "number of communities:"+str(index)                          