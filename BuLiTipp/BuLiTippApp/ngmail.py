#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
author: cdanzmann@gmail.com, 2014-03-07
USAGE: simply call send() to queue a mail.
The module will build a connection to smtp server, if not yet established, and send the mail asynchronously(each in a separate thread). The connection will be cancelled after $SESSION_TIMEOUT seconds.
If more mails are queued while connection is still established (for example in a for loop), the mails will queue and be sent one after another. Order is not preserved.
The cancelling of the connection will be queued as well, so if $SESSION_TIMEOUT seconds have passed, but there are still mails to send in the queue, first the mails will be sent, and if no mails are left, the connection will be cancelled.
So it is not guaranteed that the session will be terminated exactly after $SESSION_TIMEOUT seconds. But the connection will be terminated eventually.
If mails join the queue after the cancellation has been queued, the connection may terminate(after a successful sending), but will be re-established before sending any more new mails.
'''
from __future__ import unicode_literals
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
#http://docs.python.org/2/library/email-examples.html#email-examples
''' required: mail_settings. USERNAME and PASSWORD as gmail credentials
'''
import mail_settings
from threading import Thread, Lock, Timer

''' SESSION_TIMEOUT in seconds
'''
SESSION_TIMEOUT = 30.0

class Send_async(Thread):
	is_connected = False
	server = None
	lock=Lock()
	timeout_timer = None
	def __init__(self, subject, toaddrs, message, message_html):
		Thread.__init__(self)
		self.subject = subject.encode('ascii', 'xmlcharrefreplace')
		self.toaddrs = toaddrs
		self.message = message.encode('ascii', 'xmlcharrefreplace')
		self.message_html = message_html.encode('ascii', 'xmlcharrefreplace')

	def run(self):
		self.send_sync()

	def send_sync(self):
		global SESSION_TIMEOUT
		Send_async.lock.acquire()
		if not Send_async.is_connected:
			self.init_session()
		msg = MIMEMultipart('alternative')
		fromaddr = mail_settings.USERNAME
		msg['From'] = fromaddr
		msg['To'] = self.toaddrs
		msg['Subject'] = self.subject
		# content
		part1 = MIMEText(str(self.message), 'plain')
		part2 = MIMEText(str(self.message_html), 'html')
		msg.attach(part1)
		if self.message_html is not None:
			msg.attach(part2)
		# The actual mail send
		Send_async.server.sendmail(fromaddr, self.toaddrs, msg.as_string())
		if Send_async.timeout_timer is None:
			Send_async.timeout_timer = Timer(SESSION_TIMEOUT, self.close_session)
			Send_async.timeout_timer.start()
		Send_async.lock.release()

	def close_session(self):
		Send_async.lock.acquire()
		if not Send_async.is_connected:
			return
		Send_async.server.quit()
		Send_async.is_connected = False
		Send_async.timeout_timer = None
		Send_async.lock.release()

	def init_session(self):
		# needs no lock, is inside send_sync() lock
		if Send_async.is_connected:
			return
		username = mail_settings.USERNAME
		password = mail_settings.PASSWORD
		Send_async.server = smtplib.SMTP('smtp.gmail.com:587')
		Send_async.server.starttls()
		Send_async.server.login(username,password)
		Send_async.is_connected = True

def send(subject, toaddrs, message, message_html=None):
	Send_async(subject, toaddrs, message, message_html).start()

