#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import random
import pandas as pd
import math
import sys 

#import classes

from parser_script import Review_Parser
from scraper_script import Scraper
from data_collection_script import Review_Detail_Data_Collector

class Review():

    def __init__(self, id, is_valid, date, book_title, book_id, rating, reviewer_href, start_date, finished_date, shelved_date):
        self.id = review_id
        self.is_valid = is_valid
        self.date = date
        self.book_title = book_title
        self.book_id = book_id
        self.rating = rating
        self.reviewer_href = reviewer_href
        self.start_date = start_date
        self.finished_date = finished_date
        self.shelved_date = shelved_date

    def get_data(self):
        data = "{},{},{},{},{},{},{},{},{},{}".format(str(self.id), self.is_valid, self.current_date, self.book_title, self.book_id, self.rating, self.reviewer_href, self.start_date, self.finished_date, self.shelved_date)
        return data

class Book():

    def __init__(self, book_id, author, language, num_reviews, num_ratings, avg_rating, isbn13, editions_url,publication_date,first_publication_date,series,log_time):
        self.id = book_id
        self.author = author
        self.language = language
        self.num_reviews = num_reviews
        self.num_ratings = num_ratings
        self.avg_rating = avg_rating
        self.isbn13 = isbn13
        self.editions_url = editions_url
        self.publication_date = publication_date
        self.first_publication_date = first_publication_date
        self.series = series

    def get_data(self):
        data = "{},{},{},{},{},{},{},{},{},{},{}".format(self.id, self.author, self.language, self.num_reviews, self.num_ratings, self.avg_rating, self.isbn13, self.editions_url, self.publication_date, self.first_publication_date, self.series)
        return data

class Boss():

    def __init__(self, assignment_size, file_name, boss_type):

        if boss_type == "book":
            self.data_type = "Books"
            id_column_name = "book_id"

        elif boss_type == "review":
            self.data_type = "Reviews"
            id_column_name = "ID"

        self.assignment_size = assignment_size
        self.log_file_name = "databases/"+ file_name + ".csv"

        print("Boss Initiated & Awaiting Input Data Request")

