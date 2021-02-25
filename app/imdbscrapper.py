import re

from selenium import webdriver


class IMDBScrapper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=options)

        self.movie_url = "https://www.imdb.com/title/tt{}/"
        self.movie_credits_url = "https://www.imdb.com/title/tt{}/fullcredits"
        self.actor_url = "https://www.imdb.com/name/nm{}/"

        self.movie_exclusions = re.compile(
            r'\(Short|TV\sSeries|TV\sMovie|pre\-production|post\-production|completed|announced|\)'
        )

    def get_movie_info(self, movie_id):
        self.browser.get(self.movie_credits_url.format(movie_id))

        title_header = self.browser.find_element_by_xpath('//div[@class="subpage_title_block"]/div/div/h3')
        title = title_header.find_element_by_xpath('./a').text
        year = title_header.find_element_by_xpath('./span').text[1:-1].strip()

        cast_list = self.browser.find_elements_by_xpath(
            '//table[@class="cast_list"]//tr[contains(@class, "odd") or contains(@class, "even")]',
        )

        cast = {}
        for row in cast_list:
            actor_link_element = row.find_element_by_xpath('./td[2]/a')
            actor_name = actor_link_element.text
            character = row.find_element_by_xpath('./td[@class="character"]').text
            actor_id = actor_link_element.get_attribute('href').split('/')[4][2:]
            cast[actor_id] = {
                'actor_name': actor_name,
                'character': character,
            }

        neigbors = dict()
        for actor_id in cast.keys():
            actor_info = self.get_actor_info(actor_id)
            # for movie_id, value in actor_info['filmography'].items():
            #     if movie_id not in neigbors.keys(): # add common actors
            #         value['common_actors'] = {actor_info['actor_id']: actor_info['actor_name']}
            #     else: # update common actors
            #         value['common_actors'].update({actor_info['actor_id']: actor_info['actor_name']})

            #     neigbors.update({movie_id: value})
                

            neigbors.update(actor_info['filmography'])
        
        rating, rating_count = self.get_movie_rate(movie_id)

        movie = {
            'movie_id': movie_id,
            'title': title,
            'year': year,
            'rating': float(rating),
            'rating_count': int(rating_count),
            'cast': cast,
            'neigbors': neigbors,
        }

        return movie

    def get_movie_rate(self, movie_id):
        self.browser.get(self.movie_url.format(movie_id))

        rating_element = self.browser.find_element_by_xpath('//div[@class="ratings_wrapper"]//div[@class="imdbRating"]')
        rating = rating_element.find_element_by_xpath('.//span[@itemprop="ratingValue"]').text
        rating_count = rating_element.find_element_by_xpath('./a').text.replace(',', '')
        
        return rating, rating_count

    def get_actor_info(self, actor_id):
        self.browser.get(self.actor_url.format(actor_id))

        name = self.browser.find_element_by_xpath('//div[@id="name-overview-widget"]//h1').text
        
        filmo_list = self.browser.find_elements_by_xpath(
            '//div[@id="filmography"]/div[@class="filmo-category-section"][1]/div[contains(@class, "filmo-row")]',
        )

        filmography = {}
        for row in filmo_list:
            movie_info = row.text
            if self.movie_exclusions.search(movie_info):
                continue
            try:
                movie_year, movie_name, character = movie_info.split('\n')
            except ValueError:
                print("Skipped and entry:", name, movie_info.replace('\n', ', '))
                pass
            else:
                movie_id = row.find_element_by_xpath('./b/a').get_attribute('href').split('/')[4][2:]
                filmography[movie_id] = {
                    'movie_name': movie_name,
                    'movie_year': movie_year,
                    'character': character,
                }

        actor = {
            'actor_id': actor_id,
            'actor_name': name,
            'filmography': filmography,
        }

        return actor

    def cleanup(self):
        self.browser.quit()
