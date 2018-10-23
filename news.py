import feedparser
import json

# rss link
news_rss = "http://www.aftonbladet.se/nyheter/rss.xml"

news_max = 5

updated = False

newsArray = {}

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
    for post in newsParser.entries:
        # save to news field
        try:
            if newsArray[i][0] != post.title:
                updated = True
        except Exception:
            updated = False

        newsArray[i] = {'id': i, 'title': post.title, 'date': post.published}
        
        # Break
        i += 1
        if i == news_max:
            break

    # save cached version
    saveJSON()

def saveJSON():
    with open('cached/news.json', 'w') as outfile:
        json.dump(newsArray, outfile)

def getJSON():
    with open('cached/news.json') as infile:
        json_data = infile.read()
        if json_data != "":
            t = json.loads(json_data)
            for element in t:
                newsArray[int(element)] = t[element]
        
        

def newsUpdated():
    if updated:
        print("Updated")
        updated = False
        return True
    else:
        return False