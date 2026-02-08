import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import heapq
from enum import Enum


class GoodsType(Enum):
    FOOD = "food"
    MEDICINE = "medicine"


@dataclass
class Location:
    
    id: str
    name: str
    latitude: float
    longitude: float
    type: str 
    
    def distance_to(self, other: 'Location') -> float:
       #haversine distance
        R = 6371 
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c


@dataclass
class PerishableGoods:
   
    id: str
    name: str
    goods_type: GoodsType
    quantity: float  # in kg or units
    pickup_location: Location
    delivery_location: Location
    time_to_expiry: int  
    priority: int = 1  
    pickup_time_window: Tuple[int, int] = (0, 1440) 
    
    def urgency_score(self) -> float:
        
        # Higher score = more urgent
        time_factor = 1000 / max(self.time_to_expiry, 1)
        priority_factor = (6 - self.priority) * 10
        return time_factor + priority_factor


@dataclass
class Vehicle:
    
    id: str
    name: str
    capacity: float  # in kg or units
    current_location: Location
    speed: float = 40.0  # km/h average speed
    
    def travel_time(self, from_loc: Location, to_loc: Location) -> float:
       
        distance = from_loc.distance_to(to_loc)
        return (distance / self.speed) * 60  # convert hours to minutes


@dataclass
class RouteStop:
    
    location: Location
    action: str
    goods: PerishableGoods
    arrival_time: float  
    estimated_duration: float = 15.0  


@dataclass
class Route:
   
    vehicle: Vehicle
    stops: List[RouteStop] = field(default_factory=list)
    total_distance: float = 0.0
    total_time: float = 0.0
    goods_delivered: List[PerishableGoods] = field(default_factory=list)
    
    def is_feasible(self) -> Tuple[bool, str]:
       
        current_load = 0.0
        
        for stop in self.stops:
            if stop.action == 'pickup':
                current_load += stop.goods.quantity
                if current_load > self.vehicle.capacity:
                    return False, f"Capacity exceeded at {stop.location.name}"
            else:  
                current_load -= stop.goods.quantity
                
                
                if stop.arrival_time > stop.goods.time_to_expiry:
                    return False, f"{stop.goods.name} expired before delivery"
        
        return True, "Route is feasible"
    
    def total_goods_saved(self) -> float:
       
        return sum(g.quantity for g in self.goods_delivered)


