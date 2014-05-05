from __future__ import division
import math
import numpy as np
from scipy.sparse import *
from scipy.spatial.distance import *
from Utils import *
from Content_Based import EADW_content_based
import numpy as np
from numpy import linalg

#########################################
######          UTILS               #####
#########################################

#X
features = []

#Y
relevants = []

def lregression(X,y):
    l = len(y)
    A = np.vstack([np.array(X).T, np.ones(l)])
    return linalg.lstsq(A.T,y)[0]

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
    return np.intersect1d(users_a, users_b)

moviesRatedBy = {}
def getMoviesRatedBy(user):
    
    if user in moviesRatedBy:
        return moviesRatedBy[user]
    
    movies = dataSet.getMoviesRatedBy(user)
    moviesRatedBy[user] = movies
    return movies


    


#########################################
######          BASELINE            #####
#########################################

##Recommeder Handbook

##pag.144 - bui = mean + bu + bi

def mean_rating():
    return dataSet.getMeanRating()



#Mean and Average
B = np.zeros((943+1,1683+1))
def z_score(user,movie):
    
    if B[user,movie] == 0:
        
        u = dataSet.getMeanUser(user)
        uv = dataSet.getVarUser(user)
        
        m = dataSet.getMeanMovie(movie)
        mv = dataSet.getVarMovie(movie)
    
       
        
        v = (0.5*mv+0.5*uv)
        
        if uv == 0:
            v = 1
        if mv == 0:
            v = 1
        
      
        B[user,movie] = (0.5*u + 0.5*m)/v
    
    return B[user,movie] 

#Cache do base_movie
b_m = {}

def base_movie(movie):
    
    if movie in b_m:
        return b_m[movie]
    
    mean = mean_rating()
    lambda2 =  25
    
    (s, n)  = dataSet.getUsersThatRateB(movie)

    res = s - n*mean
    
    res = res/(lambda2 + n)
    
    b_m[movie] = res
    
    return res 
            
#Cache do base_user
b_u = {}
def base_user(user):
    
    if user in b_u:
        return b_u[user]
    
    mean = mean_rating()
    lambda3 = 25
    accum = 0
    movies = getMoviesRatedBy(user)
    
    for movie in movies:
        accum += dataSet.getRating(user, movie) - mean - base_movie(movie)
    
    
    res = accum/(lambda3 + len(movies))
    
    b_u[user] = res

    return res


def baseline(user, movie):
    
    mean = mean_rating()
    #print "mean %f" % mean
    
    bm = base_movie(movie)
    #print "b_m %f" % bm
    
    bu = base_user(user)
    #print "b_u %f" % bu
    
    return mean + bm + bu

S = np.zeros((1682+1,1682+1),dtype=np.double)

def make_similiraty_func(distance_func,normalization_func,opt1,opt2):
    
    def similarity(m1,m2):
    
    
        if S[m1,m2] != 0 :
            return S[m1,m2]
        
        if S[m2,m1] != 0 :
            return S[m2,m1]
    
        U = getUsersThatRateAandB(m1,m2)
        
        #Optimizacao 1
        #Inverse User frequency
      
        
        #n_movies = dataSet.getMovies()
        
        n = len(U)
        temp1 = np.empty(n)
        temp2 = np.empty(n)
        
        index = 0
        for u in U:
            
            #print u
            v1 = dataSet.getRating(u,m1) + normalization_func(u,m1)
            v2 = dataSet.getRating(u,m2) + normalization_func(u,m2)
            
            
            #n1 = math.log(n_movies/len(getMoviesRatedBy(u)))
            #n2 = math.log(n_movies/len(getMoviesRatedBy(u)))
            
           
            
            t1 = v1
            t2 = v2
            
            
            if math.isnan(t1) or math.isnan(t1):
                print "Erro"
                print u
                print m1
                print m2
                return
            temp1[index] = t1
            temp2[index] = t2
            index += 1
        
      
        #Caso Especial nao existem utilizadores q avaliaram m1 e m2
        if n == 0:
            S[m1,m2] = None
            return None
        
        
        if len(temp1) > 0 and len(temp2) > 0 :
            sim = distance_func(temp1,temp2) + 1
        else:
            raise
            return -1
        
        
        if opt1 == True:
            #Optimizacao - Slide 20 (37/72)
            #tr-98-12.pdf
            p = 2.5
            sim = sim*math.pow(abs(sim),p-1)
            #print sim
           
        if opt2 == True:
            #Optimizacao  - Slide 19 (30/72)
            if(n <= 50):
                sim = (n/50)*sim
        
        S[m1,m2] = sim
        S[m2,m1] = sim 
    
        return sim        
    
    return similarity
    
