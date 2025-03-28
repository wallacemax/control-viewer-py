"""
API router for the Control Viewer application
"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime
from models import ControlPoint, ControlGroup, HistoricalData, SystemSettings
from database import database
from utils import serialize_to_json, generate_simulated_value, calculate_status

router = APIRouter(prefix="/api")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting message: {e}")

manager = ConnectionManager()

# Control Points API
@router.get("/control-points", response_model=List[ControlPoint])
async def get_control_points():
    """Get all control points"""
    return await database.get_all_control_points()

@router.get("/control-points/{point_id}", response_model=ControlPoint)
async def get_control_point(point_id: str):
    """Get a specific control point by ID"""
    point = await database.get_control_point(point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Control point not found")
    return point

@router.post("/control-points", response_model=ControlPoint)
async def create_control_point(point: ControlPoint):
    """Create a new control point"""
    # Set timestamp if not provided
    if not point.timestamp:
        point.timestamp = datetime.now()
    
    # Calculate status if not provided
    if point.status == "unknown" and point.value is not None:
        point.status = calculate_status(point)
    
    created_point = await database.create_control_point(point)
    
    # Broadcast the new point to all connected clients
    await manager.broadcast(serialize_to_json({
        "action": "create", 
        "data": created_point.dict()
    }))
    
    return created_point

@router.put("/control-points/{point_id}", response_model=ControlPoint)
async def update_control_point(point_id: str, point: ControlPoint):
    """Update an existing control point"""
    existing_point = await database.get_control_point(point_id)
    if not existing_point:
        raise HTTPException(status_code=404, detail="Control point not found")
    
    # Set timestamp to now
    point.timestamp = datetime.now()
    
    # Calculate status based on value
    if point.value is not None:
        point.status = calculate_status(point)
    
    updated_point = await database.update_control_point(point_id, point)
    
    # Broadcast the updated point to all connected clients
    await manager.broadcast(serialize_to_json({
        "action": "update", 
        "data": updated_point.dict()
    }))
    
    return updated_point

@router.delete("/control-points/{point_id}")
async def delete_control_point(point_id: str):
    """Delete a control point"""
    success = await database.delete_control_point(point_id)
    if not success:
        raise HTTPException(status_code=404, detail="Control point not found")
    
    # Broadcast the deletion to all connected clients
    await manager.broadcast(serialize_to_json({
        "action": "delete", 
        "data": {"id": point_id}
    }))
    
    return {"status": "success", "message": f"Control point {point_id} deleted"}

# Control Groups API
@router.get("/control-groups", response_model=List[ControlGroup])
async def get_control_groups():
    """Get all control groups"""
    return await database.get_all_control_groups()

@router.get("/control-groups/{group_id}", response_model=ControlGroup)
async def get_control_group(group_id: str):
    """Get a specific control group by ID"""
    group = await database.get_control_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Control group not found")
    return group

@router.post("/control-groups", response_model=ControlGroup)
async def create_control_group(group: ControlGroup):
    """Create a new control group"""
    created_group = await database.create_control_group(group)
    return created_group

@router.put("/control-groups/{group_id}", response_model=ControlGroup)
async def update_control_group(group_id: str, group: ControlGroup):
    """Update an existing control group"""
    updated_group = await database.update_control_group(group_id, group)
    if not updated_group:
        raise HTTPException(status_code=404, detail="Control group not found")
    return updated_group

@router.delete("/control-groups/{group_id}")
async def delete_control_group(group_id: str):
    """Delete a control group"""
    success = await database.delete_control_group(group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Control group not found")
    return {"status": "success", "message": f"Control group {group_id} deleted"}

# Historical Data API
@router.get("/historical-data/{point_id}", response_model=HistoricalData)
async def get_historical_data(
    point_id: str, 
    start_time: Optional[datetime] = None, 
    end_time: Optional[datetime] = None
):
    """Get historical data for a control point"""
    point = await database.get_control_point(point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Control point not found")
    
    history = await database.get_historical_data(point_id, start_time, end_time)
    return history

# System Settings API
@router.get("/settings", response_model=SystemSettings)
async def get_settings():
    """Get system settings"""
    return await database.get_system_settings()

@router.put("/settings", response_model=SystemSettings)
async def update_settings(settings: SystemSettings):
    """Update system settings"""
    updated_settings = await database.update_system_settings(settings)
    return updated_settings

# WebSocket endpoint for real-time updates
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                if message["action"] == "update_value":
                    point_id = message["id"]
                    new_value = message["value"]
                    
                    point = await database.get_control_point(point_id)
                    if point:
                        point.value = new_value
                        point.timestamp = datetime.now()
                        point.status = calculate_status(point)
                        
                        await database.update_control_point(point_id, point)
                        
                        # Broadcast the update to all connected clients
                        await manager.broadcast(serialize_to_json({
                            "action": "update",
                            "data": point.dict()
                        }))
            except Exception as e:
                print(f"Error processing WebSocket message: {e}")
                await websocket.send_text(json.dumps({
                    "error": str(e)
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Simulation endpoint for demo purposes
@router.post("/simulate")
async def simulate_data():
    """Simulate random changes to control point values for demo purposes"""
    points = await database.get_all_control_points()
    
    for point in points:
        if point.type == "sensor":  # Only simulate sensor values
            point.value = generate_simulated_value(point)
            point.timestamp = datetime.now()
            point.status = calculate_status(point)
            
            await database.update_control_point(point.id, point)
    
    # Broadcast updates to all connected clients
    await manager.broadcast(serialize_to_json({
        "action": "simulate",
        "timestamp": datetime.now().isoformat()
    }))
    
    return {"status": "success", "message": "Simulation completed"}

# Background simulation task
async def simulation_task():
    """Background task to periodically simulate data changes"""
    while True:
        try:
            settings = await database.get_system_settings()
            # Simulate data periodically based on refresh rate setting
            await simulate_data()
            await asyncio.sleep(settings.refresh_rate)
        except Exception as e:
            print(f"Error in simulation task: {e}")
            await asyncio.sleep(5)  # Fallback sleep on error

# Function to start the background task
def start_simulation():
    """Start the simulation background task"""
    asyncio.create_task(simulation_task())