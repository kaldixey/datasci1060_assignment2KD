'''
Created on 30 Oct 2018

@author: Mark Lake with code from Mark Altaweel
'''

import sqlite3 as lite
import sys
from image_file import ImageFile


class SQLiteDatabase(object):
    '''
    This class represents an SQLite database.
    The constructor will set con to the object that represents the database
    connection (the name 'con' is arbitrary)
    '''
    filename = ""
    con = None


    def __init__(self, filename):
        '''
        This attempts to connect to the named file as an SQLite database.
        It will create the database if it does not exist. 
        Note that the process is placed within try, except, and finally statements.
        '''
        self.filename = filename
        
        try:
    
            ''' Connects to the test.db. and creates it if it does not exist. '''
            self.con = lite.connect(self.filename)
            '''Prints a list of any tables in the database'''
            cursor = self.con.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            print("Opened database " + self.filename)
            print("Contains tables: " + str(cursor.fetchall()))
  
        except lite.Error, e:
            ''' If it was not possible to open the database, an error is reported and the process ends''' 
            print "Error %s:" % e.args[0]
            sys.exit(1)     
        
        
    def close(self):
        if self.con:
            self.con.close() 
            print ("\nClosed database " + self.filename)
        else:
            print ("\nDatabase " + self.filename + " was not open!")
            
    
    def create_table(self, table, columns):
        '''
            This function creates a table with a user specified name and user specified
            columns.  The columns must be specified as exactly the string that would be provided
            in the CREATE TABLE SQL statement.
        '''
        
        ''' Assemble the SQL string '''
        sql_string1 = "DROP TABLE IF EXISTS %s" % table
        sql_string2 = "CREATE TABLE %s (%s)" % (table, columns)
        summary_string = "Table Created: %s (%s)" % (table, columns)
        print(summary_string)
     
        try:
            cur = self.con.cursor()
            cur.execute(sql_string1)
            cur.execute(sql_string2)
            self.con.commit()   
           
        except lite.Error, e:
            ''' Or, if there was an error, roll back to the previous state '''
            if self.con:
                self.con.rollback()
                print "Error %s\nRolled back to previous state" % e.args[0]
        
        
    def extract_image_file (self, table, key, path, image_col, ID_col):
        '''
            Extracts the image data stored in the database and writes it to an image file.
        ''' 
        
        ''' Create a suitable filename using the key, which is guaranteed to be unique'''
        
        
        filename = str(key) + "_image.jpg"
        #print("Image filename " + filename)
        image = ImageFile(path, filename)
        
        sql_string = "SELECT %s FROM %s WHERE %s=?" % (image_col, table, ID_col)
              
        try:
            # first call is to the database
            cur = self.con.cursor()    
            cur.execute(sql_string, (key,)) 
            data = cur.fetchone()  
    
            #now write that image (or binary data) result
            image.write_image(data) 

            print("Extracted %s from item %s in %s" % (filename, str(key), table))  

        except lite.Error, e:
            print "Error %s:" % e.args[0]


    def extract_value(self, return_col, table, search_col, comparison, value):
        '''
            Runs a query on the database and returns any matching values as the first item in a tuple
        '''    
        
        ''' Assemble the SQL string '''
        sql_string = "SELECT %s FROM %s WHERE %s %s ?" % (return_col, table, search_col, comparison)
        #print("Comparator " + comparison)
        #print(sql_string)
        
        ''' Execute the SQL statement.  When passing 'value' it is converted to the first item in a tuple'''
        try:
            cur = self.con.cursor()
            cur.execute(sql_string, (value,))
            self.con.commit()   
            rows = cur.fetchall()
            return(rows)
            
        except lite.Error, e:
            ''' Or, if there was an error, roll back to the previous state '''
            if self.con:
                self.con.rollback()
                print "Error %s\nSearch failed" % e.args[0]
                
                
    def insert_row(self, table, data):
        '''
            Inserts a row into a user-specified table. The data should be passed in as a list and no of values should match
            no of columns in the destination table.
        '''
        
        ''' Assembles the SQL string.
            The for loop ensures there are as many placeholders as there are columns in the data.
            See https://docs.python.org/2/library/sqlite3.html for further info'''
        sql_string = "INSERT INTO %s VALUES(" % table
        for i in range(1, len(data)):
            sql_string += "?,"
        sql_string += "?)"        
        #print(sql_string)
     
        ''' Now execute the SQL statement.  Note that you need to pass the actual data as the
            second argument to execute '''
        try:
            cur = self.con.cursor()
            cur.execute(sql_string, data)
            self.con.commit()   
            ''' This will tell us if any rows have been updated '''
            #print "Number of rows updated: %d" % cur.rowcount
           
        except lite.Error, e:
            ''' Or, if there was an error, roll back to the previous state '''
            if self.con:
                self.con.rollback()
                print "Error %s\nRolled back to previous state" % e.args[0]
                
                        
    def print_table(self, table):
        '''
            Prints all the rows in the given table.
        '''
        
        ''' Creates the SQL query string.  The preferred way of adding the contents of variables
            into an SQL string is to use the placeholder '?' but that doesn't seem to be possible
            when the variable contains the table name.  This solution uses string formatting, but
            a program where security is an issue should really check that the table name exists
            (see e.g. discussion at
            https://stackoverflow.com/questions/3247183/variable-table-name-in-sqlite. '''
        sql_string = "SELECT * FROM %s" % table
        
        try:
            cur = self.con.cursor()
            cur.execute(sql_string)

            rows = cur.fetchall()
            print ("\nTable " + table + " contains:")
            for row in rows:
                print(row)
                #print(type(row))
                #print(row[1])
        
        except lite.Error, e:
            print "Error %s\nQuery failed" % e.args[0]
                
                
    def update_image(self, path, filename, table, key):
        '''
            Adds a single image to an entry in the database
        '''
        
        image = ImageFile(path, filename)
        data = image.read_image()
        
        try:    
            cur = self.con.cursor()
    
            ''' Converts data to SQLite binary representation'''
            image_data = lite.Binary(data)
  
            #cur.execute("ALTER TABLE Cars ADD COLUMN Figure BLOB")
    
            ''' Assembles the SQL string '''
            sql_string = "UPDATE %s SET %s=? WHERE PasID=?" % (table, "Image")
            
            ''' Execute the SQL statement and commit the changes '''
            cur.execute(sql_string, (image_data, key))
            self.con.commit()  
            
            #print("\nAdded %s to item %s in %s" % (filename, str(key), table))  
    
        except lite.Error, e:
            if self.con:
                self.con.rollback()
                print "Error %s\nRolled back to previous state" % e.args[0]
    
                
                
    def update_value(self, table, key, column, value):
        '''
            This updates a table in the database by selecting a single entry 
            and updating the associated columns with new data.
        '''    
        
        ''' Assemble the SQL string '''
        sql_string = "UPDATE %s SET %s=? WHERE Id=?" % (table, column)
        #print(sql_string)
        
        ''' Execute the SQL statement, passing the relevant data '''
        try:
            cur = self.con.cursor()
            cur.execute(sql_string, (value, key))
            self.con.commit()   
            #print "Number of rows updated: %d" % cur.rowcount
            
        except lite.Error, e:
            ''' Or, if there was an error, roll back to the previous state '''
            if self.con:
                self.con.rollback()
                print "Error %s\nRolled back to previous state" % e.args[0]
     
     

                    


        