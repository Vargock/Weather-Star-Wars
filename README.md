# Star Wars Weather

Follow this link to the website: https://weather-star-wars.onrender.com/

Star Wars Weather is a Flask-based web application that uses your IP address to fetch local weather data and matches it to a Star Wars planet (e.g., Tatooine, Hoth, Naboo). It displays the temperature, city, and a themed commentary, styled with a Star Wars aesthetic. It's an old idea by Tom Scott's, I just decided to recreate it for learning purposes... and maybe to have some fun with it myself xD

## Features

- Geolocation: Determines your city using ipinfo.io based on IP address.
- Weather Data: Fetches current temperature, rain, snowfall, wind speed, and visibility from open-meteo.com.
- Planet Matching: Compares weather conditions to Star Wars planets, selecting the closest match.
- Dynamic UI: Displays weather with planet-specific colors, images, and witty commentary.
- Fallback: Defaults to Alderaan (no weather data) if location or weather lookup fails.

## AKNOWLEDGMENTS

- ip.info for accurate user's location
- Open-meteo API for current weather
- Tom Scott for the idea)
- Star Wars universe for inspiration
