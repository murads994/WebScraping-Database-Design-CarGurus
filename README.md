# Webscraping and Database Design

Web scarping is a skill that allows you to extract valuable data from websites, process it and store it for future use. It can be used in many efficient ways like price monitoring, studying market trend, social media management. The goal of this project is to scrape Cargurus website for used car listing information, create a MongdoDB database to store that information in semi structured format, and use the created dataset to develop Fair Market Value prediction model for used cars. 

## Data Source
As a main source for our data collection process, we used cargurus.com website.
Cargurus is a Massachusets based automotive research and shopping website that
assists users in comparing local listings for used and new cars, and contacting sellers.
We specifically decided to use this website for data collection because it is a well-known
go-to website among potential car buyers and it provides reliable listings collected from
approved sellers or dealerships across the US. It also provides detailed descriptions,
and average market value price for each listing which is relevant to our business
problem. Since location is another important factor affecting given car's price, we
decided to narrow down our dataset to listings collected from San Francisco and Bay
Area(Northern California), to get rid of the confounding effects of location in our model
development process further.

## Web-Scraping Routine
We made extensive use of Selenium, and BeatifulSoup python libraries in our
web-scraping routine. To make the written code more readable we divided the whole
process into 5 different functions. In this section we will break down each step involved
in our web-scraping routine below.

1. As a first step, Using Selenium and chromedriver, we automated a routine that
goes to cargurus.com website, clicks on “buy-used” sub-section of the search 
box, inputs zipcode of San-Francisco(94122) in the relevant input field and clicks
search.

2. Next, we save the search results page to our local machine, and iterate through
upcoming 64 pages of search results and save each of them to our local
machine. We automate the iteration process by searching for the next button’s
text(“Next page”) using its xpath and text() function.

3. After that, we open each of the saved search result pages from our machine,
parse them as beautiful soup objects, and scrape URL’s of individual listings
using their css selector.

4. Then, again using Selenium and chromedriver, we open each of the saved 1003
listing urls, and save them to the local machine.

5. In the next step, we iterate over and open each of the saved listing pages from
our machine and scrape the following information using BeautifulSoup and css
selectors.

6. We stored each listing’s information in a dictionary to make it convenient for
insertion into Mongodb database, and saved resulting dictionaries, in a list.

7. Finally, we inserted resulting dictionaries into a Mongodb database as documents
of a collection.

## Database Design
In order to make sure resulting dataset is ready for business use, we structured it into 2
main collections. First collection, namely, “cargurus_listings” contains technical
information about a given listing, along with its unique identifier VIN number. This
collection is more intended for modeling purpose and designed to keep the features that
can be handy in modeling process. Second collection(“cargurus_listings_avg_price”) ,
contains information about listing’s average market price, cargurus deal rating, and URL
of the listing, along with unique identifier VIN.This database was intended to compare
the results of Fair Price Prediction Model with Average Price given by cargurus. To
ensure coherence and consistency across the dataset, we took several different steps
in formatting each of the individual fields:

1. Each of the fields containing information that could be represented in a numerical
form were stripped of unnecessary text, and symbols using python’s regex library
and stored as integer or float values accordingly.

2. Each of the fields given as strings containing unit measurements were
transformed to be included in the field name, and keys were transformed to be
represented as numerical values. (Engine Size(Liters), Cargo Volume(cubic feet)
and etc.)

3. Both Collections contain 1000 documents each of which could be uniquely
identified with “VIN” field, along with the automatically created index by
MongoDB.

We chose MongoDB as a database of our choice because of its ability to store
semi-structured data. Since, some of the fields we scraped from cargurus website were
car specific such as battery range for electric cars, or bed length for trucks, this was a
very handy feature to have. We used Selenium in our Web-Scraping routine mainly
because it made it very easy to scroll through 65 search result pages, and 1003 listing
pages with the added ability to monitor the page that is currently being accessed. We
stored each of the search result pages, and individual listing pages on our local
machine to be able to cross check the information accessed through web-scraping. We
went for BeautifulSoup as our web-scraping tool because it provides convenient html
parsing of the pages, and easy access to web elements using their css selectors. We
decided to store all of the scraped information from each listing in python dictionaries to
be able to easily insert them into MongoDb collections. In the next section, we will
further talk about the design choices made in the creation of these datasets with respect to added business value, and discuss how these datasets could be used to solve the Fair Market Value price prediction in the used car market.

## Business Use of Dataset
As we discussed earlier, the main goal in the collection and creation of this
database is to prepare a ready to use dataset for developing a fair-market value
prediction model. With the chaotic used car market caused by Covid followed by a
microchip shortage, entrepreneurs in car sales businesses are looking for reliable ways
to value cars. Fair Market Value prediction model is designed to optimize price
valuations in business situations as such. Such models are so much in demand for car
sales business that a lot of well-known online automotive websites such as
Edmunds.com, vinaudit.com, carsxse.com are offering their own fair market value
predictions through convenient to access api calls, that can be obtained through
monthly subscriptions, and fixed rate per api calls for dealerships. In designing our
database, we also took into consideration its business use, and structured our
collections in a way, that they coud be ready for model development and verification
purposes. More Specifically, the first collection(“cargurus_listings”) we designed
contains all the technical details about a car such as Make, Model, Year, Mileage,
Engine Size, Horsepower and etc. This collection is designed to be the main source of
model development for the Fair Market Value prediction model. Each of the documents
included in this collection, contains minimum of 15 and maximum of about 30 fields
containing universal or car specific information. Each of the fields included in this
collection are chosen in a way that they could be used as features in the predictive
model, or for visualization in exploratory data analysis to generate insights. The second
collection (“cargurus_listings_avg_price”) contains fields storing information about car’s
average market price and deal rating provided by cargurus, url to the listing, along with
VIN number which is a unique identifier for each of the documents in both collections.
This dataset is intended for comparing predictions made from a fair market value
prediction model based on the first dataset, with the average price estimate provided by
cargurus. Since similar fair market value predictions are also available from other
sources accessible using car’s VIN number, this collection is designed in a way that it
can be scalep up if the user decides to make use of one of such api’s to get an external
confirmation on car’s fair market value price to be compared with the results produced
by the in house model. In that case, user can just add ann additional field to each of the
documents containing external fair market value estimate. We did not make use of such
external fair market value estimate api’s in our data collection process mainly because
they are costly to use. However, the design choices of this collection have taken into
account the possibility of scaling through the use of external sources. The design
structure of our database ensures that a Fair Market Value prediction model coulde be
developed based on the first collection, and testified against external resources using
the second collection.
