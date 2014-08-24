#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests, wget, sys, os

MW_KEY = "59a2199b-d3f1-4eda-8c3f-8b1f570a4811"

def main():
  downloadAudio("los+angeles", "mw", "en")


def downloadAudio(keyword, engine, path = None):
  # data processing
  keyword = unicode(keyword).strip().replace(" ","+")
  engine = unicode(engine).lower()
  print 'Try to search "%s" using engine %s' % (keyword, engine)
  
  found, url = audioLink(keyword, engine)
  print "Return Audio Link: %s" % url

  if found == True:
    oldname = wget.download(url) 
    moveFile(oldname, keyword, path, engine = "youdao")
  else:
    pass
  
# return (true/false, audio_link)
def audioLink(keyword, engine, **argvs):
  engine = engine.lower()
  
  # Youdao 
  if engine in ["youdao","youda", "yd"]:
    # default = 1 if not specifiy
    type = argvs.get("type") or "1" 
    url = u"http://dict.youdao.com/dictvoice?audio=%s&type=%s" % (keyword, type)
    return (True, url)
 
  # Merriam-Webster
  elif engine in ["merriam", "mw"]:
    query = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/%s?key=%s"
    print "Return Query URL: %s" % (query % (keyword, MW_KEY))
    soup = getSoup(query % (keyword, MW_KEY))
    url = parseMerriamWebsterSoup(soup)
    if url != None:
      return (True, url)
    else:
      return (False, None)
  
  # Invalid Engine Name
  else:
    return (False, None)



###################################
### Merriam-Webster 
###################################

def parseMerriamWebsterSoup(soup):

  if soup.find("suggestion") != None:
    print "Found no result\nSuggested Words\n"
    for (index, suggestion) in enumerate(soup.find_all("suggestion")):
      print "%02i. %s\n" % ((index+1), suggestion.string) 
    return None
    
  elif soup.find("sound") == None:
    print "No audio file has been found."
    return None
  
  else:
    audioName = soup.find("sound").find("wav").string
    url = "http://media.merriam-webster.com/soundc11/%s/%s" % (audioName[0], audioName)
    return url    


###################################
### General Helper Function
###################################


def getSoup(url):
  r = requests.get(url)
  soup = BeautifulSoup(r.text)
  return soup

def checkFileExist(file, path = "."):
  filesInSearchedPath = os.listdir(".")
  return file in filesInSearchedPath

# dirnames can be formatted as "foo" or "foo/bar"
# function return true if it is executed succesffully 
def createDirectory(dirnames):
  # unicodize the dirnames, remove trailing space & forward slash
  dirnames = unicode(dirnames).strip("/ ")

  try:
    currPath = u"./"
    for dirname in dirnames.split("/"):
      files = os.listdir(currPath)
      if not(dirname in files) or not(os.path.isdir(currPath + dirname)):
        os.mkdir(currPath + dirname)
      currPath += dirname + "/"
  except:
    return False
  else:
    return True

# rename the filename while maintaining the extension
# move to the provided path if provided
def moveFile(oldFullname, newName, path = None, **argvs):
  # get the newfile based on the extension of the old filename
  if "." in oldFullname:
    extention = oldFullname.split(".")[-1]
    newFullname = u"%s.%s" % (newName, extention)
  elif argvs.get("engine") == "youdao":
    newFullname = u"%s.%s" % (newName, "mp3")
  else:
    newFullname = newName

  if path == None:
    os.rename(oldFullname, newFullname)
  else:
    path = path.strip("/ ")
    createDirectory(path)
    os.rename(oldFullname, path + "/" + newFullname)

if __name__ == "__main__":
  main()
