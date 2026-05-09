# Directory tree of the project
📁 hackaton/
├── 📁 cycle_sync_app
│   ├── 📁 controllers
│   │   ├── 📁 db_control
│   │   │   ├── 📁 driver_controllers
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 garage_controller.py
│   │   │   │   ├── 📄 powertrain_hub_controller.py
│   │   │   │   └── 📄 tire_controller.py
│   │   │   ├── 📁 oem_controllers
│   │   │   │   ├── 📄 fleet_controller.py
│   │   │   │   └── 📄 oem_blueprint_controller.py
│   │   │   ├── 📁 recycler_controllers
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 analytics_controller.py
│   │   │   │   └── 📄 exchange_controller.py
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 auth_controller.py
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main_controller.py
│   │   ├── 📄 README_controllers.md
│   │   └── 📄 wizard_controller.py
│   ├── 📁 data_ingestion_engine
│   │   ├── 📄 __init__.py
│   │   ├── 📄 ingestion_service.py
│   │   ├── 📄 market_scraper.py
│   │   └── 📄 README_data_ingestion.md
│   ├── 📁 mcp_agent_server
│   │   ├── 📁 prompts
│   │   │   ├── 📄 oem_battery_prompt.py
│   │   │   └── 📄 recycler_market_prompt.py
│   │   ├── 📄 __init__.py
│   │   ├── 📄 agent_tools.py
│   │   ├── 📄 ai_orchestrator.py
│   │   ├── 📄 core_llm_client.py
│   │   └── 📄 README_mcp_agent.md
│   ├── 📁 models
│   │   ├── 📁 data_manager
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 company_registry_manager.py
│   │   │   ├── 📄 database_manager.py
│   │   │   ├── 📄 market_cache_manager.py
│   │   │   └── 📄 tire_manager.py
│   │   ├── 📁 driver_models
│   │   │   ├── 📁 powertrain_models
│   │   │   │   └── 📄 bev_model.py
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 tire_model.py
│   │   │   └── 📄 vehicle_model.py
│   │   ├── 📁 oem_models
│   │   │   ├── 📄 fleet_model.py
│   │   │   └── 📄 oem_model.py
│   │   ├── 📁 recycler_models
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 macro_market_model.py
│   │   ├── 📁 telemetry_simulation
│   │   │   └── 📄 trip_simulator.py
│   │   ├── 📄 auth_model.py
│   │   ├── 📄 veritwin.db
│   │   └── 📄 README_models.md
│   ├── 📁 storage
│   │   ├── 📁 car_photos
│   │   │   ├── 📄 maserati_grecale_folgore.jpg
│   │   │   ├── 📄 maserati_mc20_cielo.jpg
│   │   │   └── 📄 maserati_quattroporte.jpg
│   │   ├── 📁 logos
│   │   │   ├── 📄 ferrari_logo.jpg
│   │   │   ├── 📄 lambo_logo.jpg
│   │   │   └── 📄 varano.png
│   │   └── 📄 ecosystem_map.html
│   ├── 📁 views
│   │   ├── 📁 Driver_widgets
│   │   │   ├── 📁 powertrain_widgets
│   │   │   │   ├── 📄 bev_widget.py
│   │   │   │   └── 📄 powertrain_hub_widget.py
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 garage_widget.py
│   │   │   ├── 📄 tire_change_dialog.py
│   │   │   └── 📄 tire_tracker_widget.py
│   │   ├── 📁 main_windows
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 main_window_oem.py
│   │   │   ├── 📄 main_window_recycler.py
│   │   │   └── 📄 main_window_user.py
│   │   ├── 📁 Oem_widgets
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 blueprint_gallery_widget.py
│   │   │   ├── 📄 car_model_form_widget.py
│   │   │   ├── 📄 fleet_telemetry_widget.py
│   │   │   ├── 📄 oem_ai_dashboard_widget.py
│   │   │   └── 📄 oem_blueprint_hub.py
│   │   ├── 📁 Recycler_widgets
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 company_explorer_widget.py
│   │   │   ├── 📄 global_exchange_widget.py
│   │   │   ├── 📄 material_analytics_widget.py
│   │   │   ├── 📄 recycler_hub.py
│   │   │   └── 📄 taxonomy_editor_widget.py
│   │   ├── 📁 registration
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 step1_role_view.py
│   │   │   ├── 📄 step2_cached_login_view.py
│   │   │   └── 📄 wizard_view.py
│   │   ├── 📄 __init__.py
│   │   └── 📄 README_view.md
│   └── 📄 main.py
├── 📄 ARCHITECTURE.md
└── 📄 print_tree.py

## Description of the project
VeriTwin is a modular and multi-tenant application designed for the automotive lifecycle. It serves as a bridge between OEMs (Original Equipment Manufacturers), car owners, and recyclers.

The application provides the following core features:

1. **OEM Product Lifecycle Management**:
   - **Digital Product Passports (DPP)**: OEMs can define the "digital birth" of a car, specifying components, materials, and expected lifespans.
   - **Fleet Telemetry**: OEMs can monitor the health and usage data of cars they have produced.
   - **Asset Tracking**: OEMs can track the movement of their vehicles through the supply chain.

2. **Vehicle Ownership and Digital Identity**:
   - **Secure Vehicle Transfer**: Owners can securely transfer the digital identity (VIN) of their car to new owners.
   - **Health Monitoring**: Owners can view the health status of their vehicle's components.

3. **Circular Economy Integration**:
   - **Recycler Portal**: Authorized recyclers can access the digital passport of end-of-life vehicles.
   - **Material Recovery**: Recyclers can identify valuable materials for extraction and reuse.

