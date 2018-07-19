import scrapy
import re
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Table, desc
from sqlalchemy.engine.url import URL
import sqlalchemy
from scraptrack import settings
from sqlalchemy.orm import mapper, sessionmaker
from scraptrack.items import TrackItem
from helpers import load_tables, remove_html_markup, clean_string, score_name, find_city, list2string, zone1, zone2, zone3a
#################### Spider Description ####################
#grabs 5 leavers sorted by the last time they were scraped
#uses their linkedin profile link as a google search term
#scrapes relevant details
############################################################
class QuotesSpider(scrapy.Spider):
    name = "tracking"
    sesh, Suspect, Leaver = load_tables()
    fresh_lvr = sesh.query(Leaver).filter_by(status='Tracking', track_lst_update=None).limit(5).all()
    lvr = sesh.query(Leaver).filter_by(status='Tracking').order_by(Leaver.track_lst_update).limit(5).all()

    def start_requests(self, sesh=sesh, Leaver=Leaver, lvr=lvr, fresh_lvr=fresh_lvr):
        print('***** Number of Fresh Leavers Not Yet Tracked: ', len(fresh_lvr))
        if len(fresh_lvr) > 0:
            for l in fresh_lvr:
                lid = l.id
                url = 'https://www.google.com/search?q=' + l.llink + ' ' + 'filter=0'

                yield scrapy.Request(url=url, callback=self.parse, meta={'lid': l.id, 'name': l.name})
        else:
            for l in lvr:
                lid = l.id
                url = 'https://www.google.com/search?q=' + l.llink + ' ' + 'filter=0'

                yield scrapy.Request(url=url, callback=self.parse, meta={'lid': l.id, 'name': l.name})

    def parse(self, response):
        db_name = response.meta['name']
        for i in response.xpath("//div[@class='g']"):
            print('**** FIRST G CLASS ****', i)
            raw_lnk = str(i.xpath(".//cite").extract())
            clink = zone2(raw_lnk)
            print('Zone2 Result Link: ', clink)
            if 'https://www.linkedin.com/in/' in clink:
                h3a = i.xpath(".//h3/a").extract()
                name, role1, firm1 = zone1(h3a)
                slp_xtract = i.xpath(".//div[contains(@class, 'slp')]/descendant::text()").extract()
                print('Raw SLP Xtract: ', slp_xtract)
                print('LENGTH of SLP Xtract: ', len(slp_xtract))

                if len(slp_xtract) > 0:
                    txt = str(slp_xtract)
                    print('length of slp: ', len(txt))
                    print('slp class detected. Running Zone3a Analysis...')
                    city, role, firm = zone3a(txt)
                    print('results from zone3a analysis: ')
                    item = TrackItem()
                    item['name'] = name
                    item['link'] = clink
                    item['ident'] = response.meta['lid']
                    item['location'] = city
                    if role1 == None:
                        item['role'] = role
                    else:
                        item['role'] = role1
                    if firm1 == None:
                        item['firm'] = firm
                    else:
                        item['firm'] = firm1
                    score = score_name(item['name'], db_name)
                    if score > 80:
                        yield item
                    else:
                        yield None

                else:
                    print('no slp class found.  salvaging text')
                    st_class = i.xpath(".//span[contains(@class, 'st')]/descendant::text()").extract()
                    print('ST Text Extracted: ', st_class)
                    salvage_string = list2string(st_class)
                    print('st class converted to string: ', salvage_string)
                    cleaned_str = clean_string(salvage_string, name)
                    print('st string filtered: ', cleaned_str)
                    item = TrackItem()
                    item['name'] = name
                    item['link'] = clink
                    item['location'] = None
                    item['ident'] = response.meta['lid']
                    if role1 == None:
                        item['role'] = None
                    else:
                        item['role'] = role1
                    if firm1 == None:
                        salvage_len = len(cleaned_str.strip())
                        print('length of salvaged text: ', salvage_len)
                        if salvage_len < 100:
                            item['firm'] = salvage_len
                        else:
                            item['firm'] = None
                    else:
                        item['firm'] = firm1
                    score = score_name(item['name'], db_name)
                    if score > 80:
                        yield item
                    else:
                        yield None


        # item = TrackItem()
        # item['ident'] = response.meta['lid']
        # slink = str(response.xpath('//*[@id="ires"]/ol/div[@class="g"]/div/div[1]/cite').extract_first())
        # item['link'] = remove_html_markup(slink).strip('[').strip(']').strip("\'")
        # deet = response.xpath('//*[@id="ires"]/ol/div[@class="g"]/div/div[2]/text()').extract()
        # deets = deet[0].replace(u'\xa0-\xa0', u'-')
        # deet_lst = deets.split('-')
        # if len(deet_lst) == 3:
        #     try:
        #         item['location'] = deet_lst[0]
        #     except:
        #         item['location'] = None
        #     try:
        #         item['role'] = deet_lst[1]
        #     except:
        #         item['role'] = None
        #     try:
        #         item['firm'] = deet_lst[2]
        #     except:
        #         item['firm'] = None
        # else:
        #     item['location'] = None
        #     item['role'] = None
        #     item['firm'] = None
        #
        # yield item
