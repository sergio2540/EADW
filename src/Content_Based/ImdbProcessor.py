from imdb import helpers
from imdb import IMDb
import os.path
import json
import re
import string
import urllib2
import os
from urllib2 import HTTPError

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

from nltk.corpus import stopwords

def processDb():
    
     

    cachedStopWords = stopwords.words("english")
    
    for i in range(1,1683):
        
        dataFilePath = "./DB/MovieDB/%s.json" % str(i)
        destinationPath = "./DB/ProcessedDB/%s.txt" % str(i)
        
        #if not os.path.exists(dataFilePath):
            #continue
        
        dbfile = open(dataFilePath,'r')
        
        movieJSON = json.loads(dbfile.read().decode('utf8'))
        
        rating = ''
        
        persons = ''
        
        summary = ''
        
        #Ratings
        if movieJSON['Rating'] != '':
            imdbRating[int(i)] = float(movieJSON['Rating'])
        
        #print "|%s|"%(movieJSON['Rating'])
        
        rating += movieJSON['Rating'] + ' '
        
        #Persons/names
        
        for director in movieJSON['Directors']:
                persons +=  director + ' '
        
        for writer in movieJSON['Writer']:
            persons +=  writer + ' '
        
        
        for actor in movieJSON['Cast']:
            persons +=  actor + ' '
            
            
        summary += movieJSON['Title'] + ' '

        
                
        for p in movieJSON['Plot']:
            summary +=  p + ' '
                 
        summary += movieJSON['Synopsis'].replace("\n\n", "") + ' '
        
        for kw in movieJSON['Keywords']:
            for w in kw.split('-'):
                summary +=  w + ' '    
        
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        summary = regex.sub('',  summary)
        toWrite = ' '.join([word for word in summary if word not in cachedStopWords]) 
           
            
        newFile = open(destinationPath,'w') 
        newFile.write(toWrite.encode('utf8'))
        newFile.close()
