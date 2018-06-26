import sendgrid
import os
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

def send_mail(body):

    from_email = Email("jdbuhrman@gmail.com")
    subject = "Updated Tracking infromation from SAR"
    to_email = Email("jbuhrman2@bloomberg.net")
    content = Content("text/html", body)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code
