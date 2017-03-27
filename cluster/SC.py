# -*- coding: utf-8 -*-
"""
Created on Wed Mar 01 16:11:09 2017

@author: huang
"""

from numpy import *
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math as m

def loadDataSet(fileName): 
    '''
    load dataset
    '''
    dataMat = []                
    fr = open(fileName)
    for line in fr.readlines():
        fltLine = []
        line = ' '.join(line.split())
        curLine = line.strip().split(' ')
        line0 = curLine[0].split('e')
        if line0[1][1] == '+':
            num = int(line0[1][2])
        else:
            num = -int(line0[1][2])
        fltLine.append(float(line0[0])*(10**num))

        line1 = curLine[1].split('e')
        if line1[1][1] == '+':
            num = int(line1[1][2])
        else:
            num = -int(line1[1][2])
        fltLine.append(float(line1[0])*(10**num))

        dataMat.append(fltLine)
    return np.array(dataMat)

def distMeas(vecA, vecB):
    '''
    return distance of vecA and vecB
    '''
    return sqrt(sum(power(vecA - vecB, 2)))

def kMeans(dataSet, k):
    '''
    KMeans algorithm
    '''
    m,n = shape(dataSet)
    clusterSet = mat(zeros((m,2)))                                    
    centroids = mat(zeros((k,n)))
    
    # create random cluster centers
    hasSelected = []
    j = 0
    while j < k:
        select = random.randint(0,m-1)
        if select not in hasSelected:
            centroids[j,:] = dataSet[select,:]
            j += 1

    isChanged = True
    while isChanged:
        isChanged = False
        #for each data point assign it to the closest centroid
        for i in range(m):
            minDist = inf
            minIndex = -1
            # calculate which centroid is the closest
            for j in range(k):
                dist = distMeas(centroids[j,:],dataSet[i,:])
                if dist < minDist:
                    minDist = dist
                    minIndex = j
            if clusterSet[i,0] != minIndex: 
                isChanged = True
            clusterSet[i,:] = minIndex,minDist
        #recalculate centroids
        for cent in range(k):
            #get all the point in this cluster
            ptsInClust = dataSet[nonzero(clusterSet[:,0].A==cent)[0]]
            #assign centroid to mean 
            centroids[cent,:] = mean(ptsInClust, axis=0) 
    #print centroids
    return centroids, clusterSet
'''
# use kNN to construct matrix W
def kNN(dataMat,data,dataIndex):
    minDist = inf
    index = 0
    for i in dataMat:
        if index != dataIndex:
            dist = distMeas(data,i)
            if dist < minDist:
                minDist = dist
                returnData = i
                returnindex = index
        index += 1
    return returnData,returnindex
            
def getW(dataMat):
    W = zeros((len(dataMat),len(dataMat)))
    index = 0
    for i in dataMat:
        returnData,returnIndex = kNN(dataMat,i,index)
        W[index][returnIndex] = W[returnIndex][index] = 1
    return W
'''

def getW(data, std_dev=0.05):
    '''
    construct matrix W
    '''
    mat = np.zeros((len(data), len(data)))
    for i, vecA in enumerate(data):
        for j, vecB in enumerate(data):
            if i == j:
                mat[i, j] = 0.
            else:
                mat[i, j] = m.exp((-distMeas(vecA, vecB)**2.)/std_dev)
    return mat

def getL(dataMat): 
    '''
    construct matrix L
    '''
    W = getW(dataMat)
    d=[np.sum(row) for row in W]  
    D=np.diag(d)  
    L=D-W   
    Dn=np.power(np.linalg.matrix_power(D,-1),0.5)  
    Lbar=np.dot(np.dot(Dn,L),Dn)  
    return Lbar
    
def getKSmallestEigVec(dataMat,n_clusters): 
    '''
    get k vectors
    '''
    L = getL(dataMat)
    w, v = linalg.eig(L)
    v_sorted = np.asarray([v for (w,v) in sorted(zip(w,v.transpose()), \
		reverse=True)][0:n_clusters]).transpose()
    row_sums = linalg.norm(v_sorted, axis=1)
    return v_sorted / row_sums[:, np.newaxis]
 
def showCluster(dataSet, k, centroids, clusterAssment): 
    '''
    plot dataset
    '''
    numSamples, dim = dataSet.shape    
    mark = ['or', 'ob', 'og', 'ok', '^r', '^b', 'sr', 'sb', '<r', '<b']    
    # draw all samples  
    for i in xrange(numSamples):  
        markIndex = int(clusterAssment[i, 0])  
        plt.plot(dataSet[i, 0], dataSet[i, 1], mark[markIndex])  
  
    mark = ['Dr', 'Db', 'Dg', 'Dk', '+r', '+b', 'dr', 'db', 'pr', 'pb']  
    # draw the centroids  
    for i in range(k):  
        plt.plot(centroids[i, 0], centroids[i, 1], mark[i], markersize = 12)  
  
    plt.show()  

if __name__ == "__main__":
    k = cluster = 2
    dataMat = loadDataSet('Data/ringData.txt')#('Data/Gaussian.txt')#
    kEigVec=getKSmallestEigVec(dataMat,k)  
    myCentroids, clustAssing = kMeans(kEigVec, cluster)
    print "in eigenvalue space"
    showCluster(kEigVec,cluster,myCentroids, clustAssing)
    
    print "in data space"
    m,n = shape(dataMat)
    clusterSet = mat(zeros((m,2)))
    for i in range(m):
        minDist = inf
        minIndex = -1
        # calculate which centroid is the closest
        for j in range(k):
            dist = distMeas(myCentroids[j,:],dataMat[i,:])
            if dist < minDist:
                minDist = dist
                minIndex = j
        if clusterSet[i,0] != minIndex: 
            isChanged = True
        clusterSet[i,:] = minIndex,minDist
    showCluster(dataMat,cluster,myCentroids, clusterSet)