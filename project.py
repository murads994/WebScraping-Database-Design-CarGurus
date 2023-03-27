### BAX422 - Individual Project 2
### Murad Salamov
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pymongo
import json
import http.client, urllib.parse



def main():
    ##### q1 - no programming required #####
    url = "https://opensea.io/collection/boredapeyachtclub?search[sortAscending]=false&search[stringTraits][0][name]=Fur&search[stringTraits][0][values][0]=Solid%20Gold"

    ##### Q2 #####
    q2(url)

    ##### Q3 #####
    q3()

    ##### Q4 #####
    q4()

    ##### Q5 #####
    shop_info_list = q5()

    ##### Q6 #####
    q6(shop_info_list)

    ##### Q7 #####
    q7()

    ##### Q8 #####
    update_list = q8()

    ##### Q9 #####
    q9(update_list)
   














##### Q2 #####
def q2(url):
    print("#### Question 2 ####")
    print("==================================")
    ### Setting up the driver ###
    service = Service("/chromedriver")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    driver.set_script_timeout(120)
    driver.set_page_load_timeout(10)


    ### Clicking on each of the top-8 most expensive Bored Apes
    for i in range(8):
        ### Get the results page
        driver.get(url)
        time.sleep(2)

        ### Get the apes by their css selector
        ape_pg = driver.find_elements(By.CSS_SELECTOR, "span.sc-29427738-0.sc-d58c749b-2.eNYnCu.heRZSz")
        
        ### all the apes have same css selector for their names(indexed from 0)
        ape_pg[i].click()
        time.sleep(5)
        ### Save the resulting page to disk
        source = driver.page_source
        filename = f"bayc_{i+1}.htm"
        file = open(filename,"w")
        file.write(source)
        time.sleep(1)
        

    driver.quit()
    print("#### End of Question 2 ####")
    print("==================================")



##### Q3 #####    
def q3():
    print("#### Question 3 ####")
    print("==================================")
    ### Connect to local mongodb server and choose db and collection
    client = pymongo.MongoClient()
    db = client["individual_project2"]
    collection = db["bayc"]
    collection.drop()

    ### Opening the file
    for i in range(8):
        filename = f"bayc_{i+1}.htm"
        file = open(filename, 'r')

        ### Getting ape's name(number)
        doc = BeautifulSoup(file, 'html.parser')
        name = doc.select("h1.sc-29427738-0")[0].text
        
        ### Getting attribute type and their values
        attribute_names = doc.select("div.Property--type")
        attribute_vals = doc.select("div.Property--value")

        ### Combining everything into a dictionary
        attribute_dict = {"Name":name}
        for i in range(len(attribute_names)):
            attribute_dict[attribute_names[i].text] = attribute_vals[i].text

        ### insert a document into a mongodb collection
        insertion = collection.insert_one(attribute_dict)
    
    ### pring resulting collection
    ### Collection of first 8 most expensive ape names and attributes
    print("Collection of first 8 most expensive ape names and attributes:")
    cursor = collection.find()
    for record in cursor:
        print(record)
    print("#### End of Question 3 ####")
    print("==================================")



##### Q4 #####
def q4():
    print("#### Question 4 ####")
    print("==================================")

    URL = "https://www.yellowpages.com/"
    user_agent = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0'}

    ### Make an initial request to the page
    session_requests = requests.session()
    page1 = session_requests.get(URL, headers=user_agent)
    cookies = session_requests.cookies.get_dict()

    ### Now,Make a search request
    URL = "https://www.yellowpages.com/search?search_term=Pizzeria&search_location=San Francisco, CA&search_type=searchbox_top"
    page2 = session_requests.get(URL, 
                            data = {"search_term" : "Pizzeria", 
                                    "search_location" : "San Francisco, CA", 
                                    "search_type" : "searchbox_top"},
                            headers=user_agent,
                            timeout = 15,
                            cookies=cookies)
    
    ### Save the result page to a file
    doc2 = BeautifulSoup(page2.content, 'html.parser')
    filename = "sf_pizzeria_search_page.htm"
    file = open(filename,"w")
    file.write(str(doc2))

    print(f"Pizzeriza Search Result page downloaded to {filename}")
    print("#### End of Question 4 ####")
    print("==================================")


