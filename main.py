from flask import Flask, jsonify
from bs4 import BeautifulSoup
from threading import Thread
from waitress import serve
from time import sleep
import requests

app = Flask(__name__)


def scrape():
    url = "https://studentenwerk.sh/de/mensaplandruck?ort=1&mensa=5&aus=2"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    data = {}

    days = soup.find_all("div", class_="tag_headline")
    for day in days:
        date = day.get("data-day")
        menus = day.find_all("div", class_="mensa_menu_detail")

        dishes = []
        for menu in menus:
            dish_name_div = menu.find("div", class_="menu_name menu_name_kleiner")
            price_div = menu.find("div", class_="menu_preis")

            # Extracting dish name, price and other details
            details = menu.get("data-arten").strip().upper() if menu.has_attr("data-arten") else "No details"
            dish_name = dish_name_div.text.strip() if dish_name_div else "No dish name"
            prices = price_div.text.strip() if price_div else "No price"

            vegan = True if "|VN|" in details else False
            vegetarian = True if "|VE|" in details else False
            pork = True if "|S|" in details else False
            beef = True if "|R|" in details else False
            alcohol = True if "|A|" in details else False

            dishes.append({
                "dish": dish_name,
                "prices": prices,
                "vegan": vegan,
                "vegetarian": vegetarian,
                "pork": pork,
                "beef": beef,
                "alcohol": alcohol,
                "details": details
            })

        data[date] = dishes

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

    serve(app, host="0.0.0.0", port=8080)
