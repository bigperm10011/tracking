import scrapy
import re
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Table, desc
from sqlalchemy.engine.url import URL
import sqlalchemy
from scraptrack import settings
from sqlalchemy.orm import mapper, sessionmaker
from scraptrack.items import TrackItem
from helpers import load_tables, remove_html_markup

class QuotesSpider(scrapy.Spider):
    name = "tracking"
    sesh, Suspect, Leaver = load_tables()
    lvr = sesh.query(Leaver).filter_by(status='Tracking').order_by(desc(Leaver.track_lst_update)).limit(5).all()

    def start_requests(self, sesh=sesh, Leaver=Leaver, lvr=lvr):
        for l in lvr:
            lid = l.id
            url = 'https://www.google.com/search?q=' + l.llink + ' ' + 'site:www.linkedin.com'

            yield scrapy.Request(url=url, callback=self.parse, meta={'lid': l.id})

    def parse(self, response):
        item = TrackItem()
        item['ident'] = response.meta['lid']
        slink = str(response.xpath('//*[@id="ires"]/ol/div[@class="g"]/div/div[1]/cite').extract_first())
        item['link'] = remove_html_markup(slink).strip('[').strip(']').strip("\'")
        deet = response.xpath('//*[@id="ires"]/ol/div[@class="g"]/div/div[2]/text()').extract()
        deets = deet[0].replace(u'\xa0-\xa0', u'-')
        deet_lst = deets.split('-')
        #print('DEET  LIST VALUE: ', deet_lst[1])
        #print('!!!!!!!!!!', len(deet_lst))
        if len(deet_lst) == 3:
            try:
                item['location'] = deet_lst[0]
            except:
                item['location'] = None
            try:
                item['role'] = deet_lst[1]
            except:
                item['role'] = None
            try:
                item['firm'] = deet_lst[2]
            except:
                item['firm'] = None
        else:
            item['location'] = None
            item['role'] = None
            item['firm'] = None
#response.xpath('//*[@id="ires"]/ol/div[@class="g"]/h3/a/text()').extract

        yield item
