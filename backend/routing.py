"""
GraphHopper Routing API Integration
Provides real-time route optimization for food delivery
Calculates optimal routes between donors and NGOs
"""

import requests
from typing import List, Dict, Optional
from geopy.distance import geodesic
import os
from dotenv import load_dotenv

load_dotenv()

GRAPHHOPPER_API_KEY = os.getenv("GRAPHHOPPER_API_KEY", "your-api-key-here")
GRAPHHOPPER_BASE_URL = "https://graphhopper.com/api/1"

class GraphHopperRouter:
    def __init__(self, api_key: str = GRAPHHOPPER_API_KEY):
        self.api_key = api_key
        self.base_url = GRAPHHOPPER_BASE_URL
    
    def calculate_route(
        self, 
        start_lat: float, 
        start_lon: float, 
        end_lat: float, 
        end_lon: float,
        vehicle: str = "car"
    ) -> Dict:
        """
        Calculate route between two points using GraphHopper API
        
        Args:
            start_lat: Starting latitude
            start_lon: Starting longitude
            end_lat: Destination latitude
            end_lon: Destination longitude
            vehicle: Vehicle type (car, bike, foot)
        
        Returns:
            Dictionary with route information
        """
        url = f"{self.base_url}/route"
        
        params = {
            "point": [f"{start_lat},{start_lon}", f"{end_lat},{end_lon}"],
            "vehicle": vehicle,
            "locale": "en",
            "instructions": True,
            "calc_points": True,
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "paths" in data and len(data["paths"]) > 0:
                path = data["paths"][0]
                return {
                    "success": True,
                    "distance_km": round(path.get("distance", 0) / 1000, 2),
                    "time_minutes": round(path.get("time", 0) / 60000, 2),
                    "instructions": path.get("instructions", []),
                    "points": path.get("points", {}),
                    "bbox": path.get("bbox", [])
                }
            else:
                # Fallback to direct distance calculation
                return self._fallback_calculation(start_lat, start_lon, end_lat, end_lon)
                
        except Exception as e:
            print(f"GraphHopper API Error: {str(e)}")
            return self._fallback_calculation(start_lat, start_lon, end_lat, end_lon)
    
    def _fallback_calculation(
        self, 
        start_lat: float, 
        start_lon: float, 
        end_lat: float, 
        end_lon: float
    ) -> Dict:
        """Fallback to geodesic distance calculation if API fails"""
        distance_km = geodesic(
            (start_lat, start_lon), 
            (end_lat, end_lon)
        ).kilometers
        
        # Estimate time (assuming average speed of 40 km/h)
        time_minutes = (distance_km / 40) * 60
        
        return {
            "success": True,
            "distance_km": round(distance_km, 2),
            "time_minutes": round(time_minutes, 2),
            "instructions": [],
            "points": {},
            "bbox": [],
            "fallback": True,
            "note": "Using direct distance calculation"
        }
    
    def optimize_multi_stop_route(
        self,
        start_location: tuple,
        destinations: List[tuple],
        vehicle: str = "car"
    ) -> Dict:
        """
        Optimize route with multiple destinations
        Uses GraphHopper Route Optimization API
        
        Args:
            start_location: (lat, lon) tuple
            destinations: List of (lat, lon) tuples
            vehicle: Vehicle type
        
        Returns:
            Optimized route information
        """
        url = f"{self.base_url}/vrp"
        
        # Build vehicles configuration
        vehicles = [
            {
                "vehicle_id": "vehicle_1",
                "start_address": {
                    "location_id": "start",
                    "lat": start_location[0],
                    "lon": start_location[1]
                },
                "type_id": "default"
            }
        ]
        
        # Build services (delivery points)
        services = []
        for idx, (lat, lon) in enumerate(destinations):
            services.append({
                "id": f"delivery_{idx}",
                "address": {
                    "location_id": f"dest_{idx}",
                    "lat": lat,
                    "lon": lon
                },
                "duration": 300  # 5 minutes per stop
            })
        
        # Build vehicle types
        vehicle_types = [
            {
                "type_id": "default",
                "profile": vehicle,
                "capacity": [10]
            }
        ]
        
        payload = {
            "vehicles": vehicles,
            "services": services,
            "vehicle_types": vehicle_types
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                params={"key": self.api_key},
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "solution": data.get("solution", {}),
                "job_id": data.get("job_id")
            }
        except Exception as e:
            print(f"GraphHopper VRP API Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback": True
            }
    
    def find_nearest_ngos(
        self,
        donor_lat: float,
        donor_lon: float,
        ngo_locations: List[Dict],
        max_distance_km: float = 50
    ) -> List[Dict]:
        """
        Find nearest NGOs to a donor location
        
        Args:
            donor_lat: Donor latitude
            donor_lon: Donor longitude
            ngo_locations: List of NGO location dicts with 'lat', 'lon', 'name', 'id'
            max_distance_km: Maximum distance to consider
        
        Returns:
            Sorted list of NGOs with distance and time information
        """
        results = []
        
        for ngo in ngo_locations:
            ngo_lat = ngo.get("latitude")
            ngo_lon = ngo.get("longitude")
            
            if ngo_lat is None or ngo_lon is None:
                continue
            
            # Calculate route
            route_info = self.calculate_route(
                donor_lat, donor_lon,
                ngo_lat, ngo_lon
            )
            
            if route_info["distance_km"] <= max_distance_km:
                results.append({
                    "ngo_id": ngo.get("id"),
                    "ngo_name": ngo.get("full_name") or ngo.get("organization_name"),
                    "distance_km": route_info["distance_km"],
                    "time_minutes": route_info["time_minutes"],
                    "latitude": ngo_lat,
                    "longitude": ngo_lon,
                    "route_details": route_info
                })
        
        # Sort by distance
        results.sort(key=lambda x: x["distance_km"])
        
        return results

# Singleton instance
graphhopper = GraphHopperRouter()