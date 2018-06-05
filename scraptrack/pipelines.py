from scraptrack import settings
from datetime import datetime, timezone
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
#from helpers import Suspect, Leaver
from helpers import load_tables

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class TrackPipeline(object):
    def process_item(self, item, spider):
        sesh = spider.sesh
        lvr = sesh.query(spider.Leaver).filter_by(id=item['ident']).one()
        ts_format = datetime.now(timezone.utc).isoformat()
        lvr.track_lst_update = ts_format
        #strftime("%Y-%m-%dT%H:%M:%S")
        lvr.track_firm = item['firm']
        lvr.track_location = item['location']
        lvr.track_role = item['role']
        lvr.track_detail = 'Yes'
        try:
            sesh.commit()
        except IntegrityError:
                print('except....', item['name'])

        return item
