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

    # This will scrape the menu
    data = {}
    food = {}
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

        # Also add the currywurst, which is always available
        currywurst = {
            "dish": "Currywurst mit Pommes",
            "prices": {
                "student": "5,30 €",
                "staff": "5,30 €",
                "guest": "5,30 €",
            },
            "contains": {
                "vegan": False,
                "vegetarian": False,
                "pork": True,
                "beef": True,
                "chicken": False,
                "alcohol": False
            },
            "awards": {
                "streetfood": False,
                "greenplate": False,
                "studentrecipe": False
            }
        }

        # These are all available drinks of the canteen
        drinks = {
            "warmgetraenke": [
                {"name": "Cappuccino", "price": "2,10 €"},
                {"name": "Café Crema", "price": "2,10 €"},
                {"name": "Filterkaffee", "price": "1,40 €"},
                {"name": "Milchkaffee", "price": "2,10 €"},
                {"name": "Latte Machhiato", "price": "2,10 €"},
                {"name": "Espresso", "price": "1,50 €"},
                {"name": "Heiße Schokolade", "price": "1,70 €"},
                {"name": "Tee", "price": "1,40 €"},
                {"name": "Heißes Wasser", "price": "0,50 €"}
            ],
            "kaltgetraenke": [
                {"name": "Waterkant Sturmflut (0.5 L)", "price": "1,10 €"},
                {"name": "Waterkant Ebbe (0.5 L)", "price": "1,10 €"},
                {"name": "Fritz Getränke (0.33 L)", "price": "2,00 €"},
                {"name": "Waysa Green Original (0.33 L)", "price": "2,00 €"},
                {"name": "Waysa White Apple (0.33 L)", "price": "2,50 €"},
                {"name": "Erdinger Hefe Alkoholfrei (0.33 L)", "price": "2,40 €"},
                {"name": "Wittenseer Blutorange (0.5 L)", "price": "1,95 €"},
                {"name": "Flora Power Mate (0.5 L)", "price": "2,50 €"},
                {"name": "Sinalco Getränke (0.5 L)", "price": "1,55 €"},
                {"name": "Sprottenwasser (0.75 L)", "price": "0,85 €"},
                {"name": "Mio Mio Getränke (0.5 L)", "price": "1,90 € zz. Pfand (0.15 €)"},
                {"name": "AiTea Pfirsisch oder Zitrone (0.5 L)", "price": "3,30 €"}
            ]
        }

        dessert = [
            {
                "name": "Schokopudding mit Vanillesoße",
                "prices": {
                    "student": "1,70 €",
                    "staff": "1,70 €",
                    "guest": "1,70 €",
                },
                "contains": {
                    "vegan": False,
                    "vegetarian": False,
                    "pork": False,
                    "beef": False,
                    "chicken": False,
                    "alcohol": False
                }
            },
            {
                "name": "Vanille Joghurt",
                "prices": {
                    "student": "2,20 €",
                    "staff": "2,20 €",
                    "guest": "2,20 €",
                },
                "contains": {
                    "vegan": False,
                    "vegetarian": False,
                    "pork": False,
                    "beef": False,
                    "chicken": False,
                    "alcohol": False
                }
            },
            {
                "name": "Erdbeer-Fruchtjoghurt",
                "prices": {
                    "student": "2,00 €",
                    "staff": "2,00 €",
                    "guest": "2,00 €",
                },
                "contains": {
                    "vegan": False,
                    "vegetarian": False,
                    "pork": False,
                    "beef": False,
                    "chicken": False,
                    "alcohol": False
                }
            },
            {
                "name": "Milchreis",
                "prices": {
                    "student": "2,10 €",
                    "staff": "2,10 €",
                    "guest": "2,10 €",
                },
                "contains": {
                    "vegan": False,
                    "vegetarian": False,
                    "pork": False,
                    "beef": False,
                    "chicken": False,
                    "alcohol": False
                }
            },
            {
                "name": "Milchreis mit Roter Grütze",
                "prices": {
                    "student": "2,30 €",
                    "staff": None,
                    "guest": None
                },
                "contains": {
                    "vegan": False,
                    "vegetarian": False,
                    "pork": False,
                    "beef": False,
                    "chicken": False,
                    "alcohol": False
                }
            },
            {
                "name": "Chiasamen-Kokos-Pudding",
                "prices": {
                    "student": "2,30 €",
                    "staff": None,
                    "guest": None
                },
                "contains": {
                    "vegan": False,
                    "vegetarian": False,
                    "pork": False,
                    "beef": False,
                    "chicken": False,
                    "alcohol": False
                }
            },
            {
                "name": "Frischer Obstsalat",
                "prices": {
                    "student": "2,60 €",
                    "staff": None,
                    "guest": None
                },
                "contains": {
                    "vegan": False,
                    "vegetarian": False,
                    "pork": False,
                    "beef": False,
                    "chicken": False,
                    "alcohol": False
                }
            },
            {
                "name": "Götterspeise Waldmeister oder Kirsche",
                "prices": {
                    "student": "1,40 €",
                    "staff": "1,80 €",
                    "guest": "2,10 €"
                },
                "contains": {
                    "vegan": False,
                    "vegetarian": False,
                    "pork": False,
                    "beef": False,
                    "chicken": False,
                    "alcohol": False
                }
            },
            {
                "name": "Salted Caramel Pudding",
                "prices": {
                    "student": "1,40 €",
                    "staff": "1,80 €",
                    "guest": "2,10 €"
                },
                "contains": {
                    "vegan": True,
                    "vegetarian": False,
                    "pork": False,
                    "beef": False,
                    "chicken": False,
                    "alcohol": False
                }
            },
            {
                "name": "Schokopudding",
                "prices": {
                    "student": "1,40 €",
                    "staff": "1,80 €",
                    "guest": "2,10 €"
                },
                "contains": {
                    "vegan": True,
                    "vegetarian": False,
                    "pork": False,
                    "beef": False,
                    "chicken": False,
                    "alcohol": False
                }
            },
            {
                "name": "Fruchtdessert Erdbeere",
                "prices": {
                    "student": "1,40 €",
                    "staff": "1,80 €",
                    "guest": "2,10 €"
                },
                "contains": {
                    "vegan": False,
                    "vegetarian": False,
                    "pork": False,
                    "beef": False,
                    "chicken": False,
                    "alcohol": False
                }
            },
            {
                "name": "Sahnepudding Cheesecake",
                "prices": {
                    "student": "1,40 €",
                    "staff": "1,80 €",
                    "guest": "2,10 €"
                },
                "contains": {
                    "vegan": False,
                    "vegetarian": False,
                    "pork": False,
                    "beef": False,
                    "chicken": False,
                    "alcohol": False
                }
            }
        ]

        # This will scrape the date
        food[date] = {
            "weekday": weekday,
            "dishes": dishes,
        }

        # Add the everyday stuff
        data = {
            "food": food,
            "everyday": {
                "currywurst": currywurst,
                "drinks": drinks,
                "dessert": dessert
            }
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
