#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests, wget, sys, os, re

MW_KEY = "59a2199b-d3f1-4eda-8c3f-8b1f570a4811"

def main():
  downloadAudio("korean", "mw", "en")


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
    url = getMerriamWebsterURL(soup)
    
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
  result = {}
  if soup.find("suggestion") != None:
    result["status"], result["suggestions"] = "no match", []
    for suggestion in soup.find_all("suggestion"):
       result["suggestions"].append(suggestion.string) 
  else:
    result["status"], result["entries"] = "found matches", []
    for entry in soup.find_all("entry"):
      if (entry.find("sound") == None or
          entry.find("sound").find("wav") == None):
        audioName = None
      else:
        audioName = entry.find("sound").find("wav").string

      result["entries"].append({
        "word": entry["id"],
        "audioName": audioName
      })   

  return result

def getMerriamWebsterURL(soup):

  results = parseMerriamWebsterSoup(soup)

  if results["status"] == "no match":
    print "Found no result\nSuggested Words"
    for (index, suggestion) in enumerate(result["suggestions"]):
      print "%02i. %s" % ((index+1), suggestion.string) 
    return None
    
  elif results["status"] == "found matches":
    match = results["entries"][0]
    if match["audioName"] == None:
      print "No audio file has been found."
      return None
    else:
      audioName = match["audioName"]
  
      # According to API, audioName need to be converted to a URL like this:
      # http://media.merriam-webster.com/soundc11/h/heart001.wav

      # Start with the base URL: http://media.merriam-webster.com/soundc11/
      # Add the first letter of the wav file as a subdirectory ("h" in the example above).*
      # Add the name of the wav file.
      # * Regarding the subdirectory element of the URL there are three exceptions:

      # If the file name begins with "bix", the subdirectory should be "bix".
      # If the file name begins with "gg", the subdirectory should be "gg".
      # If the file name begins with a number, the subdirectory should be "number".
      if re.compile("^gg").match(audioName) != None:
        subDirName = "gg"
      elif re.compile("^bix").match(audioName) != None:
        subDirName = "bix"
      elif re.compile("^[0-9]").match(audioName) != None:
        subDirName = "number"
        raise Exception
      else:
        subDirName = audioName[0]

      url = "http://media.merriam-webster.com/soundc11/%s/%s" % (subDirName, audioName)
      return url 
  
  else:
    return None


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
