"""
Control Viewer - NiceGUI and FastAPI Implementation
Main application entry point
"""

import logging
import os
import asyncio
from contextlib import asynccontextmanager

# Set up logging first
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import FastAPI components
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from nicegui import ui, app as nicegui_app


# Import application components
from config import settings
from database import database, start_background_tasks
from api import router as api_router, start_simulation

@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for FastAPI app startup and shutdown"""
    logger.info("Starting application...")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    logger.info("Data directory checked/created")
    
    try:
        # Get current event loop or create a new one if needed
        try:
            loop = asyncio.get_running_loop()
            logger.debug("Using existing event loop")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.debug("Created new event loop")
        
        # Start background tasks
        await start_background_tasks()
        logger.info("Background tasks started")
        
        # Start simulation for demo purposes
        if settings.DEBUG:
            start_simulation()
            logger.info("Debug mode: Simulation started")
        
        yield
        
        # Shutdown logic can go here
        logger.info("Application shutting down")
        
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        # We still need to yield to allow FastAPI to continue
        yield

# Create FastAPI app with lifespan
fast_app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan
)

# Add CORS middleware
fast_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
fast_app.include_router(api_router)

# Add a simple health check endpoint
@fast_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}

# Setup main UI page
@ui.page('/')
def index():
    """Main application page"""
    logger.info("Rendering main application page")
    try:
        from ui import setup_layout
        setup_layout()
    except Exception as e:
        logger.critical(f"Error initializing UI: {e}", exc_info=True)
        with ui.card().classes('bg-red-100 p-4'):
            ui.label("Err loading application UI").classes('text-h6 text-red-600')
            ui.label(str(e)).classes('text-red-500')

# Create additional routes if needed
@ui.page('/about')
def about():
    """About page"""
    with ui.card().classes('w-full max-w-3xl mx-auto'):
        ui.label(f"{settings.APP_NAME} {settings.APP_VERSION}").classes('text-h4')
        ui.label(settings.APP_DESCRIPTION)

@ui.page('/test')
def test_page():
    """Test page"""
    with ui.card():
        ui.label("Test Page").classes('text-h4')
        ui.label("If this is here, good news.")

# Mount FastAPI to NiceGUI
nicegui_app.mount("/api", fast_app)

# Run the application
if __name__ in {"__main__", "__mp_main__"}:
    logger.info("=" * 50)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Host: {settings.HOST}, Port: {settings.PORT}, Debug: {settings.DEBUG}")
    logger.info(f"Application will be available at: http://{settings.HOST}:{settings.PORT}/")
    logger.info(f"API endpoints will be available at: http://{settings.HOST}:{settings.PORT}/api/")
    logger.info("=" * 50)
    
    try:
        logger.info(f"Current event loop: {asyncio.get_event_loop()}")

        ui.run(
            host=settings.HOST,
            port=settings.PORT,
            title=settings.APP_NAME,
            dark=False,
            reload=settings.INFO,
            storage_secret="control-viewer-secret",
            show=True
        )
    except Exception as e:
        logger.critical(f"Failed to start application: {e}", exc_info=True)