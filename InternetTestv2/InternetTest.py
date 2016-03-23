import os
import twitter
import ClientInfo
import re
import sys
from datetime import datetime
import argparse
import sqlite3 as sql

def testSpeed():
    '''Run a speed test, check if the speeds are to low, and if they are
    send out a tweet to shaw that lets them know!'''
    TARGET_DOWNLOAD = 60
    TARGET_UPLOAD = 6
    
    print('------------------ RUNNING TEST ---------------------')

    db = databaseInit('data/sqlite3.sqlite')
    dailyAverage = False
    speeds = os.popen("speedtest-cli --simple").read()
    print (speeds)

    if 'errno' in speeds.lower():
        connected = False
    else:
        connected = True

    twitterInfo = ClientInfo.info()
    
    twitterApi = twitter.Api(
        consumer_key = twitterInfo.consumerKey,
        consumer_secret = twitterInfo.consumerSecret,
        access_token_key = twitterInfo.accessTokenKey,
        access_token_secret = twitterInfo.accessTokenSecret
    )
    
    if connected:
        #parse the results for the speeds
        results = re.findall(r'\d+\.\d+', speeds, re.IGNORECASE|re.DOTALL)

        #fix this
        tweetID = getMaxTweetID(db) + 1
        
        ping = int(float(results[0]))
        downSpeed = int(float(results[1]))
        upSpeed = int(float(results[2]))
        tweet = 'SpeedTest #{2}: Hey @ShawInfo, why is my internet so slow @ {0}Mbs down/{1}Mbs up when I pay for 60/6 in Edmonton. @Shawhelp #speedtest'.format(downSpeed, upSpeed, str(tweetID).zfill(3))
        #check if the download speed is less than 25% of the target (what we pay for)
        if downSpeed < TARGET_DOWNLOAD * .25:
            #twitterApi.PostUpdate(tweet)
            pass

        elif dailyAverage:
            tweet = 'Daily average internet speeds: {0}Mbs down/{1}Mbs up, with {2}ms ping. Tested every hour by your friendly neighborhood pi. #speedtest'.format(loggedDown, loggedUp, loggedPing)
            twitterApi.PostUpdate(tweet)

    else:
        #set default info if there is no connection
        ping = sys.maxint
        downSpeed = 0
        upSpeed = 0

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {'Ping':ping, 'Down_Speed':downSpeed,
            'Up_Speed':upSpeed, 'Log_Date':date}
    dailyAverageSpeeds(db)
    logTweet(db, data)
    db.close()
    print('----------------- FINISHED TEST ---------------------')
    
def databaseInit(location):
    db = sql.connect(location)
    cursor = db.cursor()

    #check if the tweets table already exists
    createTable(db, cursor, 'tweets',
                ['tweet_id INTEGER PRIMARY KEY', 'Ping INTEGER',
                 'Down_Speed INTEGER', 'Up_Speed INTEGER',
                 'Log_Date DATE']
                 )

    cursor.close()

    return db

def createTable(dbconn, cursor, table, rows):
    try:
        cursor.execute("""CREATE TABLE {0}({1})""".format(table, ', '.join(rows)))
        dbconn.commit()
    except sql.OperationalError:
        pass       

def logTweet(dbconn, data):
    print('Inserting into DB')
    cursor = dbconn.cursor()
    cursor.execute("""INSERT INTO tweets(tweet_id, Ping, Down_Speed, Up_Speed, Log_Date)
                    VALUES(NULL, ?, ?, ?, ?)""",(
                        data['Ping'], data['Down_Speed'], data['Up_Speed'],
                        data['Log_Date'])
                   )
    cursor.close()
    dbconn.commit()

def getMaxTweetID(dbconn):
    cursor = dbconn.cursor()
    cursor.execute("""SELECT MAX(tweet_id) FROM tweets""")
    result = cursor.fetchone()
    cursor.close()
    return result[0]

def dailyAverageSpeeds(dbconn):
    cursor = dbconn.cursor()
    cursor.execute("""SELECT AVG(Down_Speed) FROM tweets
                   WHERE datetime(Log_Date) > datetime('now','-1 day')""")
    resultDown = cursor.fetchone()
    cursor.execute("""SELECT AVG(Up_Speed) FROM tweets
                   WHERE datetime(Log_Date) > datetime('now','-1 day')""")
    resultUp = cursor.fetchone()
    cursor.close()

    return (resultDown[0], resultUp[0])

if __name__ == '__main__':
    testSpeed();
