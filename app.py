import requests
from flask import Flask, render_template

API_URL = "https://api.open-meteo.com/v1/forecast?"
PLANETS = {
    "Earth": 15,
    "Tatooine": 35,
    "Hoth": -40,
    "Mars": -60,
    "Venus": 460,
    "Jupiter": -145,
    "Saturn": -178,
}


app = Flask(__name__)


class LocData:
    def __init__(self, temp_data, loc_data):
        self.city = loc_data["city"]
        self.country = loc_data["country"]
        self.temp_float = temp_data["current"]["temperature_2m"]
        self.temp_unit = temp_data["current_units"]["temperature_2m"]
        self.temp_tuple = self.temp_float, self.temp_unit
        self.temp_str = f"{str(self.temp_float)} {self.temp_unit}"


@app.route("/")
def index():
    data = get_data()

    return render_template("index.html", temp=data.temp_str, city=data.city)


def location_lookup() -> dict:
    try:
        location = requests.get("http://ipinfo.io/json").json()
        print(location)
        return location
    except Exception as e:
        print(e)


def get_coords(location: dict) -> list[str]:
    coords = location["loc"].split(",")
    # print(coords)
    return coords


def get_data() -> dict:
    location = location_lookup()
    coords = get_coords(location)
    lat = coords[0][:5]
    long = coords[1][:5]

    temp_request = "&current=temperature_2m"
    string_coords = f"latitude={lat}&longitude={long}"
    full_url = API_URL + string_coords + temp_request

    try:
        temperature = requests.get(full_url).json()
    except Exception as e:
        return print(e)
    print(temperature)
    return LocData(temperature, location)


# get_coords(location)


# print(location_lookup())

if __name__ == "__main__":
    app.run(debug=True)
