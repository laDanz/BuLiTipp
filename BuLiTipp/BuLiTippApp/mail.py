#http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
#http://docs.python.org/2/library/email-examples.html#email-examples
import mail_settings
''' required: mail_settings. USERNAME and PASSWORD as gmail credentials
'''
def send(subject, toaddrs, message):
	import smtplib
	from email.mime.text import MIMEText
	fromaddr = mail_settings.USERNAME
	# Credentials (if needed)
	username = mail_settings.USERNAME
	password = mail_settings.PASSWORD
	msg = MIMEText(message)
	msg['Subject'] = subject
	msg['From'] = fromaddr
	msg['To'] = toaddrs
	# The actual mail send
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(username,password)
	server.sendmail(fromaddr, toaddrs, msg.as_string())
	server.quit()

