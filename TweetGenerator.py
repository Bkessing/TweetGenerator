import tweepy
import json
import emoji
import sys
import logging
import random


logging.basicConfig(level=logging.INFO)

with open('Config.json') as data_file:    
    data = json.load(data_file)


consumerKey = data["consumer-key"]
consumerSecret = data["consumer-secret"]
accessToken = data["access-token-key"]
accessTokenSecret = data["access-token-secret"]
searchList = ["giveaway -filter:retweets -filter:replies -filter:links"]
order = data["order"]
tweets = data["tweets"]
trainingNumber = data["training-number"]

auth = tweepy.OAuthHandler(consumerKey,consumerSecret)
auth.set_access_token(accessToken,accessTokenSecret)
api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)


def clean_tweet(tweet):
    allchars = [str for str in tweet]
    emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
    cleanTweet = ' '.join([str for str in tweet.split() if not any(i in str for i in emoji_list)])
    return cleanTweet.translate(non_bmp_map)

def getKey(array, i):
    key = ""
    for j in range(i-order,i):
        key = key + array[j]
    return key

def getKey2(word):
    key = ""
    for i in range(len(word)-order,len(word)):
        key = key + word[i]
    return key
    
def splitLetters(sentence):
    return [char for char in sentence]

def calculatePercentages(model):
    for x,y in model.items():
        size = 0
        for i in range(1,len(y),2):
            size+= int(y[i])
        for i in range(1,len(y),2):
            y[i] = y[i] / size
        model[x] = y
               
def printDebug(model):
    for i in model.values():
        if len(i) > 2:
            print(i)

def printFinal(array):
    sentence = ""
    for i in range(order,len(array)-1):
        sentence = sentence + array[i]
    print(sentence)

def prepairTweet(tweetArray):
    prepairedTweet = []
    for i in range(0,order):
        prepairedTweet.append("_")
    for j in range(0,len(tweetArray)):
        prepairedTweet.append(tweetArray[j])
    for z in range(0,order):
        prepairedTweet.append("_")

    return prepairedTweet
    
def getTweet(model):
    sentence = []
    for j in range(0,order):
        sentence.append("_")
    randomNum = 0
    word = ""
    while(word != "_"):
        randomNum = random.random()
        key = getKey2(sentence)
        listWords = model.get(key)
        countWeight = 0
        for i in range(1,len(listWords),2):
            countWeight += float(listWords[i])
            if(float(listWords[i]) + countWeight >= randomNum):
                word = listWords[i-1]
                break
        sentence.append(word)
    printFinal(sentence)
    
def createModel():
    model = {}
    for search in searchList:
        for tweet in tweepy.Cursor(api.search,search, result_type= "latest",count = 100,tweet_mode='extended' ).items(trainingNumber):
        
                
            cleanedTweet = clean_tweet(tweet.full_text)
            tweetArray = splitLetters(cleanedTweet)
            tweetArray = [item.lower() for item in tweetArray]
            prepairedTweet = prepairTweet(tweetArray)
            for i in range(order,len(prepairedTweet)-1):
                key = getKey(prepairedTweet,i)
                if key in model:
                    valueList = model.get(key)
                    if prepairedTweet[i] in valueList:
                        j = valueList.index(prepairedTweet[i])
                        valueList[j+1] = valueList[j+1] + 1
                    else:
                        valueList.append(prepairedTweet[i])
                        valueList.append(1)
                else:
                    tempList = []
                    tempList.append(prepairedTweet[i])
                    tempList.append(1)
                    model[key] = tempList

    calculatePercentages(model)
    print(model.get("giveaway"))
    return model




    

model = createModel()
print(len(model))
for i in range(0,tweets):
    getTweet(model)
    print("")

