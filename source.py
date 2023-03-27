# BAX422 - Individual Project
# Murad Salamov
from bs4 import BeautifulSoup
import requests
import time
import re


def main():
    
    ### Programming Part 1 ####
    print("Programming Part 1")
    print("==================================")
    # a) use the URL identified above and write code that loads eBay's search result 
    # page containing sold "amazon gift card". Save the result to file. Give the file the filename "amazon_gift_card_01.htm".
    download_page_1()
    print("==================================")
    # b) take your code in (a) and write a loop that will download the first 10 
    # pages of search results. Save each of these pages to "amazon_gift_card_XX.htm" (XX = page number). 
    # IMPORTANT: each page request needs to be followed by a 10 second pause.  Please remember, you want your program to mimic your 
    # behavior as a human and help you make good purchasing decisions.
    download_search_results()
    print("==================================")
    # c) write code that loops through the pages you downloaded in (b), opens and parses them to a Python or Java xxxxsoup-object.
    # d) using your code in (c) and your answer to 1 (g), identify and print to screen the title, price, and shipping price of each item.
    # also return total number of products with price range exceptions
    n = print_product_info()
    print("==================================")
    # e) using RegEx, identify and print to screen gift cards that sold above face value. 
    # i.e., use RegEx to extract the value of a gift card from its title when possible 
    # (doesn’t need to work on all titles, > 90% success rate if sufficient). 
    # Next compare a gift card’s value to its price + shipping (free shipping should be treated as 0).  If value < price + shipping, then a gift card sells above face value.
    # f) What fraction of Amazon gift cards sells above face value? Why do you think this is the case?
    sold_above_faceval(n)
    print("==================================")
    # a) Following the steps we discussed in class and write code that automatically logs into the website fctables.com .
    # b) Verify that you have successfully logged in:  use the cookies you 
    # received during log in and write code to access https://www.fctables.com/tipster/my_bets/ . 
    # Check whether the word “Wolfsburg” appears on the page.  
    # Don’t look for your username to confirm that you are logged in (it won’t work) and use this page’s content instead.
    print("Programming Part 2")
    print("==================================")
    login_check_mybet()
    print("==================================")
    print("End of Programming Assignments")
    return 0
     



def download_page_1():
    URL = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=amazon+gift+card&_sacat=0&rt=nc&LH_Sold=1&LH_Complete=1&_pgn=1"
    user_agent = {'User-agent': 'Mozilla/5.0'}
    page = requests.get(URL, user_agent)
    doc = BeautifulSoup(page.content, "html.parser")
    filename = "amazon_gift_card_01.htm"
    file = open(filename, "w")
    file.write(str(doc))
    print(f'Search results page 1 is downloaded to {filename}')


def download_search_results():
    URL_loop = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=amazon+gift+card&_sacat=0&rt=nc&LH_Sold=1&LH_Complete=1&_pgn="
    for i in range(10):
        filename = f"amazon_gift_card_{str(i+1).zfill(2)}.htm"
        headers = {'User-Agent':'Mozilla/5.0'}
        URL = URL_loop + str(i+1)
        page = requests.get(URL, headers=headers)
        doc = BeautifulSoup(page.content, "html.parser")
        with open(filename, "w") as f:
            f.write(str(doc))
            print(f'Search results page {i+1} is downloaded to {filename}')
            time.sleep(10)   


def print_product_info():
    count_product_og = 0
    for j in range(10):
        filename = f"amazon_gift_card_{str(j+1).zfill(2)}.htm"
        with open(filename, 'r') as file:
            doc = BeautifulSoup(file, 'html.parser')
            info = doc.select("li.s-item.s-item__pl-on-bottom")
            # title = doc.select("li.s-item.s-item__pl-on-bottom div.s-item__title>span")
            # price = doc.select("li.s-item.s-item__pl-on-bottom span.s-item__price")
            # shipping = doc.select("li.s-item.s-item__pl-on-bottom span.s-item__shipping.s-item__logisticsCost")
            
            for i in range(1,len(info)):
                #Print Product Number
                print(f"Page: {j+1}, Product {i}")

                ### If product price contains a range skip that product overall as advised:
                if info[i].select("span.s-item__price")[0].text.__contains__("to"):
                    print("Invalid Price --- Skip this product")
                    continue
                count_product_og+=1
                
                
                ### if title contains "new listing" strip it
                if info[i].select("div.s-item__title>span")[0].text.__contains__("New Listing"):
                    print(info[i].select("div.s-item__title>span")[0].text.replace('New Listing', ''))
                else:
                    print("Title: " + info[i].select("div.s-item__title>span")[0].text)


                ### Print price
                print("Price: " + info[i].select("span.s-item__price")[0].text)
                
                
                # If shipping info is not included, consider free shipping as advised
                if len(info[i].select("span.s-item__shipping.s-item__logisticsCost"))== 0:
                    print("Free Shipping")
                else:
                    print("Shipping: " + info[i].select("span.s-item__shipping.s-item__logisticsCost")[0].text)
                
            
    print(f"There were {count_product_og} products in 10 pages with exclusion of products with price range values")
    return count_product_og


