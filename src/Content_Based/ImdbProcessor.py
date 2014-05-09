from imdb import helpers
from imdb import IMDb
import os.path
import json
import re
import string
import urllib2
import os
from urllib2 import HTTPError

from collections import Counter

#ia = imdb.IMDb('http')
#results = ia.search_movie('the passion')
##mv = results[0] #First result
##URL = ia.get_imdbURL(mv) #URL for first result
##print(URL)

def process_URLS(idMovieObj):
    ia = IMDb('mobile',useModule='lxml')
    
    for id, movie in idMovieObj.iteritems():
        
        m = {}
        newFile = "./DB/MovieDB/%s.json" % str(id)
        #Correctos 1313 para cima
        if os.path.exists(newFile):
            #print "Already processed %s " % str(id)
            continue
        
       
        
        print "Processing"
        try:
            print id
            r= urllib2.urlopen(movie.imdb_url)
        except HTTPError:
            print ("HTTP ERROR")
            continue
        except ValueError:
            print ("VALUE ERROR")
            continue
      
        try:
            movieUrl = r.url;
        except ValueError:
            continue

        print "Redirected"
        movieObj = helpers.get_byURL(movieUrl)

        if movieObj is None:
            continue


        print id
        try:
            m['Title'] = movieObj['title'].encode('utf8').lower()
        except KeyError:
            m['Title'] = ''
        try:
            m['Rating'] = str(movieObj['rating']).encode('utf8')
            
        except KeyError:
            m['Rating'] = ''

        try:
            m['Directors'] = []
            for director in movieObj['director']:
                m['Directors'].append(director['name'].encode('utf8').lower())
                
        except KeyError:
            m['Directors'] = []
        
        try:
            m['Writer'] = []
            print movieObj.get('writer')
            for writer in movieObj['writer']:
                m['Writer'].append(writer['name'].encode('utf8').lower())
                
        except KeyError:
            m['Writer'] = []

        try:
            m['Cast'] = []
            for actor in movieObj['cast']:
                m['Cast'].append(actor['name'].encode('utf8').lower())
        except KeyError:
            m['Cast'] = []

        try:
            
            m['Plot'] = []
            for plot in movieObj.get('plot'):
                m['Plot'].append(plot.encode('utf8').lower())
                
        except Exception:
            m['Plot'] = []
        try:
            ia.update(movieObj, 'synopsis')
            
            m['Synopsis'] = movieObj.get('synopsis').encode('utf8').lower()
           
        except Exception:
            m['Synopsis'] = ""
        try:
            ia.update(movieObj, 'keywords')
          
            
            m['Keywords'] = []
            
            for keyword in movieObj.get('keywords'):
                m['Keywords'].append(keyword.encode('utf8').lower())
        except Exception:
            m['Keywords'] = []
        
        
        file = open(newFile,'w')
        file.write(json.dumps(m, indent=True))
        file.close()
 

def getMissing(idMovieObj):

    ia = IMDb()
    
    path = "./missing.txt"
    file  = open(path, 'a')
    
    m = 0
    for id, movie in idMovieObj.iteritems():
        
        i = int(id)
        
        newFile = "./DB/MovieDB/%s.json" % str(i)
        if not os.path.exists(newFile):
            results = ia.search_movie(movie.title.strip())
            
            try:
                mv = results[0] #First result
            except IndexError:
                m += 1
                print "Missing %s" % (m)
                continue
            
            URL = ia.get_imdbURL(mv) #URL for first result
            movie.imdb_url = URL
           
            file.write(str(i) + " " + URL + "\n")
            file.flush()
            print(URL)
            #process_URLS(dict)
            #fileM.write(str(i) + " " + FullDict[i].imdb_url + "\n")
    
    file.close()
    print("Missing Done!")
    #process_URLS(idMovieObj)
            
            
def getCorrectUrls():
    path = ".//Missing.txt"
    fileM  = open(path, 'r')
    path = ".//Corrected.txt"
    fileC = open(path, 'w')
    for line in fileM.readlines():
        splittedBySpace = line.split(' ')[1]
        splittedByInt = splittedBySpace.split('?')[1]
        print(splittedByInt)
        #search = pygoogle(query=splittedByInt)
        #for key, url in search.search().iteritems():
            #print("key:%surl:%s\n" %(key,url))




