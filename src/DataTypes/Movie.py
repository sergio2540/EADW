#########################################
######          MOVIES              #####
#########################################


class Movie:
    
    def __init__(self,movie_id,title,release_date,video_release_date,imdb_url,genres):
        self.movie_id = int(movie_id)
        self.title = title
        self.release_date = release_date
        self.video_release_date = video_release_date
        self.imdb_url = imdb_url
        self.genres = genres
        self.id_String_Genres = {}
        self.user_votes = {}
        self.votes_sum = 0
        self.votes_num = 0

    
    def __str__(self):
        return "Movie id : %d Title: %s Release: %s Video Release %s IMDB URL: %s Genres %s"  % (self.movie_id,self.title, self.release_date, self.video_release_date, self.imdb_url,self.genres)

    def genreStringRep(self):
        repString = ""
        for genre_Id, genre_String in self.id_String_Genres.iteritems():
            repString += (genre_String + "|")
        return repString
    