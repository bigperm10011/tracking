from scraptrack import settings
from datetime import datetime, timezone
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
from email.email import send_mail
from helpers import load_tables

class TrackPipeline(object):
    def process_item(self, item, spider):
        sesh = spider.sesh
        lvr = sesh.query(spider.Leaver).filter_by(id=item['ident']).one()
        ts_format = datetime.now(timezone.utc).isoformat()
        lvr.track_lst_update = ts_format

        lvr.track_firm = item['firm']
        lvr.track_location = item['location']
        lvr.track_role = item['role']
        lvr.track_detail = 'Yes'
        try:
            sesh.commit()
        except IntegrityError:
                print('except....', item['name'])

        return item

    def close_spider(self, spider):
        sesh = spider.sesh
        lvrs = sesh.query(spider.Leaver).filter_by(track_detail == 'Yes').all()
        today = datetime.date.today()
        html = """\
            <!DOCTYPE html><html lang="en"><head>SAR Tracker Update </head><body><table border='1'>
            <thead><tr><th>Name</th><th>Firm</th><th>Role</th><th>Location</th><th>Location</th></tr></thead>"""
        for l in leavers:
            timestamp = l.track_lst_update
            date = timestamp.date()
            if date == today:
                html = html + "<tr>"
                html = html + "<td>" + l.name + "</td>"
                html = html + "<td>" + l.track_firm + "</td>"
                html = html + "<td>" + l.track_role + "</td>"
                html = html + "<td>" + l.track_location + "</td>"
                html = html + '<td><a target="_blank" href="'+ l.llink + ' ">LinkedIn</a></td></tr>'
        html = html + "</table></body></html>"
        resp_code = send_mail(html)
        print(resp_code)

        self.client.close()
