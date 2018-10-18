import feedparser

# rss link
news_rss = "http://www.aftonbladet.se/nyheter/rss.xml"

news_max = 5

updated = False

newsArray = {}

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
        newsArray[i] = (post.title, post.published)
        print(post.published + " " + post.title)
        
        # Break
        i += 1
        if i == news_max:
            break

def newsUpdated():
    if updated:
        updated = False
        return True
    else:
        return False

news_Parse()