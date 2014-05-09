from __future__ import division
import numpy as np
from scipy.sparse import lil_matrix
from csc import divisi2
import math

class Data:
    
    def __init__(self, n_users, n_movies,n_ratings):
        
        self.acc_rating = 0
        self.n_rating = 0
        self.data = set()  
        self.matrix = lil_matrix((n_users+1,n_movies+1),dtype=np.double)
        self.users = {}
        self.movies = {}
        
        
    def isInMatrix(self,user,movie):
        return not self.matrix[user,movie] == 0
    
     
    def setRating(self, user, movie, rating):
      
       
        r = int(rating)
        u = int(user)
        m = int(movie)
    
            
        self.data.add( (r, u, m) )
        self.matrix[u,m] = r

        
        self.acc_rating += r
        self.n_rating += 1
        self.mean = self.acc_rating / self.n_rating
     
        
    def getRating(self, user, movie):
        return self.matrix[user,movie]
    
    def getUsers(self):
        return set(self.users)
    
    def getMovies(self):
        return set(self.movies)
    
    def getUsersThatRate(self, movie):
        return self.matrix_csc.indices[self.matrix_csc.indptr[movie]:self.matrix_csc.indptr[movie+1]]
    
    def getUsersThatRateB(self, movie):
        ratings = self.matrix_csc.data[self.matrix_csc.indptr[movie]:self.matrix_csc.indptr[movie+1]]
        acc=0
        l=0
        for r in ratings:
            acc += r 
            l+=1
        return (acc,l)
    
    def getMoviesRatedBy(self, user):
        return self.matrix_csr.indices[self.matrix_csr.indptr[user]:self.matrix_csr.indptr[user+1]]
    
    
    
    def getMeanUser(self,user):
        t = self.matrix_csr.data[self.matrix_csr.indptr[user]:self.matrix_csr.indptr[user+1]]
        
        if len(t) == 0:
            return self.getMeanRating()
        
        return np.mean(t)
   
    def getVarUser(self,user):
        
        var = np.std(self.matrix_csr.data[self.matrix_csr.indptr[user]:self.matrix_csr.indptr[user+1]])
   
        if math.isnan(var):
            return 1
        return var
    
    def getMeanMovie(self,movie):
        
        t = self.matrix_csc.data[self.matrix_csc.indptr[movie]:self.matrix_csc.indptr[movie+1]]
        
        if len(t) == 0:
            return self.getMeanRating()
        
        return np.mean(t)
       
    
    def getVarMovie(self,movie):
        var = np.std(self.matrix_csc.data[self.matrix_csc.indptr[movie]:self.matrix_csc.indptr[movie+1]])
        if math.isnan(var):
            return 1
        return var
        
    def getMeanRating(self):
        return self.mean
    
    def finalize(self):
        #print self.ratings
        
        self.matrix_csr = self.matrix.tocsr()
        self.matrix_csr.eliminate_zeros() 
        self.matrix_csr.sort_indices()
        
        
        self.matrix_csc = self.matrix.tocsc()
        self.matrix_csc.eliminate_zeros()
        self.matrix_csc.sort_indices()
        
        for n in self.matrix.nonzero():
            print n
        
        
        
    def make_svd(self):
        matrix = divisi2.make_sparse(self.data).normalize_all()
        self.U,self.s,self.V = matrix.svd(k=14)
        self.predictions = divisi2.reconstruct_activation(self.V, self.s)
        del self.data
        print "init end"
        
        
    def sim(self,m1,m2):
        #print "sim"
        #print self.predictions.entry_named(m1,m2)
        try:
            return self.predictions.entry_named(m1,m2)
        except:
            return -1