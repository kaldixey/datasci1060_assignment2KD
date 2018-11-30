'''
This simply gets some data from a record within PAS.

The data recovered are the object, image, description and other attribute data

Created on Jul 27, 2016

@author: maltaweel, modified by tcrnmar
'''

import os
from bs4 import BeautifulSoup
import time
import urllib2

class PasRecord(object):  
    '''This class contains methods to scrape useful information from a single record page on the portable antiquities scheme database'''
    def __init__(self, url):
        self.url = url
        
        ''' Current time stamp when data was downloaded '''
        self.timestamp = time.asctime() 

        ''' Full filename of associated image file (if any) '''
        self.image_filename = None

        ''' Parse HTML of article, aka making soup '''
        self.soup = BeautifulSoup(urllib2.urlopen(self.url), "html.parser")
        title = self.soup.find('title').getText()
        self.object_id = title.split()[2]


    def report_url(self):
        '''returns the URL'''
        return (self.url)


    def report_object_id(self):
        '''returns the unique object ID'''
        return (self.object_id)


    def report_object_image_filename(self):
        '''returns the filename of the object image, if applicable'''
        return (self.image_filename)


    def scrape_main_topic(self):
        ''' gets the main topic and description, which should be the object in this link '''
        obj = self.soup.find('h1').getText()
        #print (obj)

        ''' gets the PAS description about the object '''
        text=self.soup.find("div",attrs={"property":"pas:description"})

        ''' gets rid of the html tags and keeps the text between <p> '''
        finalText=text.find('p').getText()

        ''' prints the final result '''
        return(finalText)
    

    def scrape_image(self, path):
        ''' scrapes the main image from the article into a specified folder'''
        links = self.soup.findAll('img')
        for link in links:    
            '''gets the link that is in src (i.e., an image from html) '''
            link = link["src"]
    
            ''' Skip links without finds.org '''
            #if "https://finds.org.uk/images/" not in link:  
            if "file://" not in link:
                continue
            
            ''' Skip thumbnails '''
            if "thumbnails" in link:
                continue
    
            ''' downloads the image link and prints (optional)'''
            #print(link)  
            download_img = urllib2.urlopen(link)
    
            ''' constructs a suitable filename, creates the image file stream,
                writes the binary data, and closes the file stream'''
            ext = link.rsplit('.', 1)[1]
            filename = self.object_id + "_" + self.timestamp.replace(" ", "_").replace(":", "_") + "." + ext
            if os.path.exists(os.path.join(path, filename)) == False:
                try:
                    txt = open(os.path.join(path, filename), "wb")
                    txt.write(download_img.read())
                    txt.close()
                except:
                    print ("Failed to save " + filename)
                else:
                    #print ("\nSaved image of " + self.object_id + " as " + filename)
                    self.image_filename = filename
            else:
                print("\nImage already saved")
              
    def scrape_attribute(self, attribute):
        '''Generic function to scrape any specified simple attribute from a span tag. Attribute argument must be a string'''
        try:
            attr = (self.soup.select_one("span[property*=pas:" + attribute + "]").text)
            return(attr)
        except:
            return(None)
        
