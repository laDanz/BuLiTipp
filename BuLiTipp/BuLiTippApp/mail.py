#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
#http://docs.python.org/2/library/email-examples.html#email-examples
import mail_settings
''' required: mail_settings. USERNAME and PASSWORD as gmail credentials
'''
def send(subject, toaddrs, message, message_html=None):
	import smtplib
	from email.mime.text import MIMEText
	from email.mime.multipart import MIMEMultipart
	#encoding
	subject = subject.encode('ascii', 'xmlcharrefreplace')
	message = message.encode('ascii', 'xmlcharrefreplace')
	if message_html:
		message_html = message_html.encode('ascii', 'xmlcharrefreplace')
	fromaddr = mail_settings.USERNAME
	# Credentials (if needed)
	username = mail_settings.USERNAME
	password = mail_settings.PASSWORD
	msg = MIMEMultipart('alternative')#MIMEText(message)
	part1 = MIMEText(str(message), 'plain')
	part2 = MIMEText(str(message_html), 'html')
	msg.attach(part1)
	if message_html is not None:
		msg.attach(part2)
	msg['Subject'] = subject
	msg['From'] = fromaddr
	msg['To'] = toaddrs
	# The actual mail send
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(username,password)
	server.sendmail(fromaddr, toaddrs, msg.as_string())
	server.quit()

