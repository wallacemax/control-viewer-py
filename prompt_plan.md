### **Step-by-Step Blueprint for Building the Control Chart System with FastAPI and NiceGUI**

This blueprint adapts the project to use **FastAPI** for the backend and **NiceGUI** for the frontend, following an iterative, incremental approach. Each step is small, testable, and builds on the previous one. The goal is to ensure a smooth development process with strong testing and no orphaned or hanging code.

---

### **Phase 1: Backend Development**

#### **Step 1: Set Up Backend Environment**
- Initialize the backend framework using **FastAPI**.
- Install required dependencies:
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

#### **Step 2: Database Schema Design**
- Create the database schema for `measurements` and `scales` tables using **SQLAlchemy**.
- Define relationships and constraints (e.g., foreign keys, data types).
- Write migrations using a tool like **Alembic**.

#### **Step 3: Create API Endpoints**
1. **GET /measurements**:
   - Fetch measurements based on filters (date range, scale ID, workstation ID, technician ID).
   - Validate query parameters using Pydantic.
   - Return paginated results.
2. **POST /recalculate**:
   - Calculate mean and sigma for a given date range and scale.
   - Validate input and handle edge cases (e.g., no data found).
3. **POST /save-baseline**:
   - Save the recalculated mean and sigma as the new baseline for a scale.

#### **Step 4: Unit Test Backend Endpoints**
- Write unit tests for each endpoint using **Pytest**.
- Test edge cases (e.g., invalid inputs, empty datasets).

---

### **Phase 2: Frontend Development**

#### **Step 5: Set Up Frontend Environment**
- Initialize the frontend framework using **NiceGUI**.
- Install required dependencies:
  ```bash
  pip install nicegui matplotlib plotly
  ```
- Set up the project structure:
  ```
  frontend/
  ├── main.py
  ├── components/
  │   ├── filter_form.py
  │   ├── control_chart.py
  ├── services/
  │   ├── api_client.py
  ├── pages/
  │   ├── home.py
  └── requirements.txt
  ```

#### **Step 6: Build UI Components**
1. **Filter Form**:
   - Create a form with:
     - Date range picker.
     - Dropdowns for scale, workstation, and technician.
   - Validate user inputs (e.g., ensure valid date ranges).
2. **Control Chart Component**:
   - Use NiceGUI's charting tools or **Matplotlib**/**Plotly** to render the control chart.
   - Accept data and control limits (CL, UCL, LCL) as inputs.

#### **Step 7: Integrate Backend with Frontend**
- Use **NiceGUI**'s built-in HTTP client or **requests** to connect the frontend to the backend.
- Populate the filter dropdowns with data from the backend.
- Fetch and display measurements on the control chart based on user inputs.

#### **Step 8: Test Frontend Components**
- Write unit tests for UI components using Python testing frameworks like **pytest**.
- Test API integration and error handling.

---

### **Phase 3: Iterative Refinement**

#### **Step 9: Implement Outlier Highlighting**
- Add logic to highlight outliers (points outside UCL and LCL) on the control chart.
- Test the highlighting functionality with sample datasets.

#### **Step 10: Add Save Baseline Feature**
- Add a button to save the recalculated mean and sigma as the new baseline.
- Test the save functionality end-to-end.

#### **Step 11: Optimize Performance**
- Optimize database queries for large datasets (e.g., add indexes).
- Use lazy loading or pagination for large datasets on the frontend.

#### **Step 12: Final Testing and Deployment**
- Conduct integration testing to ensure the system works end-to-end.
- Deploy the system to a production environment using tools like **Docker** or **Heroku**.

---

### **Breaking Down the Blueprint into Smaller Steps**

Each phase is now broken into smaller, right-sized steps that can be implemented and tested incrementally.

---

## **Prompts for Code-Generation LLM**

Below are the prompts for each step. Each prompt builds on the previous one, ensuring no orphaned or hanging code.

---

