'''
This gets links to websites from PAS

You only get about 20 objects here as that is how many are per page.

Created on Aug 3, 2016

@author: maltaweel, modified by tcrnmar
'''

from bs4 import BeautifulSoup
import urllib2
from urlparse import urlparse
import re

class PasSearchOnePage(object):
    
    def __init__(self, url):
        ''' Initialise with the search URL '''
        self.url = url
        
        
        ''' Parse HTML of article, aka making soup '''
        soup = BeautifulSoup(urllib2.urlopen(url), "html.parser")

        ''' Scrape for the links that have artefacts.  Here we look for
            the links to pages which have a division or section ("div")
            tag attribute "typeof" with the value "crm:E22_Man-Made_Object" '''
        records = soup.findAll('div',attrs={"typeof":"crm:E22_Man-Made_Object"})

        ''' For loop  that stores the links '''
        self.links = []
        for record in records:
            ''' The "about" tag contains the link '''
            link = record["about"]
            self.links.append(link)
    
    
    def print_results(self):
        print("\nQuery string: "+ self.url)
        print(str(len(self.links)) + " results:")
        for link in self.links:
            print(link)
               
    
    def return_links (self):  
        return (self.links)

class PasSearch(object):
    ''' Iterates through all pages when search results extend to more
        than one page.
        
        * DO NOT alter this code and DO NOT use it for development * 
        There is a risk of loading the server should an error in your code
        produce an infinite loop 
    '''
    
    def __init__(self, url):
        ''' Initialise with the search URL and get the protocol
            and domain part of that (need later for multiple
            page search results '''
        self.url = url
        self.server = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(url))
        self.links = []
       
        ''' Parse HTML of article, aka making soup '''
        print("Page 1 is " + str(self.url))
        soup = BeautifulSoup(urllib2.urlopen(url), "html.parser")
        self.extract_artefact_links(soup)
        next_page = self.get_next_page_link(soup)
        i = 2
        while next_page:
            print("Page " + str(i) + " is " + next_page)
            soup = BeautifulSoup(urllib2.urlopen(next_page), "html.parser")
            self.extract_artefact_links(soup)
            next_page = self.get_next_page_link(soup)
            i = i+1
    
    
    def get_next_page_link(self, soup):
        ''' Link to next page must be a hyperlink and its text
            must contain the word "Next" '''
        link_to_next = soup.findAll("a", href=True, text=re.compile(r"Next"))
        
        if link_to_next:
            ''' Construct the actual url '''
            url = (self.server + link_to_next[0]['href'])
            
            ''' Last page of PAS search results does have a next button 
                which points to top of current page.  For example, the next
                link of a final page for will end "page4#".  
                * CAUTION * - We must test for 
                this to avoid an infinite loop! '''
            print ("URL in fn " + url)
            if (url[-1] != "#"):
                return (url)
            else:
                return (None)
        else:            
            return (None)
    
    
    def extract_artefact_links(self, soup):
        ''' Scrape for the links that have artefacts.  Here we look for
            the links to pages which have a division or section ("div")
            tag attribute "typeof" with the value "crm:E22_Man-Made_Object" '''
        records = soup.findAll('div',attrs={"typeof":"crm:E22_Man-Made_Object"})

        ''' For loop  that stores the links '''
        for record in records:
            ''' The "about" tag contains the link '''
            link = record["about"]
            self.links.append(link)
    
    
    def print_results(self):
        print("\n" + str(len(self.links)) + " results from\n" + str(self.url))
        for link in self.links:
            print(link)
               
    
    def return_links (self):  
        return (self.link)    
