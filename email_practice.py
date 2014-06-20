import smtplib

##def send_email(message = "this is the message to be sent", subject = '',from_email = "rtfdtddprocessing@gmail.com", from_password = "rtfd_tdd",to_email = "8018337876@messaging.sprintpcs.com"):
##    if subject == '' or subject == None:
##        try:
##            subject = message[:50]
##        except:
##            subject = message
##
##    vtext = "8018337876@messaging.sprintpcs.com"
##    msg = """From: %s
##    To: %s
##    Subject: %s
##    %s""" % (from_email, to_email, subject,message)
##
##    server = smtplib.SMTP('smtp.gmail.com',587)
##    server.starttls()
##    server.login(from_email,from_password)
##    print 'Sending message:',msg
##    server.sendmail(from_email, to_email, msg)
##    server.quit()

#send_email('please tell me if this is working')

import smtplib

class email:
    def __init__(self):
        print 'yay'
        self.server = smtplib.SMTP('smtp.gmail.com',587)
        self.server.starttls()
    def send_email(self):#message = "this is the message to be sent", subject = '',from_email = "rtfdtddprocessing@gmail.com", password = "rtfd_tdd",to_email = "8018337876@messaging.sprintpcs.com"):

        message = "please work2"
        subject = ''
        from_email = "rtfdtddprocessing@gmail.com"
        password = "rtfd_tdd"
        to_email = "8018337876@messaging.sprintpcs.com"
        if subject == '' or subject == None:
            try:
                subject = message[:50]
            except:
                subject = message

        #message = "this 4 is the message to be sent"

        msg = """From: %s
        To: %s
        Subject: %s
        %s""" % (from_email, to_email, subject,message)
        print 'Sending message:', msg

        self.server.login(from_email,password)
        self.server.sendmail(from_email, to_email, msg)
    def close_email(self):
        self.server.quit()
e = email()
e.send_email()
e.close_email()
#send_email()