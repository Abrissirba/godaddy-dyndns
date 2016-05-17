#!/usr/bin/env python3

import configparser
import logging
import sys
import string

import pif
import pygodaddy
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

username = ''
password = ''
SERVER = ""
FROM = ""
TO = ""

logging.basicConfig(filename='godaddy-dyndns.log',
		    format='%(asctime)s %(message)s',
		    level=logging.INFO)   

def sendEmail(body):
    
    SUBJECT = "Dynamic DNS Error - server adsync"

    msg = MIMEMultipart()
    msg['From'] = FROM
    msg['To'] = TO
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(body, 'plain'))

    text = msg.as_string()
    server = smtplib.SMTP(SERVER)
    server.sendmail(FROM, TO, text)
    server.quit()
    return;

client = pygodaddy.GoDaddyClient()
is_logged_in = client.login(username, password)
if not is_logged_in:
    logging.error('Login failed!')
    sys.exit(1)
    
for domain in client.find_domains():
    dns_records = list(client.find_dns_records(domain))
    public_ip = pif.get_public_ip()
    
    for record in dns_records:
        if record.hostname == 'web':
            hostname = record.hostname + '.' + domain
            try:
                updated = client.update_dns_record(hostname, public_ip)
                if updated:
                    logging.info("Domain '{0}' public IP set to '{1}'".format(hostname, public_ip))
            except ValueError as e:
                sendEmail(': ' + public_ip)
                logging.info(e)