class LogisticsOptimizer:
    
    
    def __init__(self, vehicle: Vehicle):
        self.vehicle = vehicle
        
    def optimize_route(self, goods_list: List[PerishableGoods]) -> Route:
      
        if not goods_list:
            return Route(vehicle=self.vehicle)
        
        sorted_goods = sorted(goods_list, key=lambda g: g.urgency_score(), reverse=True)
        
        route = Route(vehicle=self.vehicle)
        current_location = self.vehicle.current_location
        current_time = 0.0
        
        
        picked_up = set()
        delivered = set()
        
        while len(delivered) < len(sorted_goods):
            best_action = None
            best_score = float('-inf')
            best_goods = None
            
           
            for goods in sorted_goods:
                if goods.id in delivered:
                    continue
                
               
                if goods.id not in picked_up:
                    travel_time = self.vehicle.travel_time(current_location, goods.pickup_location)
                    arrival_time = current_time + travel_time
                    
                  
                    if arrival_time <= goods.pickup_time_window[1]:
                      
                        score = goods.urgency_score() - (travel_time * 0.5)
                        
                        if score > best_score:
                            best_score = score
                            best_action = 'pickup'
                            best_goods = goods
                
               
                elif goods.id in picked_up:
                    travel_time = self.vehicle.travel_time(current_location, goods.delivery_location)
                    arrival_time = current_time + travel_time
                    
                    
                    if arrival_time <= goods.time_to_expiry:
                       
                        score = goods.urgency_score() + 50 - (travel_time * 0.3)
                        
                        if score > best_score:
                            best_score = score
                            best_action = 'delivery'
                            best_goods = goods
            
           
            if best_action is None:
                break
            
         
            if best_action == 'pickup':
                travel_time = self.vehicle.travel_time(current_location, best_goods.pickup_location)
                current_time += travel_time
                
                stop = RouteStop(
                    location=best_goods.pickup_location,
                    action='pickup',
                    goods=best_goods,
                    arrival_time=current_time
                )
                route.stops.append(stop)
                picked_up.add(best_goods.id)
                
                current_location = best_goods.pickup_location
                current_time += stop.estimated_duration
                route.total_distance += self.vehicle.current_location.distance_to(current_location) if len(route.stops) == 1 else stop.location.distance_to(current_location)
                
            else:  
                travel_time = self.vehicle.travel_time(current_location, best_goods.delivery_location)
                current_time += travel_time
                
                stop = RouteStop(
                    location=best_goods.delivery_location,
                    action='delivery',
                    goods=best_goods,
                    arrival_time=current_time
                )
                route.stops.append(stop)
                delivered.add(best_goods.id)
                route.goods_delivered.append(best_goods)
                
                current_location = best_goods.delivery_location
                current_time += stop.estimated_duration
        
        route.total_time = current_time
        return route
    
    def calculate_all_paths(self, goods_list: List[PerishableGoods]) -> Dict[str, List[Tuple[Location, float]]]:
      
        all_locations = set()
        all_locations.add(self.vehicle.current_location)
        
        for goods in goods_list:
            all_locations.add(goods.pickup_location)
            all_locations.add(goods.delivery_location)
        
        paths = {}
        locations_list = list(all_locations)
        
        for i, loc1 in enumerate(locations_list):
            for loc2 in locations_list[i+1:]:
                distance = loc1.distance_to(loc2)
                key = f"{loc1.id} -> {loc2.id}"
                paths[key] = [(loc1, 0), (loc2, distance)]
        
        return paths
    
    def find_k_shortest_routes(self, goods_list: List[PerishableGoods], k: int = 3) -> List[Route]:
        
        routes = []
        
        
        route1 = self.optimize_route(goods_list)
        if route1.stops:
            routes.append(route1)
        
        
        route2 = self._optimize_by_distance(goods_list)
        if route2.stops and route2 != route1:
            routes.append(route2)
        
        
        route3 = self._optimize_by_time_window(goods_list)
        if route3.stops and route3 not in routes:
            routes.append(route3)
        
    
        routes.sort(key=lambda r: (r.total_goods_saved(), -r.total_time), reverse=True)
        return routes[:k]
    
    def _optimize_by_distance(self, goods_list: List[PerishableGoods]) -> Route:
        
        route = Route(vehicle=self.vehicle)
        current_location = self.vehicle.current_location
        current_time = 0.0
        picked_up = set()
        delivered = set()
        
        while len(delivered) < len(goods_list):
            min_distance = float('inf')
            best_action = None
            best_goods = None
            
            for goods in goods_list:
                if goods.id in delivered:
                    continue
                
                if goods.id not in picked_up:
                    distance = current_location.distance_to(goods.pickup_location)
                    travel_time = (distance / self.vehicle.speed) * 60
                    
                    if current_time + travel_time <= goods.pickup_time_window[1]:
                        if distance < min_distance:
                            min_distance = distance
                            best_action = 'pickup'
                            best_goods = goods
                
                elif goods.id in picked_up:
                    distance = current_location.distance_to(goods.delivery_location)
                    travel_time = (distance / self.vehicle.speed) * 60
                    
                    if current_time + travel_time <= goods.time_to_expiry:
                        if distance < min_distance - 1: 
                            min_distance = distance
                            best_action = 'delivery'
                            best_goods = goods
            
            if best_action is None:
                break
            
            if best_action == 'pickup':
                travel_time = self.vehicle.travel_time(current_location, best_goods.pickup_location)
                current_time += travel_time
                stop = RouteStop(location=best_goods.pickup_location, action='pickup', 
                               goods=best_goods, arrival_time=current_time)
                route.stops.append(stop)
                picked_up.add(best_goods.id)
                current_location = best_goods.pickup_location
                current_time += stop.estimated_duration
            else:
                travel_time = self.vehicle.travel_time(current_location, best_goods.delivery_location)
                current_time += travel_time
                stop = RouteStop(location=best_goods.delivery_location, action='delivery',
                               goods=best_goods, arrival_time=current_time)
                route.stops.append(stop)
                delivered.add(best_goods.id)
                route.goods_delivered.append(best_goods)
                current_location = best_goods.delivery_location
                current_time += stop.estimated_duration
        
        route.total_time = current_time
        return route
    
    def _optimize_by_time_window(self, goods_list: List[PerishableGoods]) -> Route:
        
        sorted_goods = sorted(goods_list, key=lambda g: (g.time_to_expiry, g.pickup_time_window[1]))
        return self.optimize_route(sorted_goods)


def format_route_output(route: Route) -> str:
    
    output = []
    output.append(f"\n{'='*80}")
    output.append(f"OPTIMIZED ROUTE FOR VEHICLE: {route.vehicle.name}")
    output.append(f"{'='*80}")
    output.append(f"Total Distance: {route.total_distance:.2f} km")
    output.append(f"Total Time: {route.total_time:.2f} minutes ({route.total_time/60:.2f} hours)")
    output.append(f"Goods Delivered: {route.total_goods_saved():.2f} units")
    
    feasible, message = route.is_feasible()
    output.append(f"Route Feasibility: {'✓ FEASIBLE' if feasible else '✗ NOT FEASIBLE'}")
    output.append(f"Status: {message}")
    
    output.append(f"\n{'ROUTE DETAILS':-^80}")
    output.append(f"{'Step':<6}{'Time':<12}{'Action':<12}{'Location':<25}{'Goods':<25}")
    output.append(f"{'-'*80}")
    
    for i, stop in enumerate(route.stops, 1):
        time_str = f"{stop.arrival_time:.1f}m"
        output.append(f"{i:<6}{time_str:<12}{stop.action.upper():<12}"
                     f"{stop.location.name:<25}{stop.goods.name:<25}")
    
    output.append(f"{'='*80}\n")
    return '\n'.join(output)
