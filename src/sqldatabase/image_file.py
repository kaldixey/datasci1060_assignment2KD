'''
Created on 30 Oct 2018

@author: Mark Altaweel with additions by Mark Lake
'''

import os, sys     

class ImageFile(object):
    '''
        Represents an image file
    '''
    
    path=""
    filename=""
    
    
    def __init__(self, path, filename):
        self.path = path
        self.filename = filename
    
    
    def read_image(self):
        '''
            Read a single image from a file
        '''
        
        ''' The try clause opens the jpg for reading as a binary file '''
        try:
            with open(os.path.join(self.path, self.filename), 'rb') as fin:
                ''' The img is then read ''' 
                img = fin.read()
            
            ''' The img data are returned'''
            return img
            
        except IOError, e:
    
            print "Error %d: %s" % (e.args[0],e.args[1])
            sys.exit(1)
                
                
    def write_image(self, data):
    
        ''' 
            Writes a single image to a file.
        '''
        #print (os.path.join(self.path, self.filename))
    
        try:
            with open(os.path.join(self.path, self.filename), 'wb') as fout:
                fout.write(data[0])  #the binary data are added
    
        except IOError, e:    
            print "Error %d: %s" % (e.args[0], e.args[1])
  
