import itertools
import pickle
import string
from nltk.corpus import stopwords
import nltk
from nltk.stem.porter import PorterStemmer
import pandas as pd
import psycopg2
from configparser import ConfigParser
import json
import uuid
import get_secret_postgres as sm

def config(filename: str = 'database.ini', section: str = 'awspostgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
        if db['password'] == '':
            db['password'] = sm.get_secret()

    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db

def get_honey_tokens(sql: str ='SELECT honey_token_email FROM public.\"Honeytokens\";'):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        #print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        # print('Data in Users table:\n')
        cur.execute(sql)
        # conn.commit()

        # display the PostgreSQL database server version
        data = cur.fetchall()
        #print(data)

        # close the communication with the PostgreSQL
        cur.close()
        return data
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            #print('Database connection closed.')

def get_org_email_dir(sql: str ='SELECT email_id FROM public.\"Employees\";'):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        #print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        # print('Data in Users table:\n')
        cur.execute(sql)
        # conn.commit()

        # display the PostgreSQL database server version
        data = cur.fetchall()
        #print(data)

        # close the communication with the PostgreSQL
        cur.close()
        return data
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            #print('Database connection closed.')

def is_spam_email(mail_from,rcptos,data):
    """ Connect to the PostgreSQL database server """
    try:
        subject = str(data).lower().split("subject")[1].split("\\n")[0].replace("\'", "")
        body = str(data).lower().split("subject")[1].split("\\n")[1].replace("\'", "")
        is_spam = []
        sql:str =f"SELECT is_spam FROM public.org_email where from_email='{mail_from}' and email_subject='{subject}' and email_body='{body}' and email_to='{rcptos}';"
        conn = None

        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        #print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        # print('Data in Users table:\n')
        cur.execute(sql)
        # conn.commit()

        # display the PostgreSQL database server version
        data = cur.fetchall()
        #print(data)
        for dat in data:
            if dat[0]:
                is_spam.append(dat)
        # close the communication with the PostgreSQL
        cur.close()
        return is_spam
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            #print('Database connection closed.')

def org_emails(sql: str ='SELECT * FROM public.org_email;'):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        #print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        # print('Data in Users table:\n')
        cur.execute(sql)
        # conn.commit()

        # display the PostgreSQL database server version
        data = cur.fetchall()
        #print(data)

        # close the communication with the PostgreSQL
        cur.close()
        return data
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            #print('Database connection closed.')

def blocked_emails(sql: str ='SELECT * FROM public.email_blocker;'):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        #print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        # print('Data in Users table:\n')
        cur.execute(sql)
        # conn.commit()

        # display the PostgreSQL database server version
        data = cur.fetchall()
        #print(data)

        # close the communication with the PostgreSQL
        cur.close()
        return data
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            #print('Database connection closed.')


def banned_emails(sql: str ='SELECT banned_email FROM public."BannedEmails";'):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        #print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        # print('Data in Users table:\n')
        cur.execute(sql)
        # conn.commit()

        # display the PostgreSQL database server version
        data = cur.fetchall()
        #print(data)

        # close the communication with the PostgreSQL
        cur.close()
        return data
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            #print('Database connection closed.')


def insert_banned_email(sentfrom):
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    # execute a statement
    for sf in [sentfrom]:
        insert_banned_sql: str = f"SELECT public.insert_banned_emails('{sf}');"
        cur.execute(insert_banned_sql)
        conn.commit()

    conn.close()

def insert_org_email(mailfrom, subject, body,rcpttos):
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    # execute a statement
    for mf in [mailfrom]:
        insert_banned_sql: str = f"SELECT public.insert_email_org('{mf}','{subject}','{body}','{rcpttos}','false')"
        cur.execute(insert_banned_sql)
        conn.commit()

    conn.close()
def insert_blocked_email_contents(mailfrom, subject, body,rcpttos):
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    body = body.strip("'")
    # execute a statement
    for mf in [mailfrom]:
        insert_banned_sql: str = f"SELECT public.insert_email_blocker('{mf}','{subject}','{body}','{rcpttos}')"
        cur.execute(insert_banned_sql)
        conn.commit()

    conn.close()




def insert_spam_emails(mailfrom, subject, body,rcpttos):
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    insert_banned_sql: str = f"SELECT public.update_spam_emails('{mailfrom}','{subject}','{body}','{rcpttos}',true)"
    cur.execute(insert_banned_sql)
    conn.commit()
    conn.close()