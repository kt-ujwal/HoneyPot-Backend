import smtpd
from datetime import datetime
import asyncore
from smtpd import SMTPServer
import OrgSQLRepository as r
import HoneyPotProcessor as hp
import itertools
import smtplib
import OrgSMTP as org_smtp


class OrgHoneySMTPServer(SMTPServer):
    no = 0

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        try:
            banned_email_list = list(itertools.chain(*r.banned_emails()))
            if mailfrom not in banned_email_list:
                hp.process_honey_tokens(mailfrom, rcpttos, data)
                banned_email_list = list(itertools.chain(*r.banned_emails()))
                if mailfrom not in banned_email_list:
                    self.sendto_realserver(peer, mailfrom, rcpttos, data)
                else:
                    pass

            else:
                hp.process_email(mailfrom, rcpttos, data)
                print("Recieved Email from blocked email sender discarding email...")
        except Exception as e:
            print(e)

    def sendto_realserver(self, peer, mailfrom, rcpttos, data):
        org_smtp.send_mail_to_org(peer, mailfrom, rcpttos, data)
        with smtplib.SMTP(host='ec2-54-173-9-46.compute-1.amazonaws.com', port=2525) as real_smtp:
        #with smtplib.SMTP(host='localhost', port=587) as real_smtp:
             real_smtp.sendmail(mailfrom, rcpttos, data)


def run():
    #server = OrgHoneySMTPServer(('localhost', 2525), None)
    server = OrgHoneySMTPServer(('172.31.89.108', 2525), None)
    try:
        print("Listening on port 2525...")
        asyncore.loop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run()
