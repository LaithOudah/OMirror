import feedparser
import json

# rss link
news_rss = "http://www.aftonbladet.se/nyheter/rss.xml"

news_max = 5

updated = False

newsArray = []
sortedArray = []

def setRSS(rss):
    global news_rss
    news_rss = rss

def setMax(max):
    global news_max
    news_max = max

def news_Parse():
    global updated, newsArray
    newsParser = feedparser.parse(news_rss)
    
    i=0
    
    # empty list
    newsArray = []
    
    for post in newsParser.entries:
        # save to news field
        try:
            if newsArray[i].get("title") != post.title:
                updated = True
        except Exception:
            updated = False

        newsArray.append({'id': i, 'title': post.title, 'date': post.published})
        
        # Break
        i += 1
        if i == news_max:
            break

    # save cached version
    if not newsArray:
        saveJSON()

def saveJSON():
    with open('cached/news.json', 'w') as outfile:
        json.dump(newsArray, outfile)

def getJSON():
    global newsArray, sortedArray
    with open('cached/news.json') as infile:
        json_data = infile.read()
        if json_data != "":
            t = json.loads(json_data)
            i = 0
            
            # EMpty list
            newsArray = []
            sortedArray = []
            
            for element in t:
                newsArray.append(element)
                i += 1
            
            # Sort list
            sortedArray = sorted(newsArray, key=lambda k: k['id'])
        
def newsUpdated():
    global updated
    if updated:
        updated = False
        return True
    else:
        return False

news_Parse()