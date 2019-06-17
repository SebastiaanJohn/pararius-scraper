import re
import requests
import pandas as pd
import time
from bs4 import BeautifulSoup


def scrape_data():
    city = input("Enter the city you want to scrape: ").lower()
    min_price = int(input("Enter the min price you want to pay: "))
    max_price = int(input("Enter the max price you want to pay: "))
    page = 1
    records = []

    while True:
        if page == 1:
            url = f"https://www.pararius.com/apartments/{city}/{min_price}-{max_price}"
        else:
            url = f"https://www.pararius.com/apartments/{city}/{min_price}-{max_price}/page-{page}"

        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        results = soup.find_all("li", attrs={"class": "property-list-item-container "})

        print(f"page {page} loading...")

        for result in results:
            # Gets the type of house (appartment, studio, house)
            type_house = result.find("span", attrs={"class": "type"}).text

            # Gets the name and adress of the item
            house_title = result.find("h2").find("a").text.split()[1:]
            house_title = " ".join(house_title)

            # Gets the location data (postal codel, neighborhood)
            location = (
                result.find("ul", attrs={"class": "breadcrumbs"})
                .find_all("li")[0]
                .text.split()
            )
            postal_code = " ".join(location[:2])
            part_of_city = location[-1]

            # Gets the amount of bedrooms
            bedrooms = result.find("li", attrs={"class": "bedrooms"}).text.split()[0]

            # Gets the surface area in m2 of the house
            surface = int(result.find("li", attrs={"class": "surface"}).text.split()[0])

            # Gets if the house if the house is furnished or not
            furniture = result.find("li", attrs={"class": "furniture"}).text.split()[0]

            # Gets the url of the house
            link = result.find("a")["href"]

            # Gets the description of the house
            description = result.find("p", attrs={"class": "description"}).text

            # Gets the estate agent of the house
            estate_agent = (
                result.find("p", attrs={"class": "estate-agent"}).find("a").text
            )

            # Gets the amount of rent of the house, and if it's inclusive or exclusive
            rent = result.find("p", attrs={"class": "price"}).text.split()[0]
            rent_regex = float(re.sub("\D", "", rent))
            inclusive = result.find("p", attrs={"class": "price"}).text.split()[2][1:-1]

            # Gets the available and offered from dates, from the detail page of the house
            stored_data = []
            detail_list = []

            r2 = requests.get(f"https://www.pararius.com{link}")
            soup2 = BeautifulSoup(r2.text, "html.parser")
            details = soup2.find_all("dd")
            for detail in details:
                stored_data.append(detail)

            # available from date
            available = str(stored_data[-3])
            available_regex = re.sub(r"<.*?>", "", available)
            detail_list.append(available_regex)

            # offered since date
            offered = str(stored_data[-1])
            offered_regex = re.sub(r"<.*?>", "", offered)
            detail_list.append(offered_regex)

            # Ads all the items to a tuple
            records.append(
                (
                    house_title,
                    type_house,
                    part_of_city,
                    postal_code,
                    bedrooms,
                    rent_regex,
                    inclusive,
                    surface,
                    furniture,
                    detail_list[0],
                    detail_list[1],
                    description,
                    estate_agent,
                    link,
                )
            )

        # Goes to the next page if possible, otherwise breaks
        if soup.find("li", attrs={"class": "next"}) is None:
            break

        print(f"page {page} completed!")

        # Added delay to stop overloading the servers
        time.sleep(5)

        page += 1

    print(f"page {page} completed!")
    print("Extracted all data.")

    return records


def make_csv(data):
    # Creates a dataframe with Pandas
    df = pd.DataFrame(
        data,
        columns=[
            "Title",
            "Type",
            "Location",
            "Postal Code",
            "Bedrooms",
            "Rent",
            "Inclusive",
            "Surface (m2)",
            "Furnished",
            "Available from",
            "Offered since",
            "Description",
            "Agent",
            "Link",
        ],
    )
    # Creates a csv file from the data frame
    df.to_csv("house_data.csv", index=False)


d = scrape_data()
make_csv(d)
