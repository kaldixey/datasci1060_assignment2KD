'''
ARCL0160 Assessment 2 2018

@author: CTRL0
'''
'''os and urllib imported for filepath manipulation'''
import os
import urllib

'''relevant classes imported for webscraping and database development'''
from webscraping.webscrape import PasRecord
from webscraping.getlinks import PasSearchOnePage
from sqldatabase.sqlite_database import SQLiteDatabase

''' Set up locations of folders to store and retrieve data and images.'''
project_folder = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
data_folder = os.path.join(project_folder, "data")
image_folder = os.path.join(data_folder, "all_available_images")
incomplete_image_folder = os.path.join(data_folder, "incomplete_buckles")
print ("Data will be saved in\n" + data_folder + "\n")

'''Identify page to scrape list of object URLs from. Convert filepath name to URL for use in beautifulsoup'''
results_page = os.path.join(project_folder, "test_files", "Search results from the database Page_ 1.html")
search_url = ("file:" + urllib.pathname2url(results_page))
print("Scraping data from " + results_page + "\n")

'''Create database to store table(s)'''
db_filename = "pasdata.db"
database = SQLiteDatabase(os.path.join(data_folder, db_filename))

'''Create table(s) to store inside database'''
database.create_table("Buckles", "PasID TEXT PRIMARY KEY, Description TEXT, Length FLOAT, Width FLOAT, Thickness FLOAT, Image BLOB")

'''Create an instance of PasSearchOnePage to scrape search results and return record links as a list'''
search_page = PasSearchOnePage(search_url)
links_list = search_page.return_links()

'''Call functions from webscrape on each record to extract desired information and store in the database'''
for link in links_list:
    record = PasRecord(link)
    pasid = record.report_object_id()
    description = record.scrape_main_topic()
    length = record.scrape_attribute("length")
    width = record.scrape_attribute("width")
    thickness = record.scrape_attribute("thickness")
    image = record.scrape_image(image_folder)
    image_filename = record.report_object_image_filename()
    database.insert_row("Buckles", [pasid, description, length, width, thickness, image])
    database.update_image(image_folder, image_filename, "Buckles", pasid)

print("\n" + str(len(links_list)) + " records updated\nImages saved to " + str(image_folder))

'''print statement to check table (commented out for optional use)'''    
#database.print_table("Buckles")

'''Query database for buckles where the word incomplete is mentioned in description. Insert results into a list'''
print("\nIDs of incomplete buckles:")
incomplete_buckles = database.extract_value("PasID", "Buckles", "Description", "LIKE", "%incomplete%")
incomplete_list = [item for items in incomplete_buckles for item in items]
for item in incomplete_list:
    print(item)

'''Extract an image of each incomplete buckle identified above and save to incomplete_buckles folder'''
print("\nExtracting images of incomplete buckles and saving to " + str(incomplete_image_folder))

for item in incomplete_list:
    database.extract_image_file("Buckles", item, incomplete_image_folder, "Image", "PasID")

database.close()
print ("\nJob done")