4. **Authentication and Authorization**:
   - **Multi-Tenant Architecture**: The system supports distinct user roles (OEM, Driver, Recycler) with appropriate permissions.
   - **Secure Login**: Users can log in with their credentials, which are securely hashed and stored.

## Features

- **[OEM] Fleet Management**: Track your fleet in real-time.
- **[OEM] Digital Twin**: Create and manage digital twins of your vehicles.
- **[Driver] Vehicle History**: View the complete history of your vehicle.
- **[Driver] Health Monitoring**: Monitor the health of your vehicle's components.
- **[Recycler] Material Recovery**: Identify valuable materials for extraction and reuse.
- **Multi-Tenant Authentication**: Secure login for different user roles.
- **Database Management**: Initialize and manage the database with dummy data.
- **UI/UX**: Professional and intuitive user interface.

## Sofware used

- **Python 3.11+**
- **PyQt6**
- **QFluentWidgets**
- **SQLAlchemy**
- **SQLite**

## Architecture of the project

### Model-View-Controller (MVC)
The project relies on a strict Model-View-Controller (MVC) architecture pattern to decouple the backend intelligence from the frontend rendering components. Here's how the three layers interact with each other:

1. **Models (Data & Logic layer)**: They query the SQLite database using raw SQL or ORM. When requested, they format and return the raw output. They have absolutely zero knowledge of the UI structure.
2. **Views (Presentation layer)**: These are the PyQt6 and QFluentWidgets components. They only define what the user sees and handle direct user interactions (clicks, text input). When an event occurs (e.g. submitting a form), they emit custom PyQt signals (`pyqtSignal`) without handling the business logic themselves.
3. **Controllers (Routing & Orchestration layer)**: They act as the brain bridging the two layers above. A controller gets instantiated with references to both a View and a Model. It connects the View's emitted signals to its own processing functions, requests data or operations from the Model, and subsequently updates the View (e.g., triggering `InfoBar` notifications or rendering a list of cards).

### 🏛️ The 3 Pillars of Digital Twin Data
#### The Birth Blueprint (OEM SSOT):
**Where it lives:** car_models table.

**Who writes to it:** Only the OEM.

**What it is:** Static data. Base price, theoretical max range, powertrain (ICE, BEV, HEV), drivetrain (FWD, AWD), expected tire lifespan. This data never changes once the model is defined.

**The Physical Instance:** (Registry SSOT):

**Where it lives:** vehicles and mounted_tires tables.

**Who writes to it:** The Factory/Dealership (Minting the VIN) or dynamically generated via Monte Carlo simulation for regional tracking.

**What it is:** The digital passport linking the physical object to its blueprint, including regional geographic location (`lat`, `lon`).

#### The Telemetry Stream:(Sensor SSOT):

**Where it lives:** A new `vehicle_telemetry` table.

**Who writes to it:** The Car's IoT Sensors.

**What it is:** Highly dynamic data. Current odometer (total distance), current GPS location, driving style score, real-time tire pressure.

### 🚗 Driver Dashboard & Telemetry Simulation
To showcase the app's real-time capabilities without needing physical hardware, the architecture implements a **Dynamic Telemetry Simulator**:
1. **Global Vehicle Selector (`main_window_user.py`)**: A dynamic ComboBox resides in the title bar allowing the user to seamlessly switch between multiple owned vehicles, propagating the active VIN to all downstream controllers.
2. **The Garage View (`garage_widget.py`)**: Renders a premium digital twin card combining the Birth Blueprint (model, image) and physical instance (VIN), along with live telemetry (odometer, driving score). It includes a "Simulate Trip" button.
3. **The Simulator (`trip_simulator.py`)**: Simulates real-world sensor fluctuations by pseudo-randomly updating the `vehicle_telemetry` table in SQLite (e.g., adding distance and slightly fluctuating the eco-score).
4. **Tire Lifecycle Management (`tire_controller.py`, `tire_model.py`)**: Ported from an advanced MATLAB predictive engine, this module visualizes 4-wheel telemetry and calculates non-linear tire wear based on vehicle mass, powertrain, and drivetrain. It provides AI-based recycler matchmaking and computes Circularity Scores and Safety Indices.

### ♻️ Recycler Hub & Live AI Market Analysis
To simulate the end-of-life circular economy, the architecture provides a **Global Salvage Exchange** powered by live intelligence:
1. **The Recycler Hub View (`recycler_hub.py`, `global_exchange_widget.py`, `material_analytics_widget.py`)**: Renders a premium high-end terminal displaying macro market cards. Clicking a card flips seamlessly to the AI Analytics Terminal.
2. **The Background ETL Pipeline (`data_ingestion_engine/`)**: A silent background thread started at application launch scrapes live RSS feeds for recycling commodities and caches them into the SQLite database via the `MarketCacheManager`.
3. **The MCP Agent Server (`mcp_agent_server/`)**: The `MotorValleyAgent` uses Gemini AI and external tools (like DuckDuckGo live search) to synthesize the cached real-world context into a strategic report.
4. **The Analytics Controller (`analytics_controller.py`)**: Catches UI requests and spins up a background `QThread` (`AgentWorker`) that streams the agent's generative text back to the terminal UI with a "hacker" typing effect, ensuring the UI remains responsive.
5. **Ecosystem Management (`taxonomy_editor_widget.py`, `company_explorer_widget.py`)**: Panel defines taxonomy. Panel issues company passports. Widget shows geographical map. Map uses Folium. Map prevents clutter. User selects category. Map updates.

This modular setup ensures that the View remains completely unaware of how the data is generated, while the database remains the Single Source of Truth (SSOT).