# -*- coding: utf-8 -*-
import requests
import re
import csv
from bs4 import BeautifulSoup as bs
import sys

class goldTinySpider:
    
    def __init__(self):
        self.listInfoUrl = "https://dev.eclipse.org/mailman/listinfo/"
        listInfoXml = requests.get(self.listInfoUrl.strip()).text  #获取list信息
        self.listInfo = re.findall("<a.*?<strong>(.*?)</strong></a>",listInfoXml)
        self.metrics = ['Domainkey-signature', 'Delivered-to', 'Thread-index', 'From', 'Accept-language', 'Importance', 'Sensitivity', 'Auto-submitted','User-agent', 'Thread-topic', 'Newsgroups', 'Date', 'Organization', 'Openpgp', 'Deferred-delivery']
        self.keyValue = ['project','title','Follow-Ups']
        self.csvfile = file('Spider.csv','wb')
        self.writer = csv.writer(self.csvfile)
        self.count = 0

    def spyUrl(self,listname):
        urlInfo = "http://dev.eclipse.org/mhonarc/lists//"+ listname +"/threads.html"
        msgPage = requests.get(urlInfo.strip()).text
        msgList = re.findall('<a.*?name=.*?href="(.*?)">',msgPage)  #提取每个项目名称中msg编号
        for msgstr in msgList:
            try:
                msgDict = dict.fromkeys(self.keyValue+self.metrics,"NA")
                msgUrl = "http://dev.eclipse.org/mhonarc/lists//"+ listname +"/"+ msgstr
                msgXml = requests.get(msgUrl.strip(),timeout = 5).text   #加了个时间控制
                msgSoup = bs(msgXml,'lxml')
                #project name
                msgDict["project"] = listname
                #title
                title = msgSoup.title.string
                msgDict["title"] = title
                #head message
                tmpList = msgSoup.find_all('li')
                tmpMsgXml = []
                for i in tmpList:
                    if i.em:
                        tmpMsgXml.append(i)
                for name in tmpMsgXml:
                    tmp = []
                    for s in name.stripped_strings:
                        tmp.append(s)
                    if tmp[0] in self.metrics:
                        value = ""
                        for j in range(1,len(tmp)):
                            value = value + tmp[j]
                        msgDict[tmp[0]] = value
                #Follow-Ups
                followUpTmp = msgSoup.find_all("strong",string = "Follow-Ups")
                if followUpTmp:
                    followUpList = []
                    value = ""
                    for i in followUpTmp[0].parent.stripped_strings:
                        followUpList.append(i)
                    for j in range(1,len(followUpList)):
                        value = value + followUpList[j]
                    msgDict['Follow-Ups'] = value
                #finish spider
                #write to csv
                if self.count == 0:
                    self.write_csv(msgDict.keys())
                self.write_csv(msgDict.values())
                self.count = self.count + 1
                print self.count,msgDict['project'],msgDict['title']
            except requests.Timeout as e1:
                print type(e1)
            except requests.ConnectionError as e2:
                print type(e2)
            except AttributeError as e3:
                print type(e3)

    def write_csv(self,lists):
        self.writer.writerow(lists)
                
def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
    mySpider = goldTinySpider()
    #print mySpider.urlInfo
    for listname in mySpider.listInfo:
        mySpider.spyUrl(listname)
    mySpider.csvfile.close()

if __name__=="__main__":
    main()
