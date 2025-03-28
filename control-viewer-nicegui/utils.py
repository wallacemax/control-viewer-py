"""
Utility functions for the Control Viewer application
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
import random
import math
from models import ControlPoint, PointStatus

def json_serial(obj: Any) -> Any:
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def serialize_to_json(data: Any) -> str:
    """Serialize data to JSON string"""
    return json.dumps(data, default=json_serial)

def parse_json(json_str: str) -> Any:
    """Parse JSON string to Python object"""
    return json.loads(json_str)

def generate_sample_data(num_points: int = 10) -> List[ControlPoint]:
    """Generate sample control points for testing"""
    point_types = ["sensor", "actuator"]
    units = ["°C", "kPa", "L/min", "rpm", "V", "A", "%"]
    
    points = []
    for i in range(num_points):
        point_type = random.choice(point_types)
        unit = random.choice(units)
        
        # Create different ranges based on unit
        if unit == "°C":
            min_val, max_val = 0, 100
            value = round(random.uniform(15, 30), 1)
        elif unit == "kPa":
            min_val, max_val = 0, 1000
            value = round(random.uniform(100, 500), 1)
        elif unit == "L/min":
            min_val, max_val = 0, 200
            value = round(random.uniform(10, 100), 1)
        elif unit == "rpm":
            min_val, max_val = 0, 3000
            value = round(random.uniform(500, 2000), 0)
        elif unit == "V":
            min_val, max_val = 0, 240
            value = round(random.uniform(110, 230), 1)
        elif unit == "A":
            min_val, max_val = 0, 100
            value = round(random.uniform(5, 20), 2)
        else:  # %
            min_val, max_val = 0, 100
            value = round(random.uniform(0, 100), 1)
        
        # Determine status based on value
        if value < min_val + (max_val - min_val) * 0.1 or value > max_val - (max_val - min_val) * 0.1:
            status = PointStatus.WARNING
        elif value < min_val + (max_val - min_val) * 0.05 or value > max_val - (max_val - min_val) * 0.05:
            status = PointStatus.ALARM
        else:
            status = PointStatus.NORMAL
            
        point = ControlPoint(
            id=f"{point_type[:1]}-{i+1:02d}",
            name=f"{point_type.capitalize()} {i+1}",
            description=f"Sample {point_type} point #{i+1}",
            value=value,
            unit=unit,
            min_value=min_val,
            max_value=max_val,
            timestamp=datetime.now(),
            status=status,
            type=point_type
        )
        
        points.append(point)
    
    return points

def generate_simulated_value(point: ControlPoint) -> float:
    """Generate a simulated value for a control point based on its previous value"""
    if point.value is None:
        # Generate initial value
        if point.min_value is not None and point.max_value is not None:
            mid_point = (point.min_value + point.max_value) / 2
            return round(random.uniform(mid_point * 0.8, mid_point * 1.2), 2)
        else:
            return round(random.uniform(0, 100), 2)
    
    # Generate new value based on previous value
    # Add some random variation but keep within bounds
    variation = random.uniform(-5, 5)
    
    # More realistic variation based on the unit
    if point.unit == "°C":
        variation = random.uniform(-0.5, 0.5)
    elif point.unit == "kPa":
        variation = random.uniform(-10, 10)
    elif point.unit == "L/min":
        variation = random.uniform(-2, 2)
    elif point.unit == "rpm":
        variation = random.uniform(-50, 50)
    elif point.unit == "%":
        variation = random.uniform(-2, 2)
    
    new_value = point.value + variation
    
    # Keep within bounds if specified
    if point.min_value is not None:
        new_value = max(point.min_value, new_value)
    if point.max_value is not None:
        new_value = min(point.max_value, new_value)
    
    # Round to appropriate precision
    if point.unit in ["°C", "V", "kPa", "L/min", "%"]:
        new_value = round(new_value, 1)
    elif point.unit in ["A"]:
        new_value = round(new_value, 2)
    else:
        new_value = round(new_value, 0)
    
    return new_value

def calculate_status(point: ControlPoint) -> PointStatus:
    """Calculate the status of a control point based on its value and limits"""
    if point.value is None or point.min_value is None or point.max_value is None:
        return PointStatus.UNKNOWN
    
    range_size = point.max_value - point.min_value
    
    # Warning threshold: within 10% of min or max
    warn_low = point.min_value + range_size * 0.1
    warn_high = point.max_value - range_size * 0.1
    
    # Alarm threshold: within 5% of min or max
    alarm_low = point.min_value + range_size * 0.05
    alarm_high = point.max_value - range_size * 0.05
    
    if point.value <= point.min_value or point.value >= point.max_value:
        return PointStatus.ERROR
    
    if point.value <= alarm_low or point.value >= alarm_high:
        return PointStatus.ALARM
    
    if point.value <= warn_low or point.value >= warn_high:
        return PointStatus.WARNING
    
    return PointStatus.NORMAL