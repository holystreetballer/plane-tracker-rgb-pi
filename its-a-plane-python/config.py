# Create a new config.py file:
echo 'DISTANCE_UNITS = "imperial"
MIN_ALTITUDE = 0

# SFO zone and location
ZONE_HOME = {
    "tl_y": 37.7213,  # SFO + 0.1 deg north
    "tl_x": -122.4790, # SFO - 0.1 deg west
    "br_y": 37.5213,  # SFO - 0.1 deg south
    "br_x": -122.2790  # SFO + 0.1 deg east
}

LOCATION_HOME = [
    37.6213,    # SFO latitude
    -122.3790   # SFO longitude
]' > config.py
