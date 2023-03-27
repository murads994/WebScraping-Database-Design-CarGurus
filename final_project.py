### BAX422 - Final Project 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
import time
import pymongo
import json
import http.client, urllib.parse
import re


def main():
    ### Refer to function definitons below for detailed description of
    ### what each function is doing and how it works

    get_result_pages()

    listing_urls = get_listing_urls()

    save_listing_pages(listing_urls)

    list_of_dics = scrape_listings(listing_urls)

    create_mongodb_collection(list_of_dics[0], list_of_dics[1])









def get_result_pages():

    ### First, we will be going to https://www.cargurus.com/ website, 
    ### and search for used car listings near San Francisco(near zipcode 94122) using selenium
    ### then we will browse through the result pages and  save each one of them to our machine

    ### Later on we will scrape those saved web pages for individual listing urls
    
    ### Setting Up the driver``
    service = Service("/chromedriver")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(100)
    driver.set_script_timeout(1200)
    driver.set_page_load_timeout(100)

    ### cargurus url
    url = "https://www.cargurus.com/"

    ### Go to the url using selenium
    driver.get(url)
    time.sleep(1)

    ###Click on Buy Used sub-section of search box
    buy_used = driver.find_element(By.XPATH, "//span[text()='Buy Used']")
    buy_used.click()
    time.sleep(1)

    ### Inputting San Francisco's zip code into zip search box(94122) and pressing enter
    input_box = driver.find_element(By.XPATH, "//*[@id='dealFinderZipUsedId_dealFinderForm']")
    input_box.send_keys("94122")
    input_box.send_keys(Keys.RETURN)

    ### Save the resulting page to disk
    source = driver.page_source
    filename = "cargurus_search_1.htm"
    file = open(filename,"w")
    file.write(source)
    time.sleep(2)

    ### Do the same thing for 65 pages
    for i in range(64):
        next_button = driver.find_element(By.XPATH, "//span[text()='Next page']")
        next_button.click()
        source = driver.page_source
        filename = f"cargurus_search_{i+2}.htm"
        file = open(filename,"w")
        file.write(source)
        time.sleep(2)

    driver.quit()



def get_listing_urls(): 

    ### In this function we will access each of the search result pages we have saved,
    ### and scrape all the urls of individual listings from each page

    listing_urls = []

    for i in range(65):
        #### Opening the file
        filename = f"cargurus_search_{i+1}.htm"
        file = open(filename, 'r')
        doc = BeautifulSoup(file, 'html.parser')

        ### Select all the listings urls
        listings = doc.select("a.lmXF4B.c7jzqC.A1f6zD")
        base_url = "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity=&zip=94122"
        for i in range(len(listings)):
            listing_urls.append(base_url + listings[i]['href'])
    
    print(listing_urls)
    print(len(listing_urls))
    return listing_urls



def save_listing_pages(listing_urls):
    service = Service("/chromedriver")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(100)
    driver.set_script_timeout(1200)
    driver.set_page_load_timeout(100)



    ### In this function we will open each of the listing urls and save the page to our local machine
    for i in range(len(listing_urls)):
        driver.get(listing_urls[i])
        time.sleep(5)
        source = driver.page_source
        filename = f"listing_{i+1}.htm"
        file = open(filename,"w")
        file.write(source)
        time.sleep(2)



