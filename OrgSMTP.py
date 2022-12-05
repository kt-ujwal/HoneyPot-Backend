import smtpd
import uuid
from datetime import datetime
import asyncore
from smtpd import SMTPServer

class OrgSMTPServer(SMTPServer):
    no = 0

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        filename = '%s-%d.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'),
                                  self.no)

        f = open(filename, 'wb')
        f.write(data)
        f.close
        print('%s saved.' % filename)
        self.no += 1

def run():
    server = OrgSMTPServer(('localhost', 2025), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass

def send_mail_to_org(peer, mailfrom, rcpttos, data):
    emailuuid = uuid.uuid4()
    filename = '%s-%s.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'), emailuuid)
    f = open(f"Org/{filename}", 'wb')
    f.write(data)
    f.close
    print('%s saved.' % filename)
