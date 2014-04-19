from imdb import helpers
from imdb import IMDb
import urllib2
from sets import Set
import os
from urllib2 import HTTPError
##ia = imdb.IMDb('http')
##results = ia.search_movie('the passion')
##mv = results[0] #First result
##URL = ia.get_imdbURL(mv) #URL for first result
##print(URL)

def process_URLS(idMovieObj):
    #imdbInst = IMDb()

    for id, movie in idMovieObj.iteritems():
        
      
        try:
            r= urllib2.urlopen(movie)
        except HTTPError:
            continue
            print ("HTTP ERROR")
        except ValueError:
            continue
        try:
            movieUrl = r.url;
        except ValueError:
            continue


        movieObj = helpers.get_byURL(movie.imdb_url)

        if movieObj is None:
            continue

        newFile = ".//Corrected//%s.txt" % str(id)
        file = open(newFile,'w')
        try:
            file.write("Title:\n")
            file.write(movieObj['title'].encode('utf-8') + "\n\n")

        except KeyError:
            file.write("\n")
        try:
            file.write("Rating:\n")
            file.write(str(movieObj['rating']).encode('utf-8') + "\n\n")

        except KeyError:
            file.write("\n")

        try:
            file.write("Directors:\n")
            for director in movieObj['director']:
                file.write(director['name'].encode('utf-8') + "\n")
            file.write("\n")

        except KeyError:
            file.write("\n")

        try:
            file.write("Cast:\n")
            for actor in movieObj['cast']:
                file.write(actor['name'].encode('utf-8') + "\n")
            file.write("\n")
        except KeyError:
            file.write("\n")

        try:
            file.write("Plot:\n")
            file.write(movieObj['plot outline'].encode('utf-8'))

        except KeyError:
            file.close()
            continue
        file.close()

def getMissing(FullDict):

    ia = IMDb()
    

    path = ".//Missing.txt"
    fileM  = open(path, 'w')
    dict = {}
    for i in range(1,1683):
        newFile = ".//MovieDB//%s.txt" % str(i)
        if not os.path.exists(newFile):
            results = ia.search_movie(FullDict[i].title.strip())
            try:
                mv = results[0] #First result
            except IndexError:
                continue
            URL = ia.get_imdbURL(mv) #URL for first result
            dict[i] = URL
            fileM.write(str(i) + " " + URL + "\n")
            #fileM.write(str(i) + "\n")
            print(URL)
    #process_URLS(dict)
            #fileM.write(str(i) + " " + FullDict[i].imdb_url + "\n")
            
def getCorrectUrls():
    path = ".//Missing.txt"
    fileM  = open(path, 'r')
    path = ".//Corrected.txt"
    fileC = open(path, 'w')
    for line in fileM.readlines():
        splittedBySpace = line.split(' ')[1]
        splittedByInt = splittedBySpace.split('?')[1]
        print(splittedByInt)
        search = pygoogle(query=splittedByInt)
        for key, url in search.search().iteritems():
            print("key:%surl:%s\n" %(key,url))


def createFiles():
    path = ".//Missing.txt"
    fileM  = open(path, 'r')
    dict = {}
    for line in fileM.readlines():
        splitted = line.split(" ")
        dict[int(splitted[0])] = splitted[1]
    process_URLS(dict)
    return dict

imdbRating = {}

def processDb():
    for i in range(1,1683):
        dataFilePath = "./DB/MovieDB/%s.txt" % str(i)
        destinationPath = "./DB/ProcessedDB/%s.txt" % str(i)
        dbfile = open(dataFilePath,'r')
        fileContent = dbfile.read()
        byNewLine = fileContent.split("\n\n")
        toWrite = ""
        newFile = open(destinationPath,'w+')

        for intermediate in byNewLine:
            topic = intermediate.split("\n")
            if topic[0] == "Rating:" and len(topic) > 1:
                imdbRating[i] = float(topic[1])
                continue
            #print("Id:%d Value:%s" % (i,float(topic[1])))
            for data in topic[1:]:
                toWrite += data + "\n"
        newFile.write(toWrite)
        newFile.close()

#print (imdbRating)

#process_URLS(createFiles())