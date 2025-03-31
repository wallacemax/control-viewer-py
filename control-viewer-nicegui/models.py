"""
Data models for the Control Viewer application
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PointType(str, Enum):
    """Type of control point"""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    SCALE = "scale"
    SOME_SCALE_NAME = "{SOME_SCALE_NAME}"

class PointStatus(str, Enum):
    """Status of a control point"""
    UNKNOWN = "unknown"
    NORMAL = "normal"
    WARNING = "warning"
    ALARM = "alarm"
    ERROR = "error"

class ControlPoint(BaseModel):
    """Model for a control point in the system"""
    id: str
    name: str
    description: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    timestamp: Optional[datetime] = None
    status: PointStatus
    type: PointType 
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "id": "temp-01",
                "name": "Temperature Sensor 1",
                "description": "Main room temperature sensor",
                "value": 23.5,
                "unit": "°C",
                "min_value": 0,
                "max_value": 50,
                "timestamp": datetime.now(),
                "status": "normal",
                "type": "sensor"
            }
        }

class ControlGroup(BaseModel):
    """Model for a group of control points"""
    id: str
    name: str
    description: Optional[str] = None
    points: List[str] = []  # List of point IDs

class HistoricalData(BaseModel):
    """Model for historical data of a control point"""
    point_id: str
    timestamps: List[datetime]
    values: List[float]

class ControlAction(BaseModel):
    """Model for an action on a control point"""
    point_id: str
    value: float
    user: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class SystemSettings(BaseModel):
    """Model for system-wide settings"""
    refresh_rate: int = 5  # in seconds
    alarm_notification: bool = True
    data_retention_days: int = 30
    theme: str = "light"