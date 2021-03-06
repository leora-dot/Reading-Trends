#HOW TO USE MINON:
    #MAKE SURE THAT BOSS SCRIPT IS ALREADY RUNNING
    #INIT MINON WITH REST API HOST & PORT (BOSS'S COMPUTER)
    #CALL KICKOFF

#import libraries
from bs4 import BeautifulSoup
import requests
import queue
import time
import threading

#import classes
from parser_script import Review_Parser, Book_Parser
from scraper_script import Scraper

class Minion():

    def __init__(self, max_sleep_time, host, port):

        self.scraper = Scraper()
        self.max_sleep_time = max_sleep_time
        self.id_queue = queue.Queue(maxsize=0)
        self.soup_tuple_queue = queue.Queue(maxsize=0)
        self.data_strings_queue = queue.Queue(maxsize=0)

        self.host = host
        self.port = port

        self.active = True

    def request_chunk(self):

        try:
            chunk_response = requests.get(self.api_url)

        except ConnectionError:
            print("ConnectionError in Request Chunk. Pausing")
            time.sleep(60)

        if self.is_chunk_none(chunk_response):
            self.active = False

        else:
            chunk_id_list = self.convert_chunk(chunk_response)
            for id in chunk_id_list:
                self.id_queue.put(id)

    def convert_chunk(self, chunk_response):

        old_chunk = chunk_response.content.decode()
        old_chunk = old_chunk.split(",")

        chars_to_remove = [",", "[", "]", " "]
        new_chunk = []

        for item in old_chunk:
            for char in chars_to_remove:
                item = item.replace(char,"")

            item = int(item)
            new_chunk.append(item)

        return new_chunk

    def data_transmission_loop(self):

        while self.active or (not self.data_strings_queue.empty()):

            data_string = self.data_strings_queue.get()

            try:
                requests.post(self.api_url, data = {"data_string": data_string})
                self.data_strings_queue.task_done()

            except ConnectionError:
                self.data_strings_queue.task_done()
                self.data_strings_queue.put(data_string)
                print("ConnectionError in Data Transmission Loop. Pausing...")
                sleep.time(60)

    def id_to_soup_tuple(self, id):
        url = self.base_url + str(id)

        webpage_as_string = self.scraper.url_to_string_content(url)
        soup = self.parser.html_to_soup(webpage_as_string)

        if not self.parser.is_soup_populated(soup): #IF RESPONSE IS INVALID
            num_invalid_responses_recieved = 1

            while self.parser.is_soup_populated(soup) == False:

                pausetime = 2.5 * 60 * 60
                print("{} invalid {} responses recieved. Pausing for {:.1f} minutes".format(num_invalid_responses_recieved, self.data_type, pausetime/60))

                time.sleep(pausetime)
                print("{} minion kicking off...".format(self.data_type))
                num_invalid_responses_recieved += 1

                webpage_as_string = self.scraper.url_to_string_content(url)
                soup = self.parser.html_to_soup(webpage_as_string)

        tuple = (id, soup)
        self.soup_tuple_queue.put(tuple)

    def sleep(self):

        self.scraper.sleep(self.max_sleep_time)

    def is_chunk_none(self, chunk):

        chunk = chunk.content.decode()

        if chunk == "":
            return True
        else:
            return False

    def parse(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def generate_data_string(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def data_scraping_loop(self):

        while self.active:

            if not self.id_queue.empty():
                id = self.id_queue.get()
                self.id_to_soup_tuple(id)
                self.id_queue.task_done()
                self.sleep()

            else:
                self.request_chunk()

    def data_parsing_loop(self):

        while self.active or (not self.soup_tuple_queue.empty()):
            self.parse()

    def kickoff(self):

        #GIVE SERVER TIME TO START UP
        print("{} minion sleeping...".format(self.data_type))
        time.sleep(40)
        print("{} minion kicking off...".format(self.data_type))

        #BACKGROUND THREADS
        active_threads = []

        for method in [self.data_scraping_loop, self.data_parsing_loop, self.data_transmission_loop]:
            thread = threading.Thread(target = method, daemon = True)
            active_threads.append(thread)
            thread.start()

        #BLOCK IN MAIN THREAD

        while self.active:
            time.sleep(1)

        for thread in active_threads:
            thread.join()

        print("{} data collected.".format(self.data_type))

class Review_Minion(Minion):

    def __init__(self, max_sleep_time, host, port):
        super().__init__(max_sleep_time, host, port)

        self.api_url = "http://{}:{}/api_review".format(self.host, self.port)
        self.base_url = "https://www.goodreads.com/review/show/"
        self.parser = Review_Parser()
        self.data_type = "review"

    def parse(self):

        if not self.soup_tuple_queue.empty():

            soup_tuple = self.soup_tuple_queue.get()
            id, soup = soup_tuple[0], soup_tuple[1]

            try:

                is_review_valid = self.parser.review_soup_is_valid(soup)

                if is_review_valid:
                    date = self.parser.review_soup_to_date(soup)
                    book_title = self.parser.review_soup_to_book_title(soup)
                    book_id = self.parser.review_soup_to_book_id(soup)
                    rating = self.parser.review_soup_to_rating(soup)
                    reviewer_href = self.parser.review_soup_to_reviewer_href(soup)

                    progress_dict = self.parser.review_soup_to_progress_dict(soup)
                    start_date = self.parser.progress_dict_to_start_date(progress_dict)
                    finished_date = self.parser.progress_dict_to_finish_date(progress_dict)
                    shelved_date = self.parser.progress_dict_to_shelved_date(progress_dict)

                else:
                    date = None
                    book_title = None
                    book_id = None
                    rating = None
                    reviewer_href = None
                    start_date = None
                    finished_date = None
                    shelved_date = None

                data_string = "{},{},{},{},{},{},{},{},{},{}".format(id, is_review_valid, date, book_title, book_id, rating, reviewer_href, start_date, finished_date, shelved_date)
                self.data_strings_queue.put(data_string)

            except AttributeError:

                print("Unable to parse {} id = {}. discarding soup".format(self.data_type, id))

            self.soup_tuple_queue.task_done()

class Book_Minion(Minion):

    def __init__(self, max_sleep_time, host, port):
        super().__init__(max_sleep_time, host, port)

        self.api_url = "http://{}:{}/api_book".format(self.host, self.port)
        self.base_url = "https://www.goodreads.com/book/show/"
        self.parser = Book_Parser()
        self.data_type = "book"

    def parse(self):

        if not self.soup_tuple_queue.empty():

            soup_tuple = self.soup_tuple_queue.get()
            id, soup = soup_tuple[0], soup_tuple[1]

            try:

                author = self.parser.book_soup_to_author(soup)
                language = self.parser.book_soup_to_language(soup)
                num_reviews = self.parser.book_soup_to_num_reviews(soup)
                num_ratings = self.parser.book_soup_to_num_ratings(soup)
                avg_rating = self.parser.book_soup_to_avg_rating(soup)
                isbn13 = self.parser.book_soup_to_isbn13(soup)
                editions_href = self.parser.book_soup_to_editions_href(soup)
                publication_date = self.parser.book_soup_to_publication_date(soup)
                first_publication_date = self.parser.book_soup_to_first_publication_date(soup)
                series = self.parser.book_soup_to_series(soup)

                data_string = "{},{},{},{},{},{},{},{},{},{},{}".format(id, author, language, num_reviews, num_ratings, avg_rating, isbn13, editions_href, publication_date, first_publication_date, series)

                self.data_strings_queue.put(data_string)

            except AttributeError:

                print("Unable to parse {} id = {}. discarding soup".format(self.data_type, id))

            self.soup_tuple_queue.task_done()

class Dual_Minion():

    def __init__(self, review_max_sleep_time, review_host, review_port, book_max_sleep_time, book_host, book_port):

        self.active = True
        self.review_minion = Review_Minion(review_max_sleep_time, review_host, review_port)
        self.book_minion = Book_Minion(book_max_sleep_time, book_host, book_port)

    def kickoff_book_minion(self):
        self.book_minion.kickoff()

    def kickoff_review_minion(self):
        self.review_minion.kickoff()

    def is_active_loop(self):

        while self.active:

            if len(self.active_threads) == 0:
                self.active = False

            else:

                for thread in self.active_threads:
                    if not thread.is_alive():
                        self.active_threads.remove(thread)

            time.sleep(60*5)

    def kickoff(self):

        self.active_threads = []

        for method in [self.kickoff_book_minion, self.kickoff_review_minion, self.is_active_loop]:
            thread = threading.Thread(target = method, daemon = True)
            self.active_threads.append(thread)
            thread.start()

        while self.active:
            time.sleep(1)

        print("All data collected. terminating")
        sys.exit()

#LOCAL
#host = "localhost"
#review_port, book_port = 8080, 80

#AWS DISTRIBUTED
host = '52.14.142.88'
review_port, book_port = 6000, 7000

review_time, book_time = 1, 115

test_dual_minion = Dual_Minion(review_time, host, review_port, book_time, host, book_port)
test_dual_minion.kickoff()
