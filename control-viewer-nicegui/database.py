"""
Database module for the Control Viewer application
"""
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from models import ControlPoint, ControlGroup, HistoricalData, SystemSettings

class MemoryDatabase:
    """Simple in-memory database implementation"""
    
    def __init__(self):
        """Initialize the in-memory database"""
        self.control_points: Dict[str, ControlPoint] = {}
        self.control_groups: Dict[str, ControlGroup] = {}
        self.historical_data: Dict[str, List[Dict[str, Any]]] = {}
        self.system_settings = SystemSettings()
        
        # Load initial data if available
        self.load_data()
    
    def load_data(self) -> None:
        """Load data from JSON files if they exist"""
        try:
            if os.path.exists("data/control_points.json"):
                with open("data/control_points.json", "r") as f:
                    data = json.load(f)
                    for item in data:
                        # Convert string timestamp to datetime if it exists
                        if "timestamp" in item and item["timestamp"]:
                            item["timestamp"] = datetime.fromisoformat(item["timestamp"])
                        self.control_points[item["id"]] = ControlPoint(**item)
            
            if os.path.exists("data/control_groups.json"):
                with open("data/control_groups.json", "r") as f:
                    data = json.load(f)
                    for item in data:
                        self.control_groups[item["id"]] = ControlGroup(**item)
            
            if os.path.exists("data/settings.json"):
                with open("data/settings.json", "r") as f:
                    self.system_settings = SystemSettings(**json.load(f))
                    
        except Exception as e:
            print(f"Error loading data: {e}")
    
    async def save_data(self) -> None:
        """Save data to JSON files"""
        try:
            os.makedirs("data", exist_ok=True)
            
            with open("data/control_points.json", "w") as f:
                # Convert datetime objects to ISO format strings
                data = []
                for point in self.control_points.values():
                    point_dict = point.dict()
                    if point_dict["timestamp"] and isinstance(point_dict["timestamp"], datetime):
                        point_dict["timestamp"] = point_dict["timestamp"].isoformat()
                    data.append(point_dict)
                json.dump(data, f, indent=2)
            
            with open("data/control_groups.json", "w") as f:
                json.dump([group.dict() for group in self.control_groups.values()], f, indent=2)
            
            with open("data/settings.json", "w") as f:
                json.dump(self.system_settings.dict(), f, indent=2)
                
        except Exception as e:
            print(f"Error saving data: {e}")
    
    # Control point methods
    async def get_control_point(self, point_id: str) -> Optional[ControlPoint]:
        """Get a control point by ID"""
        return self.control_points.get(point_id)
    
    async def get_all_control_points(self) -> List[ControlPoint]:
        """Get all control points"""
        return list(self.control_points.values())
    
    async def create_control_point(self, point: ControlPoint) -> ControlPoint:
        """Create a new control point"""
        self.control_points[point.id] = point
        await self.save_data()
        return point
    
    async def update_control_point(self, point_id: str, point: ControlPoint) -> Optional[ControlPoint]:
        """Update an existing control point"""
        if point_id not in self.control_points:
            return None
        
        self.control_points[point_id] = point
        
        # Add to historical data
        if point.value is not None:
            if point_id not in self.historical_data:
                self.historical_data[point_id] = []
            
            self.historical_data[point_id].append({
                "timestamp": point.timestamp or datetime.now(),
                "value": point.value
            })
            
            # Limit historical data size
            max_records = self.system_settings.data_retention_days * 24 * 12  # 5-minute intervals
            if len(self.historical_data[point_id]) > max_records:
                self.historical_data[point_id] = self.historical_data[point_id][-max_records:]
        
        await self.save_data()
        return point
    
    async def delete_control_point(self, point_id: str) -> bool:
        """Delete a control point"""
        if point_id not in self.control_points:
            return False
        
        del self.control_points[point_id]
        
        # Also remove from groups
        for group in self.control_groups.values():
            if point_id in group.points:
                group.points.remove(point_id)
        
        await self.save_data()
        return True
    
    # Control group methods
    async def get_control_group(self, group_id: str) -> Optional[ControlGroup]:
        """Get a control group by ID"""
        return self.control_groups.get(group_id)
    
    async def get_all_control_groups(self) -> List[ControlGroup]:
        """Get all control groups"""
        return list(self.control_groups.values())
    
    async def create_control_group(self, group: ControlGroup) -> ControlGroup:
        """Create a new control group"""
        self.control_groups[group.id] = group
        await self.save_data()
        return group
    
    async def update_control_group(self, group_id: str, group: ControlGroup) -> Optional[ControlGroup]:
        """Update an existing control group"""
        if group_id not in self.control_groups:
            return None
        
        self.control_groups[group_id] = group
        await self.save_data()
        return group
    
    async def delete_control_group(self, group_id: str) -> bool:
        """Delete a control group"""
        if group_id not in self.control_groups:
            return False
        
        del self.control_groups[group_id]
        await self.save_data()
        return True
    
    # Historical data methods
    async def get_historical_data(self, point_id: str, start_time: Optional[datetime] = None, 
                                 end_time: Optional[datetime] = None) -> HistoricalData:
        """Get historical data for a control point"""
        if point_id not in self.historical_data:
            return HistoricalData(point_id=point_id, timestamps=[], values=[])
        
        data = self.historical_data[point_id]
        
        # Filter by time range if specified
        if start_time or end_time:
            filtered_data = []
            for record in data:
                record_time = record["timestamp"]
                if start_time and record_time < start_time:
                    continue
                if end_time and record_time > end_time:
                    continue
                filtered_data.append(record)
            data = filtered_data
        
        # Sort by timestamp
        data.sort(key=lambda x: x["timestamp"])
        
        return HistoricalData(
            point_id=point_id,
            timestamps=[record["timestamp"] for record in data],
            values=[record["value"] for record in data]
        )
    
    # System settings methods
    async def get_system_settings(self) -> SystemSettings:
        """Get system settings"""
        return self.system_settings
    
    async def update_system_settings(self, settings: SystemSettings) -> SystemSettings:
        """Update system settings"""
        self.system_settings = settings
        await self.save_data()
        return self.system_settings

# Create a singleton instance
database = MemoryDatabase()

# Background task to periodically save data
async def periodic_save():
    """Save data periodically to ensure persistence"""
    try:
        while True:
            await asyncio.sleep(60)  # Save every minute
            await database.save_data()
    except asyncio.CancelledError:
        # Handle task cancellation gracefully
        pass
    except Exception as e:
        print(f"Error in periodic save task: {e}")

# Function to start the background task
async def start_background_tasks():
    """Start background tasks"""
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_save())
    
    await asyncio.sleep(0)

    return #cheep return awaitable