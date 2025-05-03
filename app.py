import requests
import random
from flask import Flask, render_template, request

API_URL = "https://api.open-meteo.com/v1/forecast?"
# Dictionary of Star Wars planets' conditions to which your local weather conditions will be compared to
PLANETS = {
    "Tatooine": {
        "temperature": 40,
        "rain": 0,
        "snowfall": 0,
        "wind_speed": 20,
        "visibility": 10000,
        "commentary": [
            "I'd tell you to be wary of Tusken Raiders, but... the heat will probably kill you sooner.",
            "Two suns, no shade  —grab a droid and head to Mos Eisley before you fry!",
            "Sandstorms incoming!",
            "This Tatooine scorcher makes a podrace feel like a breeze!",
        ],
        "color": "rgba(245, 200, 150, 0.4)",
        "image_path": "/static/images/tatooine.jpg",
    },
    "Hoth": {
        "temperature": -40,
        "rain": 0,
        "snowfall": 10,
        "wind_speed": 30,
        "visibility": 500,
        "commentary": [
            "Bundle up or find a tauntaun to stay warm!",
            "Wampa alert! Stay inside unless you want to be an ice sculpture.",
            "Blizzard on Hoth? More likely than you think!",
            "Echo Base is buried in snow again. Stay frosty out there!",
        ],
        "color": "rgba(200, 220, 255, 0.4)",
        "image_path": "/static/images/hoth.webp",
    },
    "Endor": {
        "temperature": 20,
        "rain": 5,
        "snowfall": 0,
        "wind_speed": 10,
        "visibility": 6000,
        "commentary": [
            "Watch for Ewoks, they are in the trees!",
            "Light rain on Endor, who could have thought of such a thing?",
            "Misty forests and chirping Ewoks — keep your blaster dry in this drizzle.",
            "Why would Wookiee, 8-foot-tall, want to live on Endor, with a bunch of 2-foot-tall Ewoks?",
        ],
        "color": "rgba(100, 150, 100, 0.4)",
        "image_path": "/static/images/endor.jpg",
    },
    "Mustafar": {
        "temperature": 50,
        "rain": 0,
        "snowfall": 0,
        "wind_speed": 15,
        "visibility": 3000,
        "commentary": [
            "GET IN SHADE, NOW — unless you want to melt.",
            "Mustafar’s lava flows are extra toasty today. Avoid the high ground!",
            "Ash and heat — beatiful sights! For a sith...",
            "Lava rivers are bubbling. Watch your step!",
        ],
        "color": "rgba(128, 53, 17, 0.4)",
        "image_path": "/static/images/mustafar.jpg",
    },
    "Alderaan": {
        "temperature": 0,
        "rain": 0,
        "snowfall": 0,
        "wind_speed": 0,
        "visibility": 0,
        "commentary": [
            "Are you sure you're in the right place? There's nothing here!",
            "Alderaan’s just a memory now — blame the Death Star for this cosmic void.",
            "No weather, no planet — just the eerie silence of Alderaan’s remains.",
            "Lost in space? Alderaan’s gone, and so’s any hope of a forecast!",
        ],
        "color": "rgba(0, 0, 0, 0.8)",
        "image_path": None,
    },
    "Kamino": {
        "temperature": 22,
        "rain": 20,
        "snowfall": 0,
        "wind_speed": 40,
        "visibility": 2000,
        "commentary": [
            "Brace for the deluge — Kamino’s storms never quit!",
            "Rain’s pounding Kamino’s oceans — hope you aren't outside",
            "Stormy seas and howling winds — Kamino’s forecast rarely changes!",
            "Kamino’s waves are crashing, so try not to go swimming.",
        ],
        "color": "rgba(100, 150, 200, 0.4)",
        "image_path": "/static/images/kamino.jpg",
    },
    "Dagobah": {
        "temperature": 28,
        "rain": 4,
        "snowfall": 0,
        "wind_speed": 5,
        "visibility": 1000,
        "commentary": [
            "Tread lightly — all manner of things dwell in this foggy swamp!",
            "Dagobah’s mists hide Yoda… and some nasty swamp creatures. Watch your step!",
            "Drizzle and fog—perfect for Jedi training, terrible for dry boots.",
            "This swamp’s humidity is strong with the Force. Seek Yoda, but don’t get stuck!",
        ],
        "color": "rgba(100, 120, 80, 0.4)",
        "image_path": "/static/images/dagobah.jpg",
    },
    "Bespin": {
        "temperature": 15,
        "rain": 2,
        "snowfall": 0,
        "wind_speed": 50,
        "visibility": 4000,
        "commentary": [
            "Be careful when flying! Well, also just in general.",
            "Cloud City’s winds are fierce — hold onto your cape, Lando!",
            "Bespin’s skies are gusty today. Don’t fall off those floating platforms!",
            "High-altitude chills and howling winds—Bespin’s not for the faint-hearted.",
        ],
        "color": "rgba(206, 179, 152, 0.4)",
        "image_path": "/static/images/bespin.jpg",
    },
    "Naboo": {
        "temperature": 25,
        "rain": 1,
        "snowfall": 0,
        "wind_speed": 8,
        "visibility": 12000,
        "commentary": [
            "Enjoy the clear weather, but be wary of Gungans...",
            "Naboo’s sunny plains are perfect! Especially for someone who abhors sand...",
            "Light breeze, clear skies — perfect time for a picnic with the Queen!",
            "Naboo’s beauty shines today. Just don’t mention the Trade Federation.",
        ],
        "color": "rgba(113, 166, 155, 0.4)",
        "image_path": "/static/images/naboo.jpeg",
    },
    "Geonosis": {
        "temperature": 45,
        "rain": 0,
        "snowfall": 0,
        "wind_speed": 25,
        "visibility": 3000,
        "commentary": [
            "Hot and dry... also droid factories and flying bugs, but just ignore them.",
            "Geonosis’s dust storms are brutal, Geonosians are worse.",
            "Scorching heat and droid clankers — welcome to Geonosis’s arena!",
            "This arid wasteland’s buzzing with trouble. Stay sharp or get stung!",
        ],
        "color": "rgba(200, 152, 100, 0.4)",
        "image_path": "/static/images/geonosis.jpg",
    },
}