def scrape_listings(listing_urls):

    ### We will be iterating over downloaded listing pages and scraping each of them for car information
    list_of_dic = []
    list_of_dic2 = []

    for j in range(1003):
        
        ### Opening the file
        filename = f"listing_{j+1}.htm"
        file = open(filename, 'r')
        doc = BeautifulSoup(file, 'html.parser')
        print(filename)

        ### Handling deleted listings
        got_away = doc.select("span.nobr")
        if len(got_away) != 0:
            print(f"Deleted Listing: {filename}")
            continue

        ###Extracting feature keys and values
        feature_keys = doc.select("dt.om75fw")
        feature_values = doc.select("dd.BivK6Q")
        
        ### Iterating over and Saving key:value pairs into a dictionary
        output_dic={}
        output_dic2={}
        for i in range(len(feature_keys)):
            
            ### Omit NHTSA ratings as they do not really affect the price
            if feature_keys[i].text == "NHTSA rollover rating:" or feature_keys[i].text == "NHTSA side crash rating:" or feature_keys[i].text == "NHTSA frontal crash rating:" or feature_keys[i].text == "NHTSA overall safety rating:":
                continue
            
            ### Strip ":" from key names
            key_name = str(feature_keys[i].text)
            key_name = re.sub(':', '', key_name)

            ### Get key values
            key_value = str(feature_values[i].text)

            ### Handle key name modifications and data types

            ### Omit this key-value pair as information is already contained in used key
            if key_name.__contains__("Certified"):
                continue
            
            ### Omit because not necessary for business use        
            if key_name.__contains__("Stock number"):
                continue

            ### Add VIN to the second dictionary as well      
            if key_name.__contains__("VIN"):
                output_dic2[key_name] = key_value    

            ### Some listings containg long text in Combined Gas Mileage element, strip it
            if key_name.__contains__("Combined gas mileage"):
                key_name = "Combined gas mileage"
            
            ### Change value to be integer, and naming to indicate the measurement unit
            if key_name.__contains__("Front legroom"):
                key_name = "Front legroom(in)"
                key_value = int(re.sub('[^0-9\.]', '', key_value))

            ### Change value to be integer, and naming to indicate the measurement unit
            if key_name.__contains__("Back legroom"):
                key_name = "Back legroom(in)"
                key_value = int(re.sub('[^0-9\.]', '', key_value))

            ### Change value to be integer, and naming to indicate the measurement unit
            if key_name.__contains__("Cargo volume"):
                key_name = "Cargo volume(cubicfeet)"
                key_value = int(re.sub('[^0-9\.]', '', key_value))

            ### Change value to be integer
            if key_name.__contains__("Mileage"):
                key_value = int(re.sub('[^0-9\.]', '', key_value))
            
            ### Change value to be integer
            if key_name.__contains__("gas mileage"):
                key_value = int(re.sub('[^0-9\.]', '', key_value))
            
            ### Change value to be integer, and naming to indicate the measurement unit
            if key_name.__contains__("Fuel tank size"):
                key_name = "Fuel tank size(gal)"
                key_value = int(re.sub('[^0-9\.]', '', key_value))

            ### Change value to be integer, and naming to indicate the measurement unit
            if key_name.__contains__("Battery capacity"):
                key_name = "Battery capacity(kWh)"
                key_value = float(re.sub('[^0-9\.]', '', key_value))

            ### Change value to be integer, and naming to indicate the measurement unit
            if key_name.__contains__("Battery charge time (240V)"):
                key_name = "Battery charge time(240V-hours)"
                key_value = float(re.sub('[^0-9\.]', '', key_value))
            
            ### Change value to be integer, and naming to indicate the measurement unit
            if key_name.__contains__("Battery charge time (120V)"):
                key_name = "Battery charge time(120V-hours)"
                key_value = float(re.sub('[^0-9\.]', '', key_value))

            ### Change value to be integer, and naming to indicate the measurement unit
            if key_name.__contains__("Battery range"):
                key_name = "Battery range(miles)"
                key_value = int(re.sub('[^0-9\.]', '', key_value))

            ### Change value to be integer, and naming to indicate the measurement unit
            if key_name.__contains__("Bed length"):
                key_name = "Bed length(in)"
                key_value = int(re.sub('[^0-9\.]', '', key_value))

            ### Change value to be integer
            if key_name.__contains__("Horsepower"):
                key_value = int(re.sub('[^0-9\.]', '', key_value))

            ### Change value to be integer
            if key_name.__contains__("Doors"):
                key_value = int(re.sub('[^0-9\.]', '', key_value))
            
            ### Change value to be integer
            if key_name.__contains__("Year"):
                key_value = int(re.sub('[^0-9\.]', '', key_value))
            
            ### Change value to be integer, and naming to indicate the measurement unit
            if key_name.__contains__("Engine"):
                key_name = "Engine Size(Liter)"
                ### Extracting engine size from expression like "182 hp 2.5L H4"
                ### into a float value 2.5
                key_value = float(re.search(r'\d+(\.\d+)?(?=L)', key_value)[0])

            ### Add key value pair to dictionary
            output_dic[key_name] = key_value

        ### Add price to both dictionaries
        price = doc.select("div.sVIZRf")[0].text
        price = int(re.sub('[^0-9\.]', '', price))
        output_dic["Price"] = price
        
        ### Add avg market price
        avg_market_price = doc.select("h4.wFcdCl")[0].text
        avg_market_price = int(re.sub('[^0-9\.]', '', avg_market_price))
        output_dic2["Average Market Price"] = avg_market_price

        ### Add how good of a deal this is
        deal = doc.select("span.RJvEVf.woFqWQ")[0].text
        output_dic2["Deal"] = deal

        ### Add url
        output_dic2["URL"] = listing_urls[j]
        
        ### add dictionary to a list
        list_of_dic.append(output_dic)
        list_of_dic2.append(output_dic2)

        
    print("List of Dictionaries:")
    print(list_of_dic)
    print(list_of_dic2)
    return(list_of_dic, list_of_dic2)



def create_mongodb_collection(list_of_dic, list_of_dic2):
    ### In this function we will push all the collected info into mongodb database

    ### Connect to MongoDb
    client = pymongo.MongoClient()
    db = client["final_project"]
    collection = db["cargurus_listings"]
    collection2 = db["cargurus_listings_avg_price"]
    
    collection.drop()
    collection2.drop()


    ### Insert one document for each listing
    ### Use the list of dictionaries we created previously
    for i in range(len(list_of_dic)):
        insertion = collection.insert_one(list_of_dic[i])
    
    for i in range(len(list_of_dic2)):
        insertion = collection2.insert_one(list_of_dic2[i])

    print("Collections were Created and all the documents were inserted into it")

if __name__ == "__main__":
    main()

