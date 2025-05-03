import requests
from flask import Flask, render_template

API_URL = "https://api.open-meteo.com/v1/forecast?"
# Dictionary of Star Wars planets' conditions to which your local weather conditions will be compared to
PLANETS = {
    "Tatooine": {
        "temperature": 40,  # Hot desert
        "rain": 0,  # No rain
        "snowfall": 0,  # No snow
        "wind_speed": 20,  # Windy
        "visibility": 10000,  # Clear
        "commentary": "I'd tell you to be wary of Tusken Raiders, but... the heat will probably kill you sooner",
        "color": "rgba(245, 200, 150, 0.4)",
        "image_path": "/static/images/tatooine.jpg",
    },
    "Hoth": {
        "temperature": -40,  # Freezing
        "rain": 0,  # No rain
        "snowfall": 10,  # Heavy snow
        "wind_speed": 30,  # Very windy
        "visibility": 500,  # Low due to snow
        "commentary": "Bundle up or find a tauntaun to stay warm!",
        "color": "rgba(200, 220, 255, 0.4)",
        "image_path": "/static/images/hoth.webp",
    },
    "Endor": {
        "temperature": 20,  # Temperate forest
        "rain": 5,  # Light rain
        "snowfall": 0,  # No snow
        "wind_speed": 10,  # Breezy
        "visibility": 6000,  # Good visibility
        "commentary": "Watch for Ewoks, they are in the trees!",
        "color": "rgba(100, 150, 100, 0.4)",
        "image_path": "/static/images/endor.jpg",
    },
    "Mustafar": {
        "temperature": 50,  # Volcanic heat
        "rain": 0,  # No rain
        "snowfall": 0,  # No snow
        "wind_speed": 15,  # Moderate wind
        "visibility": 3000,  # Hazy due to ash
        "commentary": "GET IN SHADE, NOW",
        "color": "rgba(128, 53, 17, 0.4)",
        "image_path": "/static/images/mustafar.jpg",
    },
    "Alderaan": {
        "temperature": 0,  # Placeholder for missing data
        "rain": 0,
        "snowfall": 0,
        "wind_speed": 0,
        "visibility": 0,
        "commentary": "Are you sure you're in the right place? There's nothing here!",
        "color": None,
        "image_path": None,
    },
    "Kamino": {
        "temperature": 22,  # Mild, oceanic
        "rain": 20,  # Heavy rain
        "snowfall": 0,  # No snow
        "wind_speed": 40,  # Stormy
        "visibility": 2000,  # Low due to rain
        "commentary": "Brace for the deluge — Kamino’s storms never quit!",
        "color": "rgba(100, 150, 200, 0.4)",
        "image_path": "/static/images/kamino.jpg",
    },
    "Dagobah": {
        "temperature": 28,  # Warm, swampy
        "rain": 4,  # Light to moderate drizzle
        "snowfall": 0,  # No snow
        "wind_speed": 5,  # Calm
        "visibility": 1000,  # Foggy
        "commentary": "Tread lightly — all mannet of things dwell in this foggy swamp!",
        "color": "rgba(100, 120, 80, 0.4)",
        "image_path": "/static/images/dagobah.jpg",
    },
    "Bespin": {
        "temperature": 15,  # Cool, high-altitude
        "rain": 2,  # Light rain
        "snowfall": 0,  # No snow
        "wind_speed": 50,  # Very windy
        "visibility": 4000,  # Cloudy
        "commentary": "Be careful when flying! Well, also just in general",
        "color": "rgba(206, 179, 152, 0.4)",
        "image_path": "/static/images/bespin.jpg",
    },
    "Naboo": {
        "temperature": 25,  # Warm, pleasant
        "rain": 1,  # Very light rain
        "snowfall": 0,  # No snow
        "wind_speed": 8,  # Gentle breeze
        "visibility": 12000,  # Clear
        "commentary": "Enjoy the clear weather, but be wary of Gungans...",
        "color": "rgba(113, 166, 155, 0.4)",
        "image_path": "/static/images/naboo.jpeg",
    },
    "Geonosis": {
        "temperature": 45,  # Extremely hot
        "rain": 0,  # No rain
        "snowfall": 0,  # No snow
        "wind_speed": 25,  # Dusty winds
        "visibility": 3000,  # Low due to dust
        "commentary": "Hot and dry... also droid factories and flying bugs, but just ignore them.",
        "color": "rgba(200, 152, 100, 0.4)",
        "image_path": "/static/images/geonosis.jpg",
    },
}


app = Flask(__name__)


class LocData:
    def __init__(self, weather_data, loc_data):
        data = weather_data["current"]  # Weather Values
        units = weather_data["current_units"]  # Weather Units

        self.city = loc_data["city"]  # User's city
        self.country = loc_data["country"]  # User's country

        self.temp_float = data["temperature_2m"]
        self.temp_unit = units["temperature_2m"]
        self.temp_tuple = self.temp_float, self.temp_unit
        self.temp_str = f"{str(self.temp_float)} {self.temp_unit}"

        self.rain = data["rain"]
        self.snowfall = data["snowfall"]
        self.wind = data["wind_speed_10m"]
        self.visibility = data["visibility"]


