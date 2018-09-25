from scraptrack import settings
#from datetime import datetime, timezone, date
import datetime
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker

from helpers import send_mail, load_tables, gen_html, htmldos, score_name

class TrackPipeline(object):
    def process_item(self, item, spider):
        print('***** Pipeline Processing Started ******')
        sesh = spider.sesh
        lvr = sesh.query(spider.Leaver).filter_by(id=item['ident']).one()
        print('Matching Links....')
        print('Link on File: ', lvr.llink)
        print('Link Found: ', item['link'])
        if lvr.llink == item['link']:
            ts_format = datetime.datetime.now(datetime.timezone.utc).isoformat()
            lvr.track_lst_update = ts_format
            lvr.track_firm = item['firm']
            lvr.track_location = item['location']
            lvr.track_role = item['role']
            lvr.track_detail = 'Yes'
            try:
                sesh.commit()
                print('Result Saved. DB Updated')
                print('.')
                print('.')
                print('.')
                print('.')
                print('.')
            except IntegrityError:
                print('except....', item['name'])
            print('***** Pipeline Processing Complete ******')
            return item

    def close_spider(self, spider):
        sesh = spider.sesh
        lvrs = sesh.query(spider.Leaver).filter_by(track_detail='Yes').all()
        today = datetime.date.today()
        checked = []
        changed = []
        for l in lvrs:
            timestamp = l.track_lst_update
            date = timestamp.date()
            if date == today:
                checked.append(l)
            print('>>Scoring Firm/Role Match Using Name Match Function')
            role_ratio = score_name(l.lrole, l.track_role)
            firm_ratio = score_name(l.lfirm, l.track_firm)
            if role_ratio < 40 or firm_raio < 40:
                changed.append(l)

        if len(changed) > 0:
            html2 = htmldos(changed)
            resp_code2 = send_mail(html2)
            print(resp_code2)
        if len(checked) > 0:
            html = gen_html(checked)
            resp_code = send_mail(html)
            print(resp_code)
