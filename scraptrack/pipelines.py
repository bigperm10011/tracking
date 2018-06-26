from scraptrack import settings
#from datetime import datetime, timezone, date
import datetime
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker

from helpers import load_tables, send_mail

class TrackPipeline(object):
    def process_item(self, item, spider):
        sesh = spider.sesh
        lvr = sesh.query(spider.Leaver).filter_by(id=item['ident']).one()
        ts_format = datetime.datetime.now(datetime.timezone.utc).isoformat()
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
        lvrs = sesh.query(spider.Leaver).filter_by(track_detail='Yes').all()
        today = datetime.date.today()
        html = """\
            <!DOCTYPE html><html lang="en"><head>SAR Tracker Update </head><body><table border='1'>
            <thead><tr><th>Name</th><th>Firm</th><th>Role</th><th>Location</th><th>Link</th></tr></thead>"""
        changes = []
        for l in lvrs:
            if l.lrole != l.track_role or l.lfirm != l.track_firm:
                changes.append(l)

            timestamp = l.track_lst_update
            date = timestamp.date()
            if date == today:
                html = html + "<tr>"
                html = html + "<td>" + l.name + "</td>"
                try:
                    html = html + "<td>" + l.track_firm + "</td>"
                except:
                    html = html + "<td>None</td>"
                try:
                    html = html + "<td>" + l.track_role + "</td>"
                except:
                    html = html + "<td>None</td>"
                try:
                    html = html + "<td>" + l.track_location + "</td>"
                except:
                    html = html + "<td>None</td>"
                try:
                    html = html + '<td><a target="_blank" href="'+ l.llink + ' ">LinkedIn</a></td></tr>'
                except:
                    html = html + '<td><a target="_blank" href=None">None</a></td></tr>'
        html = html + "</table></body></html>"
        resp_code = send_mail(html)
        print(resp_code)
        if len(changes) > 0:
            html2 = """\
                <!DOCTYPE html><html lang="en"><head>SAR Leaver Found! </head><body><table border='1'>
                <thead><tr><th>Name</th><th>Old Firm</th><th>New Firm</th><th>Old Role</th><th>New Role</th><th>Location</th><th>LinkedIn</th></tr></thead>"""
            for c in changes:
                html2 = html2 + "<tr>"
                html2 = html2 + "<td>" + c.name + "</td>"
                try:
                    html2 = html2 + "<td>" + c.lfirm + "</td>"
                except:
                    html2 = html2 + "<td>None</td>"
                try:
                    html2 = html2 + "<td>" + c.track_firm + "</td>"
                except:
                    html2 = html2 + "<td>None</td>"
                try:
                    html2 = html2 + "<td>" + c.lrole + "</td>"
                except:
                    html2 = html2 + "<td>None</td>"
                try:
                    html2 = html2 + "<td>" + c.track_role + "</td>"
                except:
                    html2 = html2 + "<td>None</td>"
                try:
                    html2 = html2 + "<td>" + c.llocation + "</td>"
                except:
                    html2 = html2 + "<td>None</td>"
                try:
                    html2 = html2 + '<td><a target="_blank" href="'+ c.llink + ' ">LinkedIn</a></td></tr>'
                except:
                    html2 = html2 + '<td><a target="_blank" href=None">None</a></td></tr>'

        html2 = html2 + "</table></body></html>"
        resp_code = send_mail(html2)
        print(resp_code)
