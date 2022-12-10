import os
import uuid
from datetime import datetime

import OrgSQLRepository as r
import itertools

import pickle
import string
from nltk.corpus import stopwords
import nltk
from nltk.stem.porter import PorterStemmer
import sklearn

def process_honey_tokens(mailfrom, rcpttos, data, honeytoken_tuple=r.get_honey_tokens()):
    honey_token_list = list(itertools.chain(*honeytoken_tuple))
    for rcpto in rcpttos:
        if rcpto in honey_token_list:
            print("Email Recieved to honey token email")
            subject = str(data).lower().split("subject")[1].split("\\n")[0].replace("\'","")
            body = str(data).lower().split("subject")[1].split("\\n")[1].replace("\'","")
            r.insert_blocked_email_contents(mailfrom, subject, body, rcpto)
            meta_data_reciever(data)
            r.insert_banned_email(mailfrom)
            print("Captured email contents and blocked sender")
        else:
            pass

def process_email(mailfrom, rcpttos, data, honeytoken_tuple=r.get_honey_tokens()):
    honey_token_list = list(itertools.chain(*honeytoken_tuple))
    for rcpto in rcpttos:
        if rcpto in honey_token_list:
            subject = str(data).lower().split("subject")[1].split("\\n")[0].replace("\'","")
            body = str(data).lower().split("subject")[1].split("\\n")[1].replace("\'","")
            r.insert_blocked_email_contents(mailfrom, subject, body, rcpto)
            meta_data_reciever(data)
            print("Captured email contents from blocked sender")
        else:
            pass


def meta_data_reciever(data):
    emailuuid = uuid.uuid4()
    metadata = f'Blocked'
    if not os.path.exists(metadata):
        os.makedirs(metadata)
    filename = '%s-%s.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'),emailuuid)
    f = open(f"{metadata}/{filename}", 'wb')
    f.write(data)
    f.close
    print('%s captured for analysis.' % filename)


ps = PorterStemmer()


def preprocessed_data(text):
    text = text.lower()
    text = nltk.word_tokenize(text)

    y = []
    for i in text:
        if i.isalnum():
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        y.append(ps.stem(i))

    return " ".join(y)

def is_spam(body):
    transform = pickle.load(open('vectorizer.pkl', 'rb'))
    model = pickle.load(open('model.pkl', 'rb'))
    #nltk.download('punkt')
    #nltk.download('stopwords')
    # 1. preprocess
    processed_text = preprocessed_data(body)
    # 2. vectorize
    input = transform.transform([processed_text])
    # 3. predict
    result = model.predict(input)[0]
    return result
