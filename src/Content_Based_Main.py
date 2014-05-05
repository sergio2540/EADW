from __future__ import division
import math
from Utils import *
from Content_Based import EADW_content_based

def prediction_trainning(loader):
        return loader.load(args.training)  



def prediction_test(test_path, error_analisys, c):
    gotIt = 0
    gaveMore = 0
    gaveLess = 0
    #global w
    file = open("Compare",'w+')
    

    
    with open(test_path) as u_test_file:
        u_tests = u_test_file.readlines()
        
        for test in u_tests:
            (user_id, movie_id, rating, timestamp) = test.split("\t")
            
            true_r = int(rating)
            u = int(user_id)
            m = int(movie_id)
            
            
            predicted_r = c.evaluate(u,m)
         
            diff = error_analisys.collect(true_r, predicted_r)
            
          
            print "ERROR STATUS"
            print error_analisys.getCountError()

            if predicted_r == true_r:
                gotIt += 1
            if predicted_r > true_r:
                gaveMore += 1
            if predicted_r < true_r:
                gaveLess += 1
            file.write("User:%s Evaluated:%s" %(user_id, movie_id))
            file.write("Predicted:%f" % predicted_r)

            print u
            print m

            print predicted_r
            file.write("True:%f" % true_r)
            print true_r
            print "ERRO %f" % error_analisys.getMeanAbsoluteError()
            print "Numero de correctos %d" % error_analisys.getNCorrects()
            print ""
            
        print ("Correct:%d Above:%d Under:%d" %(gotIt, gaveMore, gaveLess))     
        print "end"
        
def prompt():
    pass


if __name__ == '__main__':
    p = ArgParser()
    args = p.parse()
    print "Argumentos:%s"%(args)
    
    loader = Loader()
    _data= prediction_trainning(loader)
    
    error_analisys = Error_Analisys()
    print _data.movies

    c = EADW_content_based.Content_Based(_data.data,_data.users, _data.movies)
    
    prediction_test(args.test,error_analisys,c)
    
    
    if args.online == True:
        prompt()