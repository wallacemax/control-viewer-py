### Adjusting the Specification for FastAPI and NiceGUI

The following steps adapt the **Control Chart System Specification** to use **FastAPI** for the backend and **NiceGUI** for the frontend. Dependencies and architecture are adjusted to align with Python's ecosystem, leveraging FastAPI's strengths for backend development and NiceGUI's simplicity for building the user interface. The adjusted plan will follow the same structure but use Python tools and best practices.

---

## **Blueprint for Building the Project**

### **Step 1: Define the Project Scope**
- Build a **Control Chart System** using **FastAPI** for the backend.
- Use **NiceGUI** for the frontend.
- Use **PostgreSQL** as the database.
- Use **Pydantic** for data validation and serialization.
- Use **SQLAlchemy** for database interaction.
- Use **Matplotlib** or **Plotly** for chart rendering.
- Use **Uvicorn** as the ASGI server.

---

### **Step 2: High-Level Plan**

#### **Backend (FastAPI)**
1. Set up the FastAPI project with a modular structure.
2. Define database models using SQLAlchemy.
3. Create API endpoints for:
   - Fetching measurements.
   - Recalculating mean and sigma.
   - Saving new baselines.
4. Implement data validation and error handling using Pydantic.
5. Add authentication and authorization (optional for now).
6. Write unit and integration tests for all endpoints.

#### **Frontend (NiceGUI)**
1. Set up the NiceGUI project.
2. Build UI components:
   - Filters (date range picker, dropdowns for Scale ID, Workstation ID, Technician ID).
   - Control chart visualization using NiceGUI's built-in charting tools or Matplotlib/Plotly.
3. Integrate the frontend with the FastAPI backend.
4. Add client-side validation and error handling.

#### **Database (PostgreSQL)**
1. Design and create the database schema.
2. Populate the database with sample data for testing.
3. Optimize queries for performance.

#### **Testing**
1. Write unit tests for backend endpoints.
2. Write integration tests for end-to-end functionality.
3. Test the frontend UI for usability and responsiveness.
4. Perform load testing to ensure scalability.

---

### **Step 3: Break Down into Iterative Chunks**

#### **Backend**
1. Set up the FastAPI project and install dependencies.
2. Create the database schema and connect it to the FastAPI app.
3. Implement the `GET /measurements` endpoint.
4. Implement the `POST /recalculate` endpoint.
5. Implement the `POST /save-baseline` endpoint.
6. Add authentication and authorization (optional).
7. Write unit tests for all endpoints.

#### **Frontend**
1. Set up the NiceGUI project.
2. Build the filter components.
3. Build the control chart component.
4. Integrate the frontend with the backend.
5. Add client-side validation and error handling.

#### **Testing**
1. Write backend unit tests.
2. Write frontend unit tests.
3. Perform integration testing.
4. Perform performance testing.

---

### **Step 4: Break Down into Smaller Steps**

#### **Backend Steps**

##### **Step 1: Set Up FastAPI Project**
- Create a new FastAPI project directory.
- Install necessary dependencies:
  ```bash
  pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic
  ```
- Set up the project structure:
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

##### **Step 2: Create Database Schema**
- Define database models in `models.py` using SQLAlchemy.
- Example:
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

- Set up the database connection in `database.py`:
  ```python
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker

  SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

  engine = create_engine(SQLALCHEMY_DATABASE_URL)
  SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  ```

##### **Step 3: Implement `GET /measurements` Endpoint**
- Create a router in `routers/measurements.py`:
  ```python
  from fastapi import APIRouter, Depends
  from sqlalchemy.orm import Session
  from app.database import SessionLocal
  from app.models import Measurement

  router = APIRouter()

  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()

  @router.get("/measurements")
  def get_measurements(scale_id: int, start_date: str, end_date: str, db: Session = Depends(get_db)):
      measurements = db.query(Measurement).filter(
          Measurement.scale_id == scale_id,
          Measurement.measurement_date >= start_date,
          Measurement.measurement_date <= end_date
      ).all()
      return measurements
  ```

##### **Step 4: Implement `POST /recalculate` Endpoint**
- Add a router in `routers/recalculation.py`:
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
          return {"error": "No data found for the selected range"}
      mean = statistics.mean(values)
      sigma = statistics.stdev(values)
      return {"mean": mean, "sigma": sigma}
  ```

##### **Step 5: Implement `POST /save-baseline` Endpoint**
- Add a router in `routers/baselines.py`:
  ```python
  from fastapi import APIRouter, Depends
  from sqlalchemy.orm import Session
  from app.database import SessionLocal
  from app.models import Scale

  router = APIRouter()

  @router.post("/save-baseline")
  def save_baseline(scale_id: int, new_mean: float, new_sigma: float, db: Session = Depends(get_db)):
      scale = db.query(Scale).filter(Scale.id == scale_id).first()
      if not scale:
          return {"error": "Scale not found"}
      scale.baseline_mean = new_mean
      scale.baseline_sigma = new_sigma
      db.commit()
      return {"message": "Baseline updated successfully"}
  ```

---

#### **Frontend Steps**

##### **Step 1: Set Up NiceGUI Project**
- Install NiceGUI:
  ```bash
  pip install nicegui
  ```
- Create a `main.py` file:
  ```python
  from nicegui import ui

  def main_page():
      ui.label('Control Chart System')

  ui.page('/')(main_page)

  ui.run()
  ```

##### **Step 2: Build Filter Form**
- Create a filter form using NiceGUI's components:
  ```python
  from nicegui import ui

  def filter_form():
      with ui.form():
          ui.date('Start Date')
          ui.date('End Date')
          ui.select(['Scale 1', 'Scale 2'], label='Scale')
          ui.button('Submit', on_click=lambda: print('Filter submitted'))
  ```

##### **Step 3: Build Control Chart**
- Use NiceGUI's `ui.chart` or integrate with Matplotlib/Plotly for charting:
  ```python
  from nicegui import ui

  def control_chart(data):
      ui.chart({
          'type': 'line',
          'data': {
              'labels': data['labels'],
              'datasets': [{
                  'label': 'Measurements',
                  'data': data['values'],
              }]
          }
      })
  ```

---

This plan ensures a smooth integration between FastAPI and NiceGUI, providing a Python-based solution for both backend and frontend development. 