### **Prompt 1: Backend Initialization**
```text
Create a FastAPI project with the following structure:
- Install dependencies: fastapi, uvicorn, sqlalchemy, psycopg2-binary, and pydantic.
- Set up a modular structure with directories for models, schemas, routers, and database configuration.
- Write a simple `main.py` file that initializes the app and includes a health check endpoint (`GET /health`) that returns a JSON response: `{ "status": "ok" }`.

Write tests for the health check endpoint using Pytest.
```

---

### **Prompt 2: Database Schema**
```text
Using SQLAlchemy, define the database schema for the following tables:

1. `measurements`:
   - `id` (Primary Key, INT)
   - `scale_id` (Foreign Key, INT)
   - `workstation_id` (INT)
   - `technician_id` (INT)
   - `measurement_value` (FLOAT)
   - `measurement_date` (TIMESTAMP)

2. `scales`:
   - `id` (Primary Key, INT)
   - `name` (VARCHAR(255))
   - `baseline_mean` (FLOAT)
   - `baseline_sigma` (FLOAT)

Write migration scripts using Alembic to create these tables in a PostgreSQL database. Test the migrations by running them against a local database.
```

---

### **Prompt 3: GET /measurements Endpoint**
```text
Create a `GET /measurements` endpoint in FastAPI. This endpoint should:
1. Accept query parameters for `start_date`, `end_date`, `scale_id`, `workstation_id`, and `technician_id`.
2. Query the `measurements` table based on these filters using SQLAlchemy.
3. Return a JSON array of matching records.

Write unit tests for this endpoint using Pytest. Include tests for:
- Valid queries.
- Missing required parameters.
- No matching records.
```

---

### **Prompt 4: POST /recalculate Endpoint**
```text
Create a `POST /recalculate` endpoint in FastAPI. This endpoint should:
1. Accept a JSON body with `start_date`, `end_date`, and `scale_id`.
2. Query the `measurements` table for the specified date range and scale.
3. Calculate the mean and standard deviation (sigma) of the `measurement_value` column.
4. Return the calculated values as a JSON response.

Write unit tests for this endpoint using Pytest. Include tests for:
- Valid inputs.
- No matching records.
- Invalid inputs.
```

---

### **Prompt 5: Frontend Initialization**
```text
Create a NiceGUI project. Set up the project structure with folders for `components`, `services`, and `pages`. Install the following dependencies:
- NiceGUI (for UI)
- Matplotlib/Plotly (for chart rendering)
- Requests (for API calls)

Create a basic homepage (`/`) with a header that says "Control Chart System". Test the homepage rendering using pytest.
```

---

### **Prompt 6: Filter Form Component**
```text
Create a `FilterForm` component in NiceGUI. This component should:
1. Include a date range picker.
2. Include dropdowns for Scale ID, Workstation ID, and Technician ID.
3. Validate user inputs (e.g., ensure date range is valid).

Write tests for the `FilterForm` component using pytest. Include tests for:
- Rendering all form fields.
- Validating user inputs.
```

---

### **Prompt 7: Control Chart Component**
```text
Create a `ControlChart` component in NiceGUI. This component should:
1. Use NiceGUI's charting tools or Matplotlib/Plotly to render a line chart.
2. Accept inputs for data points, mean, UCL, and LCL.
3. Highlight outliers (points outside UCL and LCL).

Write tests for the `ControlChart` component using pytest. Include tests for:
- Rendering the chart with valid data.
- Highlighting outliers correctly.
```

---

### **Prompt 8: Integration**
```text
Integrate the `FilterForm` and `ControlChart` components. When the user submits the form, fetch data from the `GET /measurements` endpoint and pass it to the `ControlChart` component.

Write integration tests to ensure the form and chart work together correctly.
```

---

### **Prompt 9: Save Baseline Feature**
```text
Add a "Save Baseline" button to the frontend. When clicked, send a request to the `POST /save-baseline` endpoint with the recalculated mean and sigma. Display a success or error message based on the response.

Write tests for this feature, including:
- Successful save.
- Backend error handling.
```

---

This plan ensures incremental progress, strong testing, and smooth integration between the backend and NiceGUI frontend.