def getMostSimilarMovies(user, movie,norm):
   
    k = 25
    sims = []
    
    cs = lambda u,v :  cosine(u,v) + 1
    #norm = lambda u,m : -1* baseline(u,m)
    
    similarity = make_similiraty_func(cs,norm,True, True)
    
    ratedByUser = dataSet.getMoviesRatedBy(user)
    
    #print len(ratedByUser)
    
    for m in ratedByUser:
        #print m
        #print movie
        s = similarity(m,movie)
        
        #se descartar negativos tenho menos erro
        
        if not s == None and not math.isnan(s) and s > 0:
            sims.append((m,s))
    

         
    sims = sorted(sims,key=lambda x: -abs(x[1]))

    #print sims
    return sims[0:k]
    
    
    
def make_prediction_func(most_similar_func, normalization_func, inverse_normalization_func):
    
    def  prediction(user,movie):
        
        
        
        divisor = 0
        dividendo = 0
        
        mostSimilar = most_similar_func(user,movie,normalization_func)
        
        for (m,s) in mostSimilar: 
            dividendo += s*(dataSet.getRating(user, m) + normalization_func(user, m))
            divisor += abs(s)
            #print m,s
        
        res = 0  
        if not divisor == 0:
            res = dividendo/divisor     
            
        return inverse_normalization_func(user,movie) + res
        
    #retorna funcao com o binding da funcao de similiridade e normalizacao    
    return prediction


def prediction_trainning(loader):
        return loader.load_dataSet(args.training)  

#w = [0.5,0.5,0]
def prediction_test(test_path, error_analisys):
    #global w
    with open(test_path) as u_test_file:
        u_tests = u_test_file.readlines()
        
        for test in u_tests:
            (user_id, movie_id, rating, timestamp) = test.split("\t")
            
            true_r = int(rating)
            u = int(user_id)
            m = int(movie_id)
            
            
            n = lambda u,m: -1*baseline(u,m)
            pred_func = make_prediction_func(getMostSimilarMovies,n,baseline) 
            
            item_based_r = pred_func(u,m)
            #content_based_r = EADW_content_based.evaluate(u,m)
            
           
          
            predicted_r = 1*item_based_r
            #1*content_based_r
            
            #features.append((item_based_r, content_based_r))
            #relevants.append(true_r)
            #w = lregression(features,relevants)
            #print w
          
            
            diff = error_analisys.collect(true_r, predicted_r)
            
            print error_analisys.getCountError()
            print predicted_r
            print true_r
            print "ERRO %f" % error_analisys.getMeanAbsoluteError()
            print "Numero de correctos %d" % error_analisys.getNCorrects()
            print ""
            
            #if diff > 2.0:
                #print u
                #print m
                #print "end"
                #return
            
                
        print "end"
        
def prompt():
    pass



if __name__ == "__main__":
    
    p = ArgParser()
    args = p.parse()
    print "Argumentos:%s"%(args)
    
    loader = Loader()
    dataSet = prediction_trainning(loader)
    
    error_analisys = Error_Analisys()
    
    prediction_test(args.test,error_analisys)
    
    
    if args.online == True:
        prompt()
        