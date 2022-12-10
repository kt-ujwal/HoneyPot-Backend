import itertools
import os
import smtpd
import uuid
from datetime import datetime
import asyncore
from smtpd import SMTPServer
import OrgSQLRepository as r

class OrgSMTPServer(SMTPServer):
    no = 0

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        try:
            for rcp_to in rcpttos:
                inbox = f'{rcp_to.split("@")[0]}/Inbox'
                spam = f'{rcp_to.split("@")[0]}/Spam'
                if not os.path.exists(inbox):
                    os.makedirs(inbox)
                if not os.path.exists(spam):
                    os.makedirs(spam)
                org_email_dir = list(itertools.chain(*r.get_org_email_dir()))
                if rcp_to in org_email_dir:
                    is_spam = r.is_spam_email(mailfrom,rcp_to,data)
                    if is_spam==[]:
                        filename = '%s-%d.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'),self.no)
                        print(f"Sending Email to {inbox}")
                        f = open(f"{inbox}/{filename}", 'wb')
                        f.write(data)
                        f.close
                        #print('%s saved.' % filename)
                        self.no += 1
                    for found_spam in is_spam:
                        if found_spam:
                            filename = '%s-%d.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'),self.no)
                            print(f"Sending Email to {spam}")
                            f = open(f"{spam}/{filename}", 'wb')
                            f.write(data)
                            f.close
                            #print('%s saved.' % filename)
                            self.no += 1
                            break

        except Exception as e:
            print(e)

def run():
    server = OrgSMTPServer(('172.31.29.216', 2525), None)
    try:
        print("Listening on port 2525...")
        asyncore.loop()
    except KeyboardInterrupt:
        pass

def send_mail_to_org(peer, mailfrom, rcpttos, data):
    emailuuid = uuid.uuid4()
    orgdata = f'Org'
    if not os.path.exists(orgdata):
        os.makedirs(orgdata)
    filename = '%s-%s.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'), emailuuid)
    f = open(f"{orgdata}/{filename}", 'wb')
    f.write(data)
    f.close()
    print('%s saved for spam analysis.' % filename)
    for rcpto in rcpttos:
        subject = str(data).lower().split("subject")[1].split("\\n")[0].replace("\'","")
        body = str(data).lower().split("subject")[1].split("\\n")[1].replace("\'","")
        r.insert_org_email(mailfrom, subject, body, rcpto)
        print(f"Email delivered to {rcpto}")

def check_process_message(mailfrom, rcpttos, data, **kwargs):
    try:
        for rcp_to in rcpttos:
            inbox = f'{rcp_to.split("@")[0]}/Inbox'
            spam = f'{rcp_to.split("@")[0]}/Spam'
            if not os.path.exists(inbox):
                os.makedirs(inbox)
            if not os.path.exists(spam):
                os.makedirs(spam)
            org_email_dir = list(itertools.chain(*r.get_org_email_dir()))
            if rcp_to in org_email_dir:
                is_not_spam = r.is_spam_email(mailfrom,rcp_to,data)
                if is_not_spam == []:
                    filename = '%s.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'))
                    print(f"Sending Email to {inbox}")
                    f = open(f"{inbox}/{filename}", 'wb')
                    f.write(data)
                    f.close

                for not_spam in is_not_spam:
                    if not_spam:
                        filename = '%s.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'))
                        print(f"Sending Email to {spam}")
                        f = open(f"{spam}/{filename}", 'wb')
                        f.write(data)
                        f.close
                        break





    except Exception as e:
        print(e)


if __name__ == '__main__':
    run()
