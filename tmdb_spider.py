import scrapy 

class TmdbSpider(scrapy.Spider):
    
    name = "tmdb_spider" # we need a unique name for each class we created in order to do scrapy.
    
    # the following 3 are setups:
    # start_urls is the page we want to start looking at, i.e. the page of your favorite movie.
    # orig_url is the domain of TMDB website; we will use it to get new urls for each actor.
    # number_map is for cases when "Acting" table of an actor is not the first table: this is rare but
    # does exist.
    start_urls = ["https://www.themoviedb.org/movie/671-harry-potter-and-the-philosopher-s-stone"]
    orig_url = "https://www.themoviedb.org"
    number_map = {0: "zero",
                  1: "one",
                  2: "two",
                  3: "three",
                  4: "four",
                  5: "five"}
    
    
    def parse(self, response):
        '''
        Assume that we start on a movie page, and then this function will help us navigate to the Full Cast & Crew page.
        
        @param response: this allow us to do operations to get what we want.
        
        @rtype: no return value, but yield another function for further steps. 
        '''
        
        cast_page = self.start_urls[0] + "/cast" # url for cast page
        
        yield scrapy.Request(cast_page, callback = self.parse_full_credits)
    
    
    def parse_full_credits(self, response):
        '''
        Aassume that we start on the Full Cast & Crew page. This function will nevigate us to the page of each actor. Crew members are not included.
        
        @param response: this allow us to do operations to get what we want.
        
        @rtype: no return value, but yield another function for further steps.
        '''
        
        casts = response.css("ol.people.credits")[0] # the actors are in the first table of the page
        
        # we want to get information of every actor, so we need a for loop.
        for name in casts.css("div.info a"):
            new_url = self.orig_url + name.attrib["href"]
            yield scrapy.Request(new_url, callback = self.parse_actor_page) 
            
    
    def parse_actor_page(self, response):
        '''
        Assume that we start on the page of an actor. This function will yield a dictionary such that each of the movies or TV shows on which that actor has worked will be presented. We will focus on the Acting table.
        
        @param response: this allow us to do operations to get what we want.
        
        @rtype: no return value, but yield the described dictionary.
        '''
        
        # get the name of actors
        name_list = response.url.split('-')
        name = " ".join(name_list[1:])
        
        # sometimes Acting table is not the first one in the page. 
        # we only want the Acting table, so we need to check
        check = response.css("div.credits_list")
        h3 = check.css("h3")
        acting_number = 0
        for i in range(len(h3)):
            if h3[i].css("h3.{}::text".format(self.number_map[i])).get() == "Acting":
                acting_number = i
                break
                
        acting = response.css("table.card.credits")[acting_number] # Acting table
        
        # retrieve information and yield as a dictionary
        for movie_name in acting.css("table.credit_group"):
            movie = movie_name.css("a.tooltip bdi::text").getall()
            for i in movie:
                yield {"actor_name" : name,
                       "movie_or_TV_show": i}