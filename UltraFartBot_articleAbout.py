import httplib, urllib, urllib2, base64, json, csv, time
from bs4 import BeautifulSoup

key = '6448c73604de4460a4a3ffd2824ef8e3'

def getData(numArticles, searchString, key):
    headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': key,
    }
    params = urllib.urlencode({
    # Request parameters
    'q': searchString,
    'Count': numArticles,
    })
    try:
        conn = httplib.HTTPSConnection('api.cognitive.microsoft.com')
        conn.request("GET", "/bing/v5.0/news/search?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = json.load(response)
        conn.close()
        return data['value']
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def breitbartExtractor():
    site = "http://www.breitbart.com"
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(site,headers=hdr)
    page = urllib2.urlopen(req)
    soup = BeautifulSoup(page, "lxml")
    topStory = soup.h2.get_text()
    topStory = topStory.encode('ascii', 'ignore')
    #soup.h2.a.get('href') pulls the first link from the first a tag in the first h2 tag in the page,  this should correspond to the top article
    firstStory = site + soup.h2.a.get('href')
    req = urllib2.Request(firstStory,headers=hdr)
    page = urllib2.urlopen(req)
    soup = BeautifulSoup(page, "lxml")
    meta = soup.find_all('meta', {'property':'article:tag'})
    articleTags = []
    for tag in meta:
        articleTags.append(tag.get('content'))
    return articleTags, topStory

def createSearchTerms(headline, website):
    #headlineWords = headline.split(' ')
    #searchTerms = '"' + headlineWords[0] + ' ' + headlineWords[1] + ' ' + headlineWords[2] + ' ' + headlineWords[3] + '" & site:' + website
    searchTerms = headline + ' & site:' + website
    return searchTerms

def getArticleAbout(searchTerms, key):
    data = getData(20, searchTerms, key)
    articleAbout = ''
    if len(data) > 0:
        if 'about' in data[0].keys():
            for item in data[0]['about']:
                if item['name'] != u'Andrew Breitbart':
                    articleAbout += item['name'].encode('ascii', 'ignore') + ','
        else:
            articleAbout = 'Article found but no "about" tags'
    else:
        articleAbout = 'No article found in Bing API'
    return articleAbout

def recordArticleAbout(articleAbout, articleTags, topStory):
    fileName = 'UltraFartBot_articleAbout.csv'
    record = open(fileName, 'a')
    record.write('Timestamp,' + time.strftime("%m/%d/%Y") + ',' + time.strftime("%H:%M:%S") + '\n')
    record.write(topStory + '\n')
    record.write('Bing API About tags:,' + articleAbout + '\n')
    record.write('Breitbart meta tags:,')
    for tag in articleTags:
        record.write(tag + ',')
    record.write('\n')
    record.write('---------' + '\n')
    record.close()

def logExecution(programName):
    logFileName = "UltraFartBot_RunLog.csv"
    runLog = open(logFileName, 'a')
    runLog.write(programName + ',' + time.strftime("%m/%d/%Y") + ',' + time.strftime("%H:%M:%S"))
    runLog.write('\n')
    runLog.close()

articleTags, topStory = breitbartExtractor()
searchTerms = createSearchTerms(topStory, 'breitbart.com')
articleAbout = getArticleAbout(searchTerms, key)
recordArticleAbout(articleAbout, articleTags, topStory)
logExecution('articleAbout')