def load_corrected_files(idMovieObj):
    
    path = "./corrected.txt"
    corrected  = open(path, 'r')
    for line in corrected.readlines():
        splitted = line.split(" ")
        idMovieObj[int(splitted[0])].imdb_url = splitted[1].strip()
        print  splitted[1].strip()
        
    process_URLS(idMovieObj)
    
    print "End Corrected"
    
def load_missing_files(idMovieObj):
    print "load missing files"
    path = "./missing.txt"
    corrected  = open(path, 'r')
    for line in corrected.readlines():
        splitted = line.split(" ")
        idMovieObj[int(splitted[0])].imdb_url = splitted[1].strip()
        print  "|%s|" % (splitted[1].strip())
        print "|%s|" % (splitted[0].strip())
        
    process_URLS(idMovieObj)


imdbRating = {}

import nltk
from nltk.corpus import stopwords
from nltk.stem import *
import math

token_dict = {}

tf = {}

def summary_tf(movie_id,summary):
    
    tf[movie_id] = {}
    
    for w in summary[movie_id]:
        if tf[movie_id].has_key(w): 
            tf[movie_id][w] += 1
        else :
            tf[movie_id][w] = 1


def summary_idf(word,summary):
    #tf_idf[movie_id]
    
   # print "idf"
    N = len(summary.keys())
    #print N

    div = 0
    for movie_id in summary.keys():
        if tf[movie_id].has_key(word):
            div += 1
    #print div
    return math.log(N+1/(1+div))   

def processDb():
    
    cachedStopWords = stopwords.words("english")
    stemmer = SnowballStemmer("english")
    
    persons = {}
    title = {}
    summary = {}
    keywords = {}
    
    for id in range(1,1683):
        
        dataFilePath = "./DB/MovieDB/%s.json" % str(id)
        
        #if not os.path.exists(dataFilePath):
            #continue
        
        dbfile = open(dataFilePath,'r')
        
        movieJSON = json.loads(dbfile.read().decode('utf8'))
        
        persons[id] = set()
        title[id] = ''
        summary[id] = ''
        
        #Title
        title[id] += movieJSON['Title'] + ' '
        
        #Ratings
        if movieJSON['Rating'] != '':
            imdbRating[int(id)] = float(movieJSON['Rating'])
        
        #print "|%s|"%(movieJSON['Rating'])
        
        #rating += movieJSON['Rating'] + ' '
        
        #Persons/names
        
        for director in movieJSON['Directors']:
            persons[id].add(director.replace(" ", ""))
        
        #for writer in movieJSON['Writer']:
            #persons.add(writer)
        
        c = 5 
        for actor in movieJSON['Cast'][:c]:
            persons[id].add(actor.replace(" ", ""))
                
        for p in movieJSON['Plot']:
            summary[id] +=  p + ' '
                 
        summary[id] += movieJSON['Synopsis'].replace("\n\n", "") + ' '
        
        
        keywords[id] = set()
        for kw in movieJSON['Keywords']:
            for w in kw.split('-'):
                keywords[id].add(w)    
        
        #remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        #no_punctuation = summary[id].translate(remove_punctuation_map)      
        #tokens = nltk.word_tokenize(no_punctuation)
        #print tokens
        
        #filtered = [w for w in tokens if not w in cachedStopWords]
        #print filtered
        
        #summary[id] = [stemmer.stem(w) for w in filtered]
        #print lemmatized

        #summary_tf(id,summary)
    
        print id
        
    for id in range(1,1683):
        
        destinationPath = "./DB/ProcessedDB/%s.txt" % str(id)
        
        #w_tf_idf = set()
        
        #if len(tf[id]) != 0:
            #maxF =  max(tf[id].values())
        
        #for w in summary[id]:
            #idf = summary_idf(w,summary) #w->idf, max idf
            #_tf = 0.5 + ((0.5*tf[id][w])/maxF)
            #tf_idf = _tf*idf
            #w_tf_idf.add( (w, tf_idf) )
    
    
        #sorted_list = sorted(w_tf_idf, key=lambda w: -w[1]) 
        print id
        
        #middle = int(len(sorted_list)//2)
        
        #print "len %s" % (len(sorted_list))
        #print "middle %s" % (middle)
        #print "sorted_list %s" % (sorted_list)
        
        #count = Counter(l)
        #temp = count.most_common(50)
        
        
        #k = len(sorted_list)*25//100
        
        #s = []
        #for w,c in sorted_list[:25]:
            #s.append(w)
            
        #print s
     
        newFile = open(destinationPath,'w') 
        newFile.write((' '.join(keywords[id])).encode('utf8'))
        newFile.close()
        #return
    
    
