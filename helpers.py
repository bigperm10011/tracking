from scraptrack.settings import get_con_string
from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.automap import automap_base
import sendgrid
import os
from sendgrid.helpers.mail import *



def send_mail(body):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("jdbuhrman@gmail.com")
    subject = "Updated Tracking infromation from SAR"
    to_email = Email("jbuhrman2@bloomberg.net")
    content = Content("text/html", body)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code


def load_tables():
    """"""
    cs = get_con_string()
    # automap base
    Base = automap_base()

    # pre-declare User for the 'user' table
    class Leaver(Base):
        __tablename__ = 'leaver'

    # reflect
    engine = create_engine(cs)
    Base.prepare(engine, reflect=True)

    # we still have Address generated from the tablename "address",
    # but User is the same as Base.classes.User now

    Suspect = Base.classes.suspect
    Session = sessionmaker(bind=engine)
    session = Session()
    return session, Suspect, Leaver


def remove_html_markup(s):
    tag = False
    quote = False
    out = ""

    for c in s:
            if c == '<' and not quote:
                tag = True
            elif c == '>' and not quote:
                tag = False
            elif (c == '"' or c == "'") and tag:
                quote = not quote
            elif not tag:
                out = out + c

    return out

def htmldos(changed):
    html2 = """\
        <!DOCTYPE html><html lang="en"><head>SAR Leaver Found! </head><body><table border='1'>
        <thead><tr><th>Name</th><th>Old Firm</th><th>New Firm</th><th>Old Role</th><th>New Role</th><th>Location</th><th>LinkedIn</th></tr></thead>"""

    for c in changed:
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
    return html2

def gen_html(checked):
    html = """\
        <!DOCTYPE html><html lang="en"><head>SAR Leavers Checked Today</head><body><table border='1'>
        <thead><tr><th>Name</th><th>Firm</th><th>Role</th><th>Location</th><th>Link</th></tr></thead>"""

    for l in checked:
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
    return html
