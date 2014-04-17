from __future__ import division


#########################################
######        LOAD DA DATA          #####
#########################################
    
    

#########################################
######          USERS               #####
#########################################

users = {}

class User:

    def __init__(self,user_id, age, gender, occupation,zip_code):
        self.user_id = int(user_id)
        self.age = int(age)
        self.gender = gender
        self.occupation = occupation
        self.zip_code = zip_code
    
    def __str__(self):
        return "id : %d age: %d gender: %s occupation %s zip code: %s" % (self.user_id,self.age, self.gender, self.occupation, self.zip_code)

def load_users():
    with open('ml-100k/u.user') as u_user_file:
        
        u_users = u_user_file.readlines()
    
        for user in u_users:
            (user_id, age, gender, occupation,zip_code) = user.split("|")
            users[user_id] = User(user_id,age,gender,occupation,zip_code)


#for (id,user) in users.iteritems():
    #print id
    #print user    

#########################################
######          MOVIES              #####
#########################################
movies = {}

class Movie:

    def __init__(self,movie_id,title,release_date,video_release_date,imdb_url,genres):
        self.movie_id = int(movie_id)
        self.title = title
        self.release_date = release_date
        self.video_release_date = video_release_date
        self.imdb_url = imdb_url
        self.genres = genres

    
    def __str__(self):
        return "Movie id : %d Title: %s Release: %s Video Release %s IMDB URL: %s Genres %s"  % (self.movie_id,self.title, self.release_date, self.video_release_date, self.imdb_url,self.genres)

def load_movies():
    with open('ml-100k/u.item') as u_item_file:
        
        u_items = u_item_file.readlines()
    
        for item in u_items:
            (movie_id, title, release_date, video_release_date, imdb_url, genres ) = item.split("|",5)
            movies[movie_id] = Movie(movie_id,title,release_date,video_release_date,imdb_url, genres)



#for (id,movie) in movies.iteritems():
    #print k
    #print movie    


import math
import numpy as np
from scipy.sparse import *

class DataSet:
    
    
    
    def __init__(self,n_users,n_movies):
        self.n_users = n_users
        self.n_movies = n_movies
        
        self.users = set()
        self.movies = set()
        
        self.acc_rating = 0
        self.n_rating = 0
        
        #Users comecam em 1 ate 943 inclusive
        self.matrix = np.zeros((n_users+1,n_movies+1),dtype=np.int)

        #print self.matrix
    
    def getSVD(self,k):
        U, s, V = np.linalg.svd(self.matrix,full_matrices=False)
        self.U = U[0:,0:k]
        self.V = V[0:k,0:].transpose()
        self.s = s[0:k]
        print self.U.shape
        print self.V.shape
        print self.s.shape
    
    
    def setRating(self,user,movie, rating):
      
        u = int(user)
        m = int(movie)
        r = int(rating)
        
        self.users.add(u)
        self.movies.add(m)
    
        
        self.acc_rating += r
        self.n_rating += 1
        self.mean = self.acc_rating/self.n_rating
        
        self.matrix[u,m] = r
     
        
    def getRating(self,user,movie):
        return self.matrix[user,movie]
    
    def getUsers(self):
        return self.users
    
    def getMovies(self):
        return self.movies
    
    def getUsersThatRate(self,movie):
        users = self.matrix[:,movie]
        #filter zeros
        users = np.flatnonzero(users)
        #print users
        return set(users)
    
    def getMoviesRatedBy(self,user):
        movies = self.matrix[user,:]
        #filter zeros
        movies = np.flatnonzero(movies)
        return set(movies)
    
    def getUserVar(self,user):
        movies = self.matrix[user,:]
        #filter zeros
        movies = np.flatnonzero(movies)
        std = np.std(self.matrix[user,movies])
        #print std
        return std
    
    def getMovieVar(self,movie):
        users = self.matrix[:,movie]
        #filter zeros
        users = np.flatnonzero(users)
        std = np.std(self.matrix[users,movie])
        #print std
        return std
        
    
    def getMean(self):
        return self.mean
        
#Matriz Data[user][movie]
#data_set = {}

dataSet = DataSet(943,1682)

