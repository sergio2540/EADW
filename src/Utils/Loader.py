from __future__ import division
import numpy as np
from scipy.spatial.distance import cosine
from scipy.sparse import *
from csc import divisi2
import math


#########################################
######        LOAD DA DATA          #####
#########################################
    
class Loader:
    
    #########################################
    ######          USERS               #####
    #########################################
    
    users = {}

    class User:
    
        def __init__(self, user_id, age, gender, occupation, zip_code):
            self.user_id = int(user_id)
            self.age = int(age)
            self.gender = gender
            self.occupation = occupation
            self.zip_code = zip_code
        
        def __str__(self):
            return "id : %d age: %d gender: %s occupation %s zip code: %s" % (self.user_id, self.age, self.gender, self.occupation, self.zip_code)
    
    def load_users(self):
        with open('ml-100k/u.user') as u_user_file:
            
            u_users = u_user_file.readlines()
        
            for user in u_users:
                (user_id, age, gender, occupation, zip_code) = user.split("|")
                self.users[user_id] = self.User(user_id, age, gender, occupation, zip_code)
    
    
    # for (id,user) in users.iteritems():
        # print id
        # print user    
    
    #########################################
    ######          MOVIES              #####
    #########################################
    
    movies = {}
    
    class Movie:
    
        def __init__(self, movie_id, title, release_date, video_release_date, imdb_url, genres):
            self.movie_id = int(movie_id)
            self.title = title
            self.release_date = release_date
            self.video_release_date = video_release_date
            self.imdb_url = imdb_url
            self.genres = genres
    
        
        def __str__(self):
            return "Movie id : %d Title: %s Release: %s Video Release %s IMDB URL: %s Genres %s" % (self.movie_id, self.title, self.release_date, self.video_release_date, self.imdb_url, self.genres)
    
    def load_movies(self):
        with open('ml-100k/u.item') as u_item_file:
            
            u_items = u_item_file.readlines()
        
            for item in u_items:
                (movie_id, title, release_date, video_release_date, imdb_url, genres) = item.split("|", 5)
                self.movies[movie_id] = self.Movie(movie_id, title, release_date, video_release_date, imdb_url, genres)
    
        
        
        # for (id,movie) in movies.iteritems():
            # print k
            # print movie 
            
    class DataSet:
        
        
        
        def __init__(self, n_users, n_movies,n_ratings):
            
            self.acc_rating = 0
            self.n_rating = 0
            self.data = set()  
            self.matrix = lil_matrix((n_users+1,n_movies+1),dtype=np.double)
            
            
            
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
            mean = np.mean(t)
            #print len(t)
            if math.isnan(mean):
                #print "nan"
                return self.getMeanRating()
            return mean
       
        def getVarUser(self,user):
            
            var = np.std(self.matrix_csr.data[self.matrix_csr.indptr[user]:self.matrix_csr.indptr[user+1]])
       
            if math.isnan(var):
                return 1
            return var
        
        def getMeanMovie(self,movie):
            
            t = self.matrix_csc.data[self.matrix_csc.indptr[movie]:self.matrix_csc.indptr[movie+1]]
            mean = np.mean(t)
            #print len(t)
            if math.isnan(mean):
                #print "nan"
                return self.getMeanRating()
            return mean
           
        
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
            self.U,self.s,self.V = matrix.svd(k=11)
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
            

            
    
    
    
    def load_dataSet(self, dataSet_path):
        
        with open(dataSet_path) as u_data_file:
            
            u_datas = u_data_file.readlines()
            dataSet = self.DataSet(943, 1682,len(u_datas))
            # from u.info
            # 943 users
            # 1682 items
            # 100000 ratings
              
            for data in u_datas:
                (user_id, movie_id, rating, timestamp) = data.split("\t")   
                dataSet.setRating(user_id, movie_id, rating)
            
            dataSet.finalize()   
            return dataSet
                
            # print dataSet.matrix
    
    
    
    def load_genre(self):
        genres = {}
        with open('ml-100k/u.genre') as u_genre_file:
            
            u_genres = u_genre_file.read()
        
            for g in u_genres.splitlines():
                if g == "":
                    break
                (genre, genre_id) = g.split("|")
                genres[genre_id] = genre
        
        return genres
    
    
    
    
    # print genres
