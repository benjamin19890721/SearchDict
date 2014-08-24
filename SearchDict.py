from bs4 import BeautifulSoup
import requests, wget, sys, os

def main():
  downloadAudio("university", "youdao", "en")

def downloadAudio(keyword, engine, path = None):
  engine = unicode(engine).lower()
  found, url = audioLink(keyword, engine)

  if found == True:
    oldname = wget.download(url) 
    moveFile(oldname, keyword, path, engine = "youdao")
  else:
    pass
  
# return (true/false, audio_link)
def audioLink(keyword, engine, **argvs):
  if engine.lower() in ["youdao","youda", "yd"]:
    type = argvs.get("type") or "1" # default = 1 if not specifiy 
    query = u"http://dict.youdao.com/dictvoice?audio=%s&type=%s"
    return True, query % (keyword, type)
  else:
    return False, None

###################################
######### Helper Function #########
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
