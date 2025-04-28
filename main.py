from flask import Flask, jsonify
from bs4 import BeautifulSoup
from waitress import serve
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

            dish_name = dish_name_div.text.strip() if dish_name_div else "No dish name"
            prices = price_div.text.strip() if price_div else "No price"

            dishes.append({
                "dish": dish_name,
                "prices": prices
            })

        data[date] = dishes

    return data


@app.route('/', methods=['GET'])
def index():
    menu = scrape()
    return jsonify(menu)


if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=8080)
