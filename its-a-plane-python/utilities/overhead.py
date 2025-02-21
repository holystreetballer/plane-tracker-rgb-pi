from FlightRadar24.api import FlightRadar24API
from threading import Thread, Lock
from time import sleep
import math
from typing import Optional, Tuple

# SFO coordinates and bounds
SFO_LAT = 37.6213
SFO_LON = -122.3790
SFO_ZONE = {
    "tl_y": SFO_LAT + 0.1,  # Add 0.1 degrees for coverage
    "tl_x": SFO_LON - 0.1,
    "br_y": SFO_LAT - 0.1,
    "br_x": SFO_LON + 0.1
}

# Runway parameters
RUNWAY_28_THRESHOLD = {
    "28L": {"lat": 37.6161, "lon": -122.3580},
    "28R": {"lat": 37.6188, "lon": -122.3530},
    "10L": {"lat": 37.6213, "lon": -122.3790},  # Same as 28R other end
    "10R": {"lat": 37.6191, "lon": -122.3795}   # Same as 28L other end
}

# Configuration
MAX_FLIGHT_LOOKUP = 10
LANDING_ALTITUDE_THRESHOLD = 1000  # feet
TAKEOFF_ALTITUDE_THRESHOLD = 3000  # feet
RUNWAY_PROXIMITY_THRESHOLD = 0.01  # degrees (rough approximation)
RETRIES = 3
RATE_LIMIT_DELAY = 1

class SFORunwayTracker:
    def __init__(self):
        self._api = FlightRadar24API()
        self._lock = Lock()
        self._data = []
        self._new_data = False
        self._processing = False
        self._active_runways = ["28L", "28R"]  # Default to 28L/R configuration

    def determine_runway_config(self, flights):
        """Determine if we're using 28 L/R or 10 L/R based on flight patterns"""
        west_operations = 0
        east_operations = 0
        
        for flight in flights:
            if hasattr(flight, 'heading'):
                if 260 <= flight.heading <= 300:  # Landing/Taking off on 28L/R
                    west_operations += 1
                elif 80 <= flight.heading <= 120:  # Landing/Taking off on 10L/R
                    east_operations += 1
        
        if east_operations > west_operations:
            self._active_runways = ["10L", "10R"]
        else:
            self._active_runways = ["28L", "28R"]

    def determine_operation(self, flight, prev_altitude=None):
        """Determine if aircraft is taking off or landing"""
        if not hasattr(flight, 'altitude') or not hasattr(flight, 'vertical_speed'):
            return None
            
        if flight.altitude <= LANDING_ALTITUDE_THRESHOLD and flight.vertical_speed < 0:
            return "Landing"
        elif flight.altitude <= TAKEOFF_ALTITUDE_THRESHOLD and flight.vertical_speed > 0:
            return "Takeoff"
        return None

    def determine_runway(self, flight):
        """Determine which runway the aircraft is using"""
        if not hasattr(flight, 'latitude') or not hasattr(flight, 'longitude'):
            return None
            
        closest_runway = None
        min_distance = float('inf')
        
        for runway in self._active_runways:
            threshold = RUNWAY_28_THRESHOLD[runway]
            distance = math.sqrt(
                (flight.latitude - threshold['lat'])**2 + 
                (flight.longitude - threshold['lon'])**2
            )
            if distance < min_distance:
                min_distance = distance
                closest_runway = runway
                
        if min_distance <= RUNWAY_PROXIMITY_THRESHOLD:
            return closest_runway
        return None

    def grab_data(self):
        """Start asynchronous data collection"""
        Thread(target=self._grab_data).start()

    def _grab_data(self):
        """Collect data about flights near SFO runways"""
        with self._lock:
            self._new_data = False
            self._processing = True

        data = []
        
        try:
            bounds = self._api.get_bounds(SFO_ZONE)
            flights = self._api.get_flights(bounds=bounds)
            
            # Determine current runway configuration
            self.determine_runway_config(flights)
            
            # Filter and process flights
            for flight in flights[:MAX_FLIGHT_LOOKUP]:
                retries = RETRIES
                
                while retries:
                    try:
                        details = self._api.get_flight_details(flight)
                        operation = self.determine_operation(flight)
                        runway = self.determine_runway(flight)
                        
                        if operation and runway:
                            flight_data = {
                                "callsign": flight.callsign,
                                "operation": operation,
                                "runway": runway,
                                "aircraft": details.get("aircraft", {}).get("model", {}).get("code", "Unknown"),
                                "airline": details.get("airline", {}).get("name", "Unknown"),
                                "altitude": flight.altitude,
                                "vertical_speed": flight.vertical_speed,
                                "heading": flight.heading
                            }
                            data.append(flight_data)
                        break
                        
                    except (KeyError, AttributeError):
                        retries -= 1
                        sleep(RATE_LIMIT_DELAY)

            with self._lock:
                self._new_data = True
                self._processing = False
                self._data = data
                
        except Exception as e:
            print(f"Error fetching flight data: {e}")
            with self._lock:
                self._new_data = False
                self._processing = False

    @property
    def new_data(self):
        with self._lock:
            return self._new_data

    @property
    def processing(self):
        with self._lock:
            return self._processing

    @property
    def data(self):
        with self._lock:
            self._new_data = False
            return self._data

    @property
    def active_runways(self):
        return self._active_runways

# Example usage
if __name__ == "__main__":
    tracker = SFORunwayTracker()
    
    while True:
        tracker.grab_data()
        while tracker.processing:
            print("Processing...")
            sleep(1)
            
        if tracker.new_data:
            print(f"\nActive runway configuration: {tracker.active_runways}")
            print("\nCurrent runway operations:")
            for operation in tracker.data:
                print(f"{operation['callsign']} - {operation['operation']} on {operation['runway']}")
                print(f"Aircraft: {operation['aircraft']} ({operation['airline']})")
                print(f"Altitude: {operation['altitude']}ft, Vertical Speed: {operation['vertical_speed']}ft/min")
                print("---")
        
        sleep(5)  # Wait before next update