def load_dataSet(dataSet_path):
    with open(dataSet_path) as u_data_file:
        
        u_datas = u_data_file.readlines()
        
        # from u.info
        # 943 users
        # 1682 items
        # 100000 ratings
          
        for data in u_datas:
            (user_id, movie_id, rating, timestamp) = data.split("\t")   
            dataSet.setRating(user_id,movie_id, rating)
            
        #print dataSet.matrix



def load_genre():
    genres = {}
    with open('ml-100k/u.genre') as u_genre_file:
        
        u_genres = u_genre_file.read()
    
        for g in u_genres.splitlines():
            if g == "":
                break
            (genre, genre_id) = g.split("|")
            genres[genre_id] = genre
    
    return genres




#print genres


#########################################
######          UTILS               #####
#########################################


#cache



usersThatRate = {}

def getUsersThatRate(movie):
    
    if movie in usersThatRate:
        return usersThatRate[movie]
        
    users = dataSet.getUsersThatRate(movie)
    
    #print users                 
    
    usersThatRate[movie] = users            
    return users


def getUsersThatRateAandB(a, b):
    
    users_a = getUsersThatRate(a)
    users_b = getUsersThatRate(b)
    
    return users_a.intersection(users_b)

moviesRatedBy = {}
def getMoviesRatedBy(user):
    
    if user in moviesRatedBy:
        return moviesRatedBy[user]
    
    movies = dataSet.getMoviesRatedBy(user)
    moviesRatedBy[user] = movies
    return movies

    
      
def cosine_distance(u, v):
    """
    Returns the cosine of the angle between vectors v and u. This is equal to
    u.v / |u||v|.
    """
    d = (math.sqrt(np.dot(u, u)) * math.sqrt(np.dot(v, v))) 
  
    
    return np.dot(u, v) / d


    


#########################################
######          BASELINE            #####
#########################################

def mean_user(user):
    
    movies = list(getMoviesRatedBy(user))
    avg = np.average(dataSet.getRating(user,movies))
    if avg < 1 and avg > 4:
        print avg
    return avg


def mean_movie(movie):
    
    users = list(getUsersThatRate(movie))
    avg = np.average(dataSet.getRating(users,movie))
    
    if avg < 1 and avg > 4:
        print avg

    return avg

##Recommeder Handbook

##pag.144 - bui = mean + bu + bi

def mean_rating():
    return dataSet.getMean()
    


#Cache do base_movie
b_m = {}

def base_movie(mean, movie):
    
    if movie in b_m:
        return b_m[movie]
    
    lambda2 =  24
    accum = 0
    users  = getUsersThatRate(movie)
    
    for user in users:
        accum += dataSet.getRating(user, movie) - mean
    
    res = accum/(lambda2 + len(users))
    
    b_m[movie] = res
    
    return res 
            
#Cache do base_user
b_u = {}
def base_user(mean,user):
    
    if user in b_u:
        return b_u[user]
    
    lambda3 = 24
    accum = 0
    movies = getMoviesRatedBy(user)
    
    for movie in movies:
        accum += dataSet.getRating(user, movie) - mean - base_movie(mean, movie)
    
    
    res = accum/(lambda3 + len(movies))
    
    b_u[user] = res

    return res


def baseline(user, movie):
     
    mean = mean_rating()
    #print "mean %f" % mean
    
    bm = base_movie(mean, movie)
    #print "b_m %f" % bm
    
    bu = base_user(mean,user)
    #print "b_u %f" % bu
    
    return mean + bm + bu

S = np.zeros((dataSet.n_movies+1,dataSet.n_movies+1))