#PREPARATION METHODS

    def is_csv(self):

        try:
            df = pd.read_csv(self.log_file_name, low_memory=False)
            is_csv = True

        except (FileNotFoundError, pd.errors.EmptyDataError):
            is_csv = False

        return is_csv

    def input_data_request(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def prepare_scope(self):

        if self.is_csv():

            data_logged_at_start = pd.read_csv(self.log_file_name)
            already_scraped = self.data_logged_at_start[id_column_name].unique()
            already_scraped = [str(id) for id in self.already_scraped]

            self.to_be_scraped = []

            for id in self.requested:

                if id not in already_scraped:
                    self.to_be_scraped.append(id)

        else:

            self.to_be_scraped = self.requested

        if not self.to_be_scraped:
            print("All Requested Data Already In Log")
            return

        random.shuffle(self.to_be_scraped)

        self.num_points_to_be_scraped = len(self.to_be_scraped)
        self.num_points_scraped = 0

    def generate_assignments(self):

        num_to_be_scraped = len(self.to_be_scraped)
        num_assignments = math.ceil(num_to_be_scraped/assignment_size)

        self.outstanding_assignment_key_list = [num for num in range(0, num_assignments - 1)]
        self.assignment_dict = {}

        for assignment in self.outstanding_assignment_key_list:
            assignment_ids = self.outstanding_assignment_key_list[assignment: assignment + assignment_size]
            self.assignment_dict[assignment] = assignment_ids

    def prepare_for_minions(self):

        if not self.requested:
            print("Boss Requires Data Request Prior to Preparing for Minions")
            return

        self.prepare_scope()
        self.prepare_log_file()
        self.generate_assignments()

        print("Boss is Ready to Recieve Requests from Minions")

#PREPARING LOG FILE METHODS

    def add_headers_to_log_file(self):

        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def prepare_log_file(self):

        if self.is_csv():
            self.open_log_file()

        else:

            self.open_log_file()
            self.add_headers_to_log_file()

        self.datafile.close()
        print("Log File Ready")

    def open_log_file(self):

        self.datafile = open(self.log_file_name, "a")

#COMMUNICATE WITH MINIONS METHODS

    def give_assignment(self):

        if self.outstanding_assignment_key_list:
            assignment_key = assignment_key_list[0]
            self.outstanding_assignment_key_list = assignment_key_list[1:]
            self.outstanding_assignment_key_list.append(assignment)

        else:
            assignment_key = None

        if assignment_key:
            assignment_ids = assignment_dict.get(assignment)
        else:
            assignment_ids = None

        return assignment_key, assignment_ids

#LOG DATA METHODS

    def input_data(self, assignment_key, data_nodes):

        self.open_log_file()
        self.generate_datetime()

        for node in data_nodes:
            log_data_point(data_node)

        self.datafile.close()
        self.complete_assignment(assignment_key)

        self.num_points_scraped += len(data_nodes)
        self.print_progress()

    def log_data_point(self, data_node):
        data = data_node.get_data()

        self.datafile.write("\n{},{}".format(data, self.now_string))

    def complete_assignment(self, assignment_key):

        try:
            self.outstanding_assignment_key_list.remove(assignment_key)

        except ValueError:
            pass

## PROGRESS METHODS

    def generate_datetime(self):

        now = datetime.now()
        self.now_string = now.strftime("%m/%d/%Y %H:%M:%S")

    def print_progress(self):
        percent_complete = round(100 * self.num_points_scraped / self.num_points_to_be_scraped, 2)
        percent_complete_string = str(self.percent_complete)

        print("{} / {} {} Collected ({}% Complete) at {}". format(str(self.num_points_scraped), str(self.num_points_to_be_scraped), self.data_type, percent_complete_string, self.now_string))

class Review_Boss(Boss):

    def __init__(self, assignment_size, file_name):
        super().__init__(assignment_size, file_name, "review")

    def input_data_request(self, min_id, max_id):
        self.requested = range(min_id, max_id)

        print("Boss Recieved Data Request & Ready to Prepare for Minions")

    def add_headers_to_log_file(self):

        self.datafile.write("ID,is_URL_valid,review_publication_date,book_title,book_id,rating,reviewer_href,started_reading_date,finished_reading_date,shelved_date,log_time")

class Book_Boss(Boss):

    def __init__(self, assignment_size, file_name):
        super().__init__(assignment_size, file_name, "book")

    def input_data_request(self, book_list):
        self.requested = book_id_list

        print("Boss Recieved Data Request & Ready to Prepare for Minions")

    def add_headers_to_log_file(self):

        self.datafile.write("book_id,author,language,num_reviews,num_ratings,avg_rating,isbn13,editions_url,publication_date,first_publication_date,series,log_time")

class Minion():

    def __init__(self, boss, max_sleep_time, minion_type):

        if minion_type == "book":
            self.base_url = "https://www.goodreads.com/book/show/"
            self.parser = Book_Parser()

        if minion_type == "review":
            self.base_url = "https://www.goodreads.com/review/show/"
            self.parser = Review_Parser()

        else:
            return "Error: Invalid Minion Type"

        self.boss = boss
        self.scraper = Scraper()
        self.max_sleep_time = max_sleep_time
        self.collected_data = []

    def request_assignment(self):
        self.assignment_key, self.assignment_ids = self.boss.give_assignment()

    def generate_current_url(self):
        self.current_url = self.base_url + str(self.current_id)

    def parse(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def generate_data_node(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def scrape_url(self):

        self.current_webpage_as_string = self.scraper.url_to_string_content(self.current_url)

    def generate_soup(self):

        self.current_soup = self.parser.html_to_soup(self.current_webpage_as_string)

        invalid_count = 0

        while self.parser.is_soup_populated(self.current_soup) == False:

            if invalid_count < 10:
                self.generate_datetime()
                print("Recieved Invalid Response from Website. Pausing Data Collection at {}...".format(self.self.now_string))

                pause_time = max(self.max_sleep_time, invalid_count*60) #IF IT'S THE FIRST ERROR, REGULAR SLEEPTIME. FOR SUBSEQUENT ERRORS, INCREASINGLY LARGE WAIT TIMES.
                self.sleep(pause_time)

                self.generate_datetime()
                print("Restarting Data Collection at {}...".format(self.now_string))
                self.current_soup = self.parser.html_to_soup(self.current_webpage_as_string)

                invalid_count += 1

            else:

                print("Too Many Invalid Requests Recieved. Terminating Data Collection.")
                sys.exit()

    def log_data(self):
        self.collected_data.append(self.current_data_node)

    def sleep(self, max_sleep_time = None):

        if max_sleep_time:
            sleeptime = max_sleep_time
        else:
            sleeptime = self.max_sleep_time

        self.scraper.sleep(sleeptime)

    def transmit_data_to_boss(self):

        self.boss.input_data(self.assignment_key, self.collected_data)
        self.collected_data = []

    def collect_assigned_data(self):

        for id in self.assignment_ids:
            self.current_id = id
            self.generate_current_url()
            self.scrape_url()
            self.generate_soup()
            self.parse()
            self.log_data()
            self.sleep()

    def data_collection_loop(self):
        self.request_assigment()

        while self.assignment_key():
            self.collect_assigned_data()
            self.transmit_data_to_boss()
            self.request_assignment()

        sys.exit()

class Review_Minion(Minion):

    def __init__(self, boss, max_sleep_time):
        super().__init__(boss, max_sleep_time, "review")

    def parse(self):

        self.is_current_valid = self.parser.review_soup_is_valid(self.current_soup)

        if self.is_current_valid:
            self.current_date = self.parser.review_soup_to_date(self.current_soup)
            self.current_book_title = self.parser.review_soup_to_book_title(self.current_soup)
            self.current_book_id = self.parser.review_soup_to_book_id(self.current_soup)
            self.current_rating = self.parser.review_soup_to_rating(self.current_soup)
            self.current_reviewer_href = self.parser.review_soup_to_reviewer_href(self.current_soup)

            self.current_progress_dict = self.parser.review_soup_to_progress_dict(self.current_soup)
            self.current_start_date = self.parser.progress_dict_to_start_date(self.current_progress_dict)
            self.current_finished_date = self.parser.progress_dict_to_finish_date(self.current_progress_dict)
            self.current_shelved_date = self.parser.progress_dict_to_shelved_date(self.current_progress_dict)

        else:
            self.current_date = None
            self.current_book_title = None
            self.current_book_id = None
            self.current_rating = None
            self.current_reviewer_href = None
            self.current_start_date = None
            self.current_finished_date = None
            self.current_shelved_date = None

    def generate_data_node(self):

        self.current_data_node = Review(self.current_id, self.is_current_valid, self.current_date, self.current_book_title, self.current_book_id, self.current_rating, self.current_reviewer_href, self.current_start_date, self.current_finished_date, self.current_shelved_date)

class Book_Minion(Minion):

    def __init__(self, boss, max_sleep_time):
        super().__init__(boss, max_sleep_time, "book")
