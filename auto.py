from scrapex import *
import time
import sys
import json
import urlparse
import re, csv
import city
import mysql_manage as db
import config_scrapy as config
from datetime import datetime
from datetime import date
import city
from time import sleep
from item import CraigsscraperItem
from scrapex import common
from scrapex.node import Node
from scrapex.excellib import *

s = Scraper(
    use_cache=False, #enable cache globally
    retries=10,
    timeout=60,
    proxy_file = 'proxy.txt',
    )

logger = s.logger

parent_url = 'https://www.booking.com/searchresults.html'
start_urls = []
product_list = []
item_list = []
total_item_list = []

news_item_cnt = 0
save_item_cnt = 0

hotel_list_file = "hotel_list.csv"
hotel_detail_file = "hotel_detail.csv"

checkin_month =5
checkin_monthday =9
checkin_year =2017

place = "Singapore"
no_rooms = 1
group_adults = 2

period_day = 7

def get_hotel_list():
    global news_item_cnt, checkin_monthday, save_item_cnt
    headers={
        'Host': 'www.booking.com',
    }
    
    for period in range(0, period_day):
        news_item_cnt = 0
        logger.info("Total Items: {}".format(save_item_cnt))

        checkin_monthday += 1

        checkin_str = "&checkin_month={}&checkin_monthday={}&checkin_year={}".format(checkin_month, checkin_monthday, checkin_year)
        checkout_str = "&checkout_month={}&checkout_monthday={}&checkout_year={}".format(checkin_month, checkin_monthday + 1, checkin_year)
        other_str = "&room1=A%2CA&no_rooms={}&group_adults={}&group_children=0".format(no_rooms, group_adults)

        url = "{}?sb=1&src=searchresults&src_elem=sb&ss={}{}{}{}".format(parent_url, place, checkin_str, checkout_str, other_str)

        while (url != ""):
            if news_item_cnt > 50: 
                break;

            html = s.load(url, use_cache=False, headers = headers)
            proxy = html.response.request.get("proxy")
            logger.info(proxy.full_address)

            href_links = html.q("//div[contains(@class,'sr_item sr_item_new')]")
            if len(href_links) > 0:
                for row in href_links:
                    title = row.q(".//h3[contains(@class,'sr-hotel__title')]/a")
                    hotel_link = title[0].x("@href").strip()
                    hotel_name = title[0].x("span[@class='sr-hotel__name']/text()").strip()
                    
                    item = [
                        'place', place,
                        'check_in', "{}/{}/{}".format(checkin_monthday, checkin_month, checkin_year),
                        'check_out', "{}/{}/{}".format(checkin_monthday + 1, checkin_month, checkin_year),
                        'hotel name', hotel_name,
                        'no_rooms', no_rooms,
                        'group_adults', group_adults,
                        'hotel_link', hotel_link,
                    ]

                    news_item_cnt += 1

                    s.save(item, hotel_list_file)

                logger.info("New Items: {}".format(news_item_cnt))

            next_div = html.q("//a[contains(@class, 'paging-next')]")
            
            if len(next_div) == 0:
                url = ""
            else:
                url = next_div[0].x("@href")

        save_item_cnt += news_item_cnt

def get_hotel_detail():
    
    hotel_list = []
    with open(hotel_list_file) as csvfile:
        reader = csv.reader(csvfile)
        
        for i,item in enumerate(reader):
            if i > 1:
                hotel_info = {}
                hotel_info["place"] = item[0]
                hotel_info["check_in"] = item[1]
                hotel_info["check_out"] = item[2]
                hotel_info["hotel_name"] = item[3]
                hotel_info["no_rooms"] = item[4]
                hotel_info["group_adults"] = item[5]
                hotel_info["hotel_url"] = item[6]
                hotel_info["star_rating"] = ""
                hotel_info["address"] = ""
                hotel_info["review_score"] = ""
                hotel_info["review_score_breaks"] = ""
                hotel_info["review_count"] = ""

                hotel_list.append(hotel_info)

    
    for hotel_info in hotel_list:
        hotel_url = hotel_info['hotel_url']

        html = s.load(hotel_url, use_cache=False)
        
        #address
        address_div = html.q("//span[contains(@class, 'hp_address_subtitle')]")
        address = ""
        if len(address_div) > 0:
            address = address_div[0].x("text()").encode("utf8").strip()

        hotel_info["address"] = address

        #review part
        review_btn = html.q("//a[@class='show_all_reviews_btn']")

        review_url = ""
        if len(review_btn) > 0:
            review_url = review_btn[0].x("@href").strip()
            review_html = s.load(review_url, use_cache = False)
            # with open("response.html", 'w') as f:
            #     f.write(review_html.encode('utf-8'))
            # return
                        
            review_score_div = review_html.q("//div[@class='review_list_score']")
            review_score = ""
            if len(review_score_div) > 0:
                review_score = review_score_div[0].x("text()").strip()

            hotel_info["review_score"] = review_score

            review_score_break_down = review_html.q("//ul[@id='review_list_score_breakdown']/li")
            review_score_breaks = []
            for row in review_score_break_down:
                score_name = row.x("p[@class='review_score_name']/text()").encode('utf8').strip()
                score_value = row.x("p[@class='review_score_value']/text()").encode('utf8').strip()
                review_score_breaks.append({score_name:score_value})

            hotel_info["review_score_breaks"] = str(review_score_breaks)

            #review count
            review_count_div = review_html.q("//meta[@itemprop = 'ratingCount']")
            review_count = 0

            if len(review_count_div) > 0:
                review_count = review_count_div[0].x("@content").encode("utf8").strip()

            hotel_info["review_count"] = review_count

            #star rating
            star_div = review_html.q("//i[contains(@class,'star_track')]")
            star_rating = ""
            if len(star_div) > 0:
                star_rating = star_div[0].x("@title").encode("utf8").strip()

            hotel_info["star_rating"] = star_rating
        
        output = []
        for key in hotel_info.keys():
            output.append(key)
            output.append(hotel_info[key])

        s.save(output, hotel_detail_file)

if __name__ == '__main__':
    #get_hotel_list()
    get_hotel_detail()
    logger.info("************************************")
    logger.info("************************************")
    logger.info("Total Save items:" + str(save_item_cnt))
    logger.info("************************************")
    logger.info("************************************")