def sold_above_faceval(n):
    count_product = 0
    count_above_faceval = 0
    for j in range(10):
        
        filename = f"amazon_gift_card_{str(j+1).zfill(2)}.htm"
        with open(filename, 'r') as file:
            doc = BeautifulSoup(file, 'html.parser')
            info = doc.select("li.s-item.s-item__pl-on-bottom")
            
            for i in range(1,len(info)):

                ### If product price contains a range skip that product overall as advised:
                if info[i].select("span.s-item__price")[0].text.__contains__("to"):
                    print("Invalid Price --- Skip this product")
                    continue
                
                
                ### if title contains "new listing" strip it
                title = ""
                if info[i].select("div.s-item__title>span")[0].text.__contains__("New Listing"):
                    title = info[i].select("div.s-item__title>span")[0].text.replace('New Listing', '')
                else:
                    title = info[i].select("div.s-item__title>span")[0].text
                
                
                ### extracting value as a float from title
                title_value = re.findall(r'\$(\d+(?:\.\d+)?)', title)

                ### If our regexp fails to extract a value, we will omit that product overall
                if len(title_value) == 0:
                    continue
                else:
                    title_value = float(title_value[0])

                count_product+=1

                ### extracting price of product as a float out of price string
                price = info[i].select("span.s-item__price")[0].text
                price_value = re.findall(r'\$(\d+(?:\.\d+)?)', price)
                price_value = float(price_value[0])
                
                
                # If shipping info is not included, consider free shipping as advised
                shipping_value = float(0.0)
                shipping = ""
                if len(info[i].select("span.s-item__shipping.s-item__logisticsCost"))== 0:
                    shipping = "Free shipping"
                    shipping_value = float(0.0)
                else:
                    shipping = info[i].select("span.s-item__shipping.s-item__logisticsCost")[0].text
                
                if shipping != "Free shipping":
                    shipping_value = re.findall(r'\$(\d+(?:\.\d+)?)', shipping)
                    shipping_value = float(shipping_value[0])
                else:
                    shipping_value = float(0.0)
                
                
                
                total_price = price_value + shipping_value
                if total_price > title_value:
                    count_above_faceval+=1
                    print(f"Page: {j+1}, Product {i}")
                    print("This Gift Card Sells above the face value.")
                    print(f"Title: {title}")
                    print(f"Price: {price}")
                    print(f"Shipping: {shipping}")

    print(f"Number of giftcards counted(by considering exclusions for price range values): {n}")      
    print(f"Number of giftcards counted(by considering regexp exclusions for title): {count_product}")
    regexp_success = count_product/n
    print(f"RegExp Success Rate: {regexp_success}")
    print(f"Number of GiftCards Selling Above Face Value: {count_above_faceval}")
    fract_above_faceval = count_above_faceval/count_product
    print(f"Proportion of Giftcards Selling above Face Value: {fract_above_faceval}")

    print("I think there might be few reasons why some Giftcards sell above face value: ")
    print("1. Sometimes this might be a part of laundering scheme when a giftcard is bought by a stolen credit card.")
    print("i.e. People will try to cash out the puchases they made by stolen cards this way")
    print("2. Another reason may be that for some people living abroad or not owning a credit card")
    print("this is the only way to make purchases on amazon.")
    print("Additionally, those purchases are relatively anonymus as well, for those who are carefull of their online footprint")


def login_check_mybet():
    URL = "https://www.fctables.com/user/login/"
    user_agent = {'User-agent': 'Mozilla/5.0'}

    page1 = requests.get(URL, user_agent)
    doc1 = BeautifulSoup(page1.content, 'html.parser')

    time.sleep(5) # 5s

    session_requests = requests.session()

    res = session_requests.post(URL, 
                            data = {"login_username" : "msbax422", # your username here
                                    "login_password" : "05Bax422!@", # your password here
                                    "user_remeber" : 1,
                                    "login_action" : 1},
                            headers=user_agent,
                            timeout = 15)
    #
    # This will get us the Cookies.
    # 
    cookies = session_requests.cookies.get_dict()
    print(cookies)
    #
    # And this is the easiest way to remain in session.
    #
    URL2 = "https://www.fctables.com/tipster/my_bets/"
    page2 = session_requests.get(URL2, headers=user_agent, cookies=cookies)
    doc2 = BeautifulSoup(page2.content, 'html.parser')
    doc2_text = doc2.text
    
    print("Checking if our bet is there...")
    ### Check if the bet is there.
    print(bool(doc2.findAll(text = "Wolfsburg 0-0 vs Bayern Munich")))
    ### Alternatively, if we specifically want to look for the word "Wolfsburg" we can do:
    print(bool(doc2_text.__contains__("Wolfsburg")))
    ### or this way
    print(bool(doc2.get_text("Wolfsburg")))

    print("As we can see from the results of tests and printed cookies, we were able to log in to the website, and find our bet in the next page.")
                
if __name__ == '__main__':
	main()