##### Q5 #####
def q5():
    print("#### Question 5 ####")
    print("==================================")
    #### Opening the file
    filename = "sf_pizzeria_search_page.htm"
    file = open(filename, 'r')
    doc = BeautifulSoup(file, 'html.parser')

    ### Select all the listings
    listings = doc.select("div.info")

    ### Remove last 2 featured listings
    listings.remove(listings[len(listings)-1])
    listings.remove(listings[len(listings)-1])

    ### Remove the first - ad listing 
    listings.remove(listings[0])

    ### Create a list of shop infos
    shop_info_list=[]

    for i in range(len(listings)):
        ### Create a shop info dictionary
        shop_info={}

        ### Extracting name from a listing
        name = listings[i].select("h2.n>a>span")[0].text
        shop_info["name"]=name

        ### Extracting search rank from a listing
        search_rank = listings[i].select("h2.n")[0].text
        search_rank = int(search_rank.replace(". "+name,""))
        shop_info["search_rank"]=search_rank

        ### Extracting URL from a listing
        url = listings[i].select("h2.n>a")[0]['href']
        url = "https://www.yellowpages.com" + url
        shop_info["url"]=url


        ###Extracting rating from a listing
        if len(listings[i].select("a.rating.hasExtraRating>div"))!=0:
            rating_list = listings[i].select("a.rating.hasExtraRating>div")[0]["class"]
            rating = 0
            if rating_list[1] == "one":
                rating = 1
            elif rating_list[1] == "two":
                rating = 2
            elif rating_list[1] == "three":
                rating = 3
            elif rating_list[1] == "four":
                rating = 4
            elif rating_list[1] == "five":
                rating = 5

            shop_info["star_rating"]=rating

            #### Extracting Review Count
            rating_count = listings[i].select("a.rating.hasExtraRating>span.count")[0].text
            rating_count = int(rating_count[1:len(rating_count)-1])
            shop_info["no_reviews"]=rating_count


        #### Extracting ta ratings and counts from a listing
        if len(listings[i].select("a.ta-rating-wrapper")) != 0:
            ta_rating_dict = listings[i].select("div.ratings")[0]['data-tripadvisor']
            ta_rating_dict = json.loads(ta_rating_dict)
            ta_rating_count = int(ta_rating_dict["count"])
            ta_rating = float(ta_rating_dict["rating"])
            shop_info["ta_rating"]=ta_rating
            shop_info["no_ta_rating"]=ta_rating_count


        ### Extracting $ signs
        if len(listings[i].select("div.price-range"))!=0:
            dollar_signs = listings[i].select("div.price-range")[0].text
            shop_info["dollar_signs"]=dollar_signs
        
        
        ### Extracting years in business 
        if len(listings[i].select("div.number"))!=0:
            years_in_business = listings[i].select("div.number")[0].text
            shop_info["years_in_business"]=int(years_in_business)

        ### Extracting Review
        if len(listings[i].select("p.body.with-avatar"))!= 0:
            review = listings[i].select("p.body.with-avatar")[0].text
            shop_info["review"]=review

        
        ### Extracting Amenities
        amenities = listings[i].select("div.amenities-info span")
        if len(amenities)!= 0:
            amenities_list=[]
            for j in amenities:
                amenities_list.append(j.text)
            shop_info["amenities"]=amenities_list
        
        shop_info_list.append(shop_info)
        print(shop_info)

    print("#### End of Question 5 ####")
    print("==================================")
    return shop_info_list

##### Q6 #####
def q6(shop_info_list):

    print("#### Question 6 ####")
    print("==================================")

    ### Connect to MongoDb
    client = pymongo.MongoClient()
    db = client["individual_project2"]
    collection = db["sf_pizzerias"]
    collection.drop()

    ### Insert one document for each pizzeria
    ### Use the list of dictionaries we created in q5
    for i in range(len(shop_info_list)):
        insertion = collection.insert_one(shop_info_list[i])

    print("All Documents inserted into sf_pizzerias collection: ")
    cursor = collection.find()
    for record in cursor:
        print(record)
    print("#### End of Question 6 ####")
    print("==================================")

##### Q7 #####
def q7():
    print("#### Question 7 ####")
    print("==================================")

    ### Connecting to MongoDB
    client = pymongo.MongoClient()
    db = client["individual_project2"]
    collection = db["sf_pizzerias"]

    ### Querying URL's
    cursor = collection.find({},{'url':1,'search_rank':1})
    
    user_agent = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0'}
    
    ### iterate over urls and download pages
    for record in cursor:
        url = record['url']
        page = requests.get(url, headers=user_agent)
        doc = BeautifulSoup(page.content, 'html.parser')
        filename = f"sf_pizzerias_{record['search_rank']}.htm"
        file = open(filename, "w")
        file.write(str(doc))
    
    print("#### End of Question 7 ####")
    print("==================================")
    


#### Q8 ####
def q8():
    print("#### Question 8 ####")
    print("==================================")
    update_list = []
    for i in range(30):
        update_dict = {}
        filename = f"sf_pizzerias_{i+1}.htm"
        file = open(filename, 'r')
        doc = BeautifulSoup(file, 'html.parser')

        ### Extracting Address
        adress = doc.select('section#details-card p')[1].text
        adress = adress.replace("Address: ","")
        update_dict["address"] = adress

        ### Extracting Phone
        phone = doc.select('p.phone')[0].text
        phone = phone.replace("Phone:  ","")
        update_dict["phone"] = phone

        ### Extracting Website
        if len(doc.select('p.website'))!=0:
            website = doc.select('p.website')[0].text
            website = website.replace("Website: ","")
            update_dict["website"] = website

        update_list.append(update_dict)
    
    print("Printing Resulting List of Update dictionaries:")
    print(update_list)
    
    print("#### End of Question 8 ####")
    print("==================================")
    return update_list

def q9(update_list):
    print("#### Question 9 ####")
    print("==================================")
    client = pymongo.MongoClient()
    db = client["individual_project2"]
    collection = db["sf_pizzerias"]
    
    conn = http.client.HTTPConnection('api.positionstack.com')
    
    update_l = update_list
    
    for i in range(len(update_l)):
        params = urllib.parse.urlencode({
            'access_key': '54a832085c729a5bb21aacebe498b4b7',
            'query': update_l[i]['address'],
            })

        conn.request('GET', '/v1/forward?{}'.format(params))

        res = conn.getresponse()
        data = res.read()

        pos_stack_api = data.decode('utf8').replace("'", '"')
        json_output = json.loads(pos_stack_api)
        update_l[i]['latitude'] = json_output['data'][0]['latitude']
        update_l[i]['longitude'] = json_output['data'][0]['longitude']
      
    for i in range(len(update_l)):
        collection.update_one({"search_rank": (i+1)},{"$set": update_l[i]})
    
    print("All the fields updated successfully. Printing the final collection: ")
    cursor = collection.find()
    for record in cursor:
        print(record)

    print("#### End of Question 9 ####")
    print("==================================")






if __name__ == '__main__':
    main()