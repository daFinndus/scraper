from flask import Flask, jsonify
from bs4 import BeautifulSoup
from datetime import datetime
from threading import Thread
from waitress import serve
from time import sleep
import requests

app = Flask(__name__)


# This function scrapes the menu from the website
def scrape():
    url = "https://studentenwerk.sh/de/mensaplandruck?ort=1&mensa=5&aus=2"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    data = {}
    days = soup.find_all("div", class_="tag_headline")

    for day in days:
        date = day.get("data-day")
        weekday = datetime.date(datetime.strptime(date, "%Y-%m-%d")).strftime("%A")

        menus = day.find_all("div", class_="mensa_menu_detail")

        dishes = []

        for menu in menus:
            dish_name_div = menu.find("div", class_="menu_name menu_name_kleiner")
            price_div = menu.find("div", class_="menu_preis")

            # Extracting dish name, price and other details
            details_data = menu.get("data-arten").strip().upper() if menu.has_attr("data-arten") else "No details"
            dish_name = ' '.join(dish_name_div.text.strip().split()) if dish_name_div else "No dish name"
            price_data = price_div.text.strip() if price_div else "No price"

            # This will scrape the prices
            student = price_data.split("/")[0].strip() if price_data else "No price"
            staff = price_data.split("/")[1].strip() if len(price_data.split("/")) > 1 else "No staff price"
            guest = price_data.split("/")[2].strip() if len(price_data.split("/")) > 2 else "No guest price"

            prices = {
                "student": student,
                "staff": staff,
                "guest": guest
            }

            # This will scrape the necessary details
            vegan = True if "|VN|" in details_data else False
            vegetarian = True if "|VE|" in details_data else False
            pork = True if "|S|" in details_data else False
            beef = True if "|R|" in details_data else False
            chicken = True if "|G|" in details_data else False
            alcohol = True if "|A|" in details_data else False

            contains = {
                "vegan": vegan,
                "vegetarian": vegetarian,
                "pork": pork,
                "beef": beef,
                "chicken": chicken,
                "alcohol": alcohol,
            }

            streetfood = True if "|STF|" in details_data else False
            greenplate = True if "|GPC|" in details_data else False
            studentrecipe = True if "|PK|" in details_data else False

            awards = {
                "streetfood": streetfood,
                "greenplate": greenplate,
                "studentrecipe": studentrecipe
            }

            dishes.append({
                "dish": dish_name,
                "prices": prices,
                "contains": contains,
                "awards": awards
            })

        # This will scrape the date
        data[date] = {
            "weekday": weekday,
            "dishes": dishes
        }

    return data


@app.route('/', methods=['GET'])
def index():
    menu = scrape()
    return jsonify(menu)


# This function is to ping the backend every 5 minutes so spindown does not occur
def ping():
    url = "https://scraper-usrk.onrender.com/"

    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Ping successful!")
            else:
                print("Ping failed.")
        except requests.exceptions.RequestException:
            print(f"Error while requesting the service.")
        finally:
            sleep(300)


if __name__ == '__main__':
    thread = Thread(target=ping)
    thread.start()

    serve(app, host="0.0.0.0", port=8000)