@app.route("/")
def index():
    weather_data = fetch_loc_and_temp()

    print(
        f"Local weather: temp={weather_data.temp_float}, rain={weather_data.rain}, "
        f"snow={weather_data.snowfall}, wind={weather_data.wind}, vis={weather_data.visibility}"
    )

    closest_planet, commentary, color, image = find_closest_planet(weather_data)
    return render_template(
        "index.html",
        temp=weather_data.temp_str,
        city=weather_data.city,
        planet=closest_planet,
        commentary=commentary,
        color=color,
        image_path=image,
    )


def location_lookup() -> dict:
    try:
        location = requests.get("http://ipinfo.io/json").json()
        return location
    except Exception as e:
        print(e)


def get_coords(location: dict) -> list[str]:
    coords = location["loc"].split(",")
    # print(coords)
    return coords


def find_closest_planet(local_data: dict) -> str:
    if local_data is None or (
        local_data.temp_float == 0
        and local_data.rain == 0
        and local_data.snowfall == 0
        and local_data.wind == 0
        and local_data.visibility == 0
    ):
        return "Alderaan"

    min_distance = float("inf")
    closest_planet = None

    for planet, conditions in PLANETS.items():
        if planet == "Alderaan":
            continue

        temp_diff = (local_data.temp_float - conditions["temperature"]) ** 2
        rain_diff = (local_data.rain - conditions["rain"]) ** 2
        snow_diff = (local_data.snowfall - conditions["snowfall"]) ** 2
        wind_diff = (local_data.wind - conditions["wind_speed"]) ** 2
        vis_diff = ((local_data.visibility - conditions["visibility"]) / 1000) ** 2

        penalty = 0
        if planet == "Tatooine" and (local_data.rain > 0 or local_data.snowfall > 0):
            penalty = 10000  # No rain/snow on Tatooine
        if planet == "Geonosis" and (local_data.rain > 0 or local_data.snowfall > 0):
            penalty = 10000  # No rain/snow on Geonosis
        if planet == "Mustafar" and (local_data.rain > 0 or local_data.snowfall > 0):
            penalty = 10000  # No rain/snow on Mustafar
        if planet == "Hoth" and local_data.snowfall < 1:
            penalty = 10000  # Hoth needs snow
        if planet == "Naboo" and (local_data.rain > 5 or local_data.snowfall > 0):
            penalty = 10000  # Naboo is pleasant, not stormy
        if planet == "Dagobah" and local_data.rain < 1:
            penalty = 10000  # Dagobah needs some rain
        if planet == "Yavin IV" and local_data.rain < 5:
            penalty = 10000  # Yavin IV needs moderate rain

        distance = temp_diff + rain_diff + snow_diff + wind_diff + vis_diff + penalty

        print(
            f"{planet}: temp_diff={temp_diff:.2f}, rain_diff={rain_diff:.2f}, "
            f"snow_diff={snow_diff:.2f}, wind_diff={wind_diff:.2f}, vis_diff={vis_diff:.2f}, "
            f"penalty={penalty}, distance={distance:.2f}"
        )

        if distance < min_distance:
            min_distance = distance
            closest_planet = planet
            # closest_planet = "Alderaan"
            # closest_planet = "Dagobah"
            # closest_planet = "Bespin"
            # closest_planet = "Endor"
            # closest_planet = "Geonosis"
            # closest_planet = "Hoth"
            # closest_planet = "Kamino"
            # closest_planet = "Naboo"
            # closest_planet = "Tatooine"
            # closest_planet = "Mustafar"

            planet_commentary = PLANETS[closest_planet]["commentary"]
            planet_color = PLANETS[closest_planet]["color"]
            planet_image_path = PLANETS[closest_planet]["image_path"]

    return closest_planet, planet_commentary, planet_color, planet_image_path


def fetch_loc_and_temp() -> dict:
    location = location_lookup()
    coords = get_coords(location)
    lat = float(coords[0])
    long = float(coords[1])
    add_request = "&current=temperature_2m,rain,snowfall,visibility,wind_speed_10m"
    string_coords = f"latitude={lat:.4f}&longitude={long}"

    full_url = API_URL + string_coords + add_request

    try:
        weather = requests.get(full_url).json()
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return LocData(
            {
                "current": {
                    "temperature_2m": 0,
                    "rain": 0,
                    "snowfall": 0,
                    "visibility": 10000,
                    "wind_speed_10m": 0,
                },
                "current_units": {
                    "temperature_2m": "°C",
                    "rain": "mm",
                    "snowfall": "mm",
                    "visibility": "m",
                    "wind_speed_10m": "km/h",
                },
            },
            location,
        )

    return LocData(weather, location)


if __name__ == "__main__":
    app.run(debug=True)
