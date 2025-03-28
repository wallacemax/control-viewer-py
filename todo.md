### **Extremely Detailed To-Do List for Implementing the Control Chart System**

This to-do list breaks down the project into detailed, actionable steps based on the specification. Each task is small, focused, and includes specific instructions to ensure smooth implementation.

---

## **1. Backend Development (FastAPI)**

### **1.1 Set Up the FastAPI Project**
1. Create a new project directory: `mkdir control-chart-system && cd control-chart-system`.
2. Create a `backend/` folder for the backend code.
3. Create a Python virtual environment: `python -m venv venv`.
4. Activate the virtual environment:
   - On Linux/Mac: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate`
5. Install dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic
   ```
6. Create the following project structure:
   ```
   backend/
   ├── app/
   │   ├── main.py
   │   ├── models.py
   │   ├── schemas.py
   │   ├── crud.py
   │   ├── database.py
   │   ├── routers/
   │   │   ├── measurements.py
   │   │   ├── recalculation.py
   │   │   └── baselines.py
   │   └── tests/
   └── requirements.txt
   ```
7. Add dependencies to `requirements.txt`:
   ```
   fastapi
   uvicorn
   sqlalchemy
   psycopg2-binary
   pydantic
   ```

---

### **1.2 Configure the Database**
1. Create a PostgreSQL database (e.g., using pgAdmin or the command line).
   - Example:
     ```sql
     CREATE DATABASE control_chart_db;
     ```
2. In `app/database.py`, configure the database connection:
   ```python
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker

   SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/control_chart_db"

   engine = create_engine(SQLALCHEMY_DATABASE_URL)
   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   ```
3. Test the database connection by creating a simple script to connect and print the engine:
   ```python
   from app.database import engine

   print(engine)
   ```

---

### **1.3 Define Database Models**
1. In `app/models.py`, define the `Measurement` and `Scale` models:
   ```python
   from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
   from sqlalchemy.ext.declarative import declarative_base

   Base = declarative_base()

   class Measurement(Base):
       __tablename__ = "measurements"
       id = Column(Integer, primary_key=True, index=True)
       scale_id = Column(Integer, index=True)
       workstation_id = Column(Integer, index=True)
       technician_id = Column(Integer, index=True)
       measurement_value = Column(Float, nullable=False)
       measurement_date = Column(DateTime, nullable=False)

   class Scale(Base):
       __tablename__ = "scales"
       id = Column(Integer, primary_key=True, index=True)
       name = Column(String, nullable=False)
       baseline_mean = Column(Float, nullable=True)
       baseline_sigma = Column(Float, nullable=True)
   ```
2. Create database tables using SQLAlchemy:
   ```python
   from app.database import engine
   from app.models import Base

   Base.metadata.create_all(bind=engine)
   ```

---

### **1.4 Create CRUD Operations**
1. In `app/crud.py`, create functions for interacting with the database:
   ```python
   from sqlalchemy.orm import Session
   from app.models import Measurement, Scale

   def get_measurements(db: Session, scale_id: int, start_date: str, end_date: str):
       return db.query(Measurement).filter(
           Measurement.scale_id == scale_id,
           Measurement.measurement_date >= start_date,
           Measurement.measurement_date <= end_date
       ).all()

   def save_baseline(db: Session, scale_id: int, mean: float, sigma: float):
       scale = db.query(Scale).filter(Scale.id == scale_id).first()
       if scale:
           scale.baseline_mean = mean
           scale.baseline_sigma = sigma
           db.commit()
           return scale
       return None
   ```

---

### **1.5 Implement API Endpoints**
1. **Health Check Endpoint**
   - In `app/main.py`, add a health check endpoint:
     ```python
     from fastapi import FastAPI

     app = FastAPI()

     @app.get("/health")
     def health_check():
         return {"status": "ok"}
     ```

2. **GET `/measurements` Endpoint**
   - In `app/routers/measurements.py`:
     ```python
     from fastapi import APIRouter, Depends
     from sqlalchemy.orm import Session
     from app.database import SessionLocal
     from app.crud import get_measurements

     router = APIRouter()

     def get_db():
         db = SessionLocal()
         try:
             yield db
         finally:
             db.close()

     @router.get("/measurements")
     def get_measurements_endpoint(scale_id: int, start_date: str, end_date: str, db: Session = Depends(get_db)):
         return get_measurements(db, scale_id, start_date, end_date)
     ```

3. **POST `/recalculate` Endpoint**
   - In `app/routers/recalculation.py`:
     ```python
     from fastapi import APIRouter, Depends
     from sqlalchemy.orm import Session
     from app.database import SessionLocal
     from app.models import Measurement
     import statistics

     router = APIRouter()

     @router.post("/recalculate")
     def recalculate_mean_sigma(scale_id: int, start_date: str, end_date: str, db: Session = Depends(get_db)):
         measurements = db.query(Measurement).filter(
             Measurement.scale_id == scale_id,
             Measurement.measurement_date >= start_date,
             Measurement.measurement_date <= end_date
         ).all()
         values = [m.measurement_value for m in measurements]
         if not values:
             return {"error": "No data found"}
         mean = statistics.mean(values)
         sigma = statistics.stdev(values)
         return {"mean": mean, "sigma": sigma}
     ```

4. **POST `/save-baseline` Endpoint**
   - In `app/routers/baselines.py`:
     ```python
     from fastapi import APIRouter, Depends
     from sqlalchemy.orm import Session
     from app.crud import save_baseline

     router = APIRouter()

     @router.post("/save-baseline")
     def save_baseline_endpoint(scale_id: int, mean: float, sigma: float, db: Session = Depends(get_db)):
         result = save_baseline(db, scale_id, mean, sigma)
         if result:
             return {"message": "Baseline updated successfully"}
         return {"error": "Scale not found"}
     ```

---

### **1.6 Write Unit Tests**
1. Set up `pytest` for testing:
   ```bash
   pip install pytest pytest-asyncio
   ```
2. Create test cases for each endpoint in `app/tests/`.

---

## **2. Frontend Development (NiceGUI)**

### **2.1 Set Up NiceGUI**
1. Install NiceGUI:
   ```bash
   pip install nicegui
   ```
2. Create a `frontend/` folder and a `main.py` file.

---

### **2.2 Build UI Components**
1. **Filter Form**
   - Create a filter form with date pickers and dropdowns.

2. **Control Chart**
   - Use NiceGUI's `ui.chart` or integrate with Matplotlib/Plotly.

---

### **2.3 Integrate with Backend**
1. Use NiceGUI's `ui.button` to trigger API calls.
2. Display chart data dynamically.

---

### **2.4 Test the Frontend**
1. Write Python-based tests for NiceGUI components.

---

## **3. Testing and Deployment**

1. **Backend Testing**
   - Test all endpoints with valid and invalid inputs.

2. **Frontend Testing**
   - Test UI responsiveness and integration with the backend.

3. **Deploy**
   - Use Docker to containerize the application.
   - Deploy to a cloud provider (e.g., AWS, Azure, or Heroku).

---