app = Flask(__name__)


class LocData:
    def __init__(self, weather_data, loc_data):

        if loc_data:
            data = weather_data["current"]
            units = weather_data["current_units"]
            self.city = loc_data["city"]
            self.country = loc_data["country"]
            self.temp_float = data["temperature_2m"]
            self.temp_unit = units["temperature_2m"]
            self.temp_tuple = self.temp_float, self.temp_unit
            self.temp_str = f"{str(self.temp_float)} {self.temp_unit}"
            self.rain = data["rain"]
            self.snowfall = data["snowfall"]
            self.wind = data["wind_speed_10m"]
            self.visibility = data["visibility"]

        else:
            self.city = "Unknown"
            self.country = "Unknown"
            self.temp_float = 0
            self.temp_unit = "°C"
            self.temp_tuple = (0, "°C")
            self.temp_str = "0 °C"
            self.rain = 0
            self.snowfall = 0
            self.wind = 0
            self.visibility = 0


@app.route("/")
def index():
    weather_data = fetch_loc_and_temp()
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
        # Get client IP from environ (PythonAnywhere-specific)
        user_ip = (
            request.environ.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            or request.environ.get("REMOTE_ADDR")
            or request.headers.get("X-Real-IP")
            or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or (request.access_route[0] if request.access_route else None)
        )
        if not user_ip:
            return {}
        # url = f"http://ipinfo.io/json"
        # Call ipinfo.io
        url = f"http://ipinfo.io/{user_ip}/json"

        response = requests.get(url, timeout=5)
        location = response.json()

        if not location or "loc" not in location:
            return {}
        return location
    except Exception as e:
        return {}


def get_coords(location: dict) -> list[str]:
    if not isinstance(location, dict) or not location or "loc" not in location:
        return ["0", "0"]
    coords = location["loc"].split(",")
    return coords


def find_closest_planet(local_data: LocData) -> tuple[str, str, str, str]:
    if local_data is None or (
        local_data.temp_float == 0
        and local_data.rain == 0
        and local_data.snowfall == 0
        and local_data.wind == 0
        and local_data.visibility == 0
    ):
        return (
            "Alderaan",
            random.choice(PLANETS["Alderaan"]["commentary"]),
            PLANETS["Alderaan"]["color"],
            None,
        )

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
            penalty = 10000
        if planet == "Geonosis" and (local_data.rain > 0 or local_data.snowfall > 0):
            penalty = 10000
        if planet == "Mustafar" and (local_data.rain > 0 or local_data.snowfall > 0):
            penalty = 10000
        if planet == "Hoth" and local_data.snowfall < 1:
            penalty = 10000
        if planet == "Naboo" and (local_data.rain > 5 or local_data.snowfall > 0):
            penalty = 10000
        if planet == "Dagobah" and local_data.rain < 1:
            penalty = 10000
        if planet == "Endor" and local_data.rain > 10:
            penalty = 10000

        distance = temp_diff + rain_diff + snow_diff + wind_diff + vis_diff + penalty

        if distance < min_distance:
            min_distance = distance
            closest_planet = planet

    planet_commentary = random.choice(PLANETS[closest_planet]["commentary"])
    planet_color = PLANETS[closest_planet]["color"]
    planet_image_path = PLANETS[closest_planet]["image_path"]

    return closest_planet, planet_commentary, planet_color, planet_image_path


def fetch_loc_and_temp() -> LocData:
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
