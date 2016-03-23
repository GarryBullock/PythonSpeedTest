import os
import twitter
import ClientInfo
import re
import sys
from datetime import datetime

def testSpeed():
    '''Run a speed test, check if the speeds are to low, and if they are
    send out a tweet to shaw that lets them know!'''
    logFileLocation = '/home/pi/InternetTest/internetSpeedLogFile.txt'
    tweetIDLocation = '/home/pi/InternetTest/tweetIDFile.txt'
    TARGET_DOWNLOAD = 60
    TARGET_UPLOAD = 6
    
    print '------------------ RUNNING TEST ---------------------'
    try:
        logFile = open(logFileLocation, 'r+')
    except:
        open(logFileLocation, 'w+')
        logFile = open(logFileLocation, 'r+')

    try:
        tweetIDFile = open(tweetIDLocation, 'r+')
    except:
        tweetIDFile = open(tweetIDLocation, 'w+')
        tweetIDFile.write("0\n")
        tweetIDFile.close()
        tweetIDFile = open(tweetIDLocation, 'r+')
        
    numLines = 0
    for line in logFile:
        numLines += 1

    #4 lines per test. Date, ping, down, up, '\n'
    numTests = numLines / 2
    loggedPing = 0
    loggedDown = 0
    loggedUp = 0


    tweetID = int(tweetIDFile.readline())
    newTweetID = tweetID + 1
    
    dailyAverage = False
    if numTests >= 24:
        logFile.seek(0) #back to the start of the file
        values = []
        
        for i in range(numTests):
            logFile.readline()
            values.append(logFile.readline())

        for entry in values:
            speeds = entry.split()
            loggedPing += int(speeds[0])
            loggedDown += int(speeds[1])
            loggedUp += int(speeds[2])

        loggedPing /= numTests
        loggedDown /= numTests
        loggedUp /= numTests

        #clear the logfile daily
        logFile.seek()
        logFile.truncate()
        dailyAverage = True

    logFile.close()
    
    speeds = os.popen("speedtest-cli --simple").read()
    print speeds
    
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

        ping = int(float(results[0]))
        downSpeed = int(float(results[1]))
        upSpeed = int(float(results[2]))
        tweet = 'SpeedTest #{2}: Hey @ShawInfo, why is my internet so slow @ {0}Mbs down/{1}Mbs up when I pay for 60/6 in Edmonton. @Shawhelp #speedtest'.format(downSpeed, upSpeed, str(tweetID).zfill(3))
        print tweet
        #check if the download speed is less than 25% of the target (what we pay for)
        if downSpeed < TARGET_DOWNLOAD * .25 and not dailyAverage:
            #twitterApi.PostUpdate(tweet)
            tweetIDFile.seek(0)
            tweetIDFile.truncate()
            tweetIDFile.write(str(newTweetId) + '\n')

        elif dailyAverage:
            tweet = 'Daily average internet speeds: {0}Mbs down/{1}Mbs up, with {2}ms ping. Tested every hour by your friendly neighborhood pi. #speedtest'.format(loggedDown, loggedUp, loggedPing)
            twitterApi.PostUpdate(tweet)

    else:
        #set default info if there is no connection
        ping = sys.maxint
        downSpeed = 0
        upSpeed = 0

    #log the data
    logFile = open(logFileLocation, 'a')
    logFile.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
    logFile.write(str(ping) + ' ' + str(downSpeed) + ' ' + str(upSpeed) + '\n')
    logFile.close()
    tweetIDFile.close()

    print '----------------- FINISHED TEST ---------------------'
    
if __name__ == '__main__':
    testSpeed();