def similarity(m1,m2):


    if S[m1,m2] != 0 :
        return S[m1,m2]
    
    if S[m2,m1] != 0 :
        return S[m2,m1]
    


    U = getUsersThatRateAandB(m1,m2)
   
    
    #Optimizacao 1
    #Inverse User frequency
    #log(numero de users/ numero de users que fizeram rate de j)
    
    n_movies = len(dataSet.getMovies())
    
    temp1 = []
    temp2 = []
    for u in U:
        #print u
        v1 = dataSet.getRating(u,m1) - baseline(u,m1)
        v2 = dataSet.getRating(u, m2) - baseline(u,m2)
        
        n1 = math.log(n_movies/len(getMoviesRatedBy(u)))
        n2 = math.log(n_movies/len(getMoviesRatedBy(u)))
        
       
        
        t1 = n1*v1
        t2 = n2*v2
        #print t1
        if t1 == 0 or t2 == 0:
            S[m1,m2] = None
            return None
        
        temp1.append(t1)
        temp2.append(t2)
    
    n = len(U)
    #Caso Especial nao existem utilizadores q avaliaram m1 e m2
    if n == 0:
        S[m1,m2] = None
        return None
   
    sim = cosine_distance(temp1,temp2)
    
    
    #Optimizacao - Slide 20 (37/72)
    #tr-98-12.pdf
    
    p = 2.5
    sim = sim*math.pow(abs(sim),p-1)
    #print sim
       
    #Optimizacao  - Slide 19 (30/72)
    #if(n <= 50):
        #sim = (n/50)*sim
        
    #Optimizacao  - Survey
    #else:
    sim = (n/(n+100))*sim
    
 
    

  
    
    S[m1,m2] = sim
    

    return sim        
    
def getMostSimilarMovies(user, movie,k):
   
    
    sims = []
    
    ratedByUser = dataSet.getMoviesRatedBy(user)
    
    #print len(ratedByUser)
    
    for m in ratedByUser:
        s = similarity(m,movie)
        
        #se descartar negativos tenho menos erro
        
        if not s == None and s > 0:
            sims.append((m,s))
        #print s

         
    sims = sorted(sims,key=lambda x: -abs(x[1]))

    #print sims
    return sims[0:k]
    
    
    
def prediction(user,movie):
    bui = baseline(user,movie)
    
    #print "Baseline %s" % bui
    #print "Baseline Movie %s" % b_m[movie]
    #print "Baseline User %s" % b_u[user]
    
    divisor = 0
    dividendo = 0
    
    k = 15
    M = getMostSimilarMovies(user,movie,k)
    
    for (m,s) in M: 
        dividendo += s*(dataSet.getRating(user, m) - baseline(user,m))
        divisor += abs(s)
        #print m,s
            

    

    
    pred = bui + (dividendo/divisor)
    return pred


#########################################
######          MAIN             #####
#########################################

import argparse

#########################################
######          PARSING             #####
#########################################

parser = argparse.ArgumentParser(description='Recommend Movies.')
parser.add_argument('--online', type=bool, default=False,
                   help='prompt interactive console (Default=False)')
parser.add_argument('--training',default="./ml-100k/u.data",
                   help='path to batch training file(Default=./ml-100k/u.data)')
parser.add_argument('--test',
                   help='path to batch test file')

args = parser.parse_args()
print args

def predict(test_path):
    
    with open(test_path) as u_test_file:
        u_tests = u_test_file.readlines()
        
        error_accum = 0
        error_count = 0
        correct = 0
        
        for test in u_tests:
            (user_id, movie_id, rating, timestamp) = test.split("\t") 
            p = math.ceil(prediction(user_id,movie_id))
            r = int(rating)
            res = abs(r - p)
            
            if res == 0:
                correct += 1
                
            error_accum += res 
            error_count += 1
           
       
            print "ERRO %f" % (error_accum/error_count)
            print p
            print r
            print ""
            
            if error_count == 400:
                print "Numero de correctos %d" % correct
                break
          
           
        
        
def prompt():
    pass


#args.training = "./ml-100k/u.data"

load_dataSet(args.training)

#dataSet.getSVD(20)

#def predictionSVD(user,movie,k):
        #return baseline(user,movie) + sum(dataSet.U[user,]) + sum(dataSet.s) + sum(dataSet.V[movie,])
    
    
predict(args.test)
if args.online == True:
    prompt()




#print "1 - Expected 3: %f" %prediction('196','242')
#print "2 - Expected 3: %f" %prediction('186','302')
#print "3 - Expected 1: %f" %prediction('22','377')
#print "4 - Expected 2: %f" %prediction('244','51')
#print "5 - Expected 1: %f" %prediction('166','346')
#print "6 - Expected 4: %f" %prediction('298','474')
#print "7 - Expected 2: %f" %prediction('115','265')
#print "8 - Expected 5: %f" %prediction('253','465')
#print "9 - Expected 3: %f" %prediction('305','451')
#print "10 - Expected 3: %f" %prediction('6','86')