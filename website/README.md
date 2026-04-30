# Website Refactoring

Refactoring begins. Created main file. Main file initializes FastAPI. Main file mounts static folder.

Created router package. Created insurer API router. Router instantiates actuarial model. Router instantiates fleet model. Router defines three endpoints. 

Endpoints return JSON. Endpoints serve actuarial summary. Endpoints serve demographic data. Endpoints serve VSI data. 

Main file includes router. Setup successful.

## Frontend Shell

Build frontend shell. Create HTML file. HTML uses Tailwind CSS. Apply dark theme. Design mimics enterprise dashboard.

Create left sidebar. Sidebar contains four links. Create main content area. Content area contains four sections.

Create javascript file. Javascript handles navigation. Javascript toggles active sections. Click sidebar link. Javascript hides other sections. Javascript shows target section.

## Actuarial Dashboard Migration

Extract grid HTML. Extract Chart.js logic. Read original Python widget. 

Inject grid into index. Grid contains five charts. Keep 2x2 layout. Keep stacked chart bottom. 

Update Javascript file. Write fetch call. Endpoint serves demographic data. Javascript populates Chart instances. Javascript injects JSON data. 

Actuarial dashboard migrates successfully.

## AI Streaming Terminal Migration

Convert AI terminal. Create FastAPI endpoint. Endpoint uses StreamingResponse. Endpoint yields orchestrator generator. 

Update main application. Main app includes AI router. Update HTML index. Create hacker-style terminal UI. 

Update Javascript logic. Javascript handles terminal streaming. Javascript uses fetch API. Javascript reads data stream. Javascript appends text real-time. 

Terminal migration completes successfully.

## Live Fleet Telemetry Migration

Extract Folium logic. Read fleet widget. Import Folium package. Create FastAPI endpoint. Endpoint returns raw HTML. Endpoint yields map data. 

Update index file. Insert iframe container. Make iframe full width. 

Update Javascript logic. Javascript sets iframe source. Map loads on startup. Map loads on tab click. 

Telemetry map migration completes successfully.

## Executive Risk Summary Refactoring

Extract regional chart logic. Extract demographic chart logic. Update index HTML. Combine chart containers. Create tab toggles. 

Update Javascript logic. Javascript handles tab switching. Javascript fetches summary API. Javascript populates KPI cards. Javascript generates regional chart.

Chart separation completes successfully.

## Predictive Asset Risk Migration

Read original VSI widget. Extract layout logic. Update index HTML. Add DataLabels plugin. Create CSS grid. Insert canvas elements.

Update Javascript file. Javascript fetches VSI data. Javascript instantiates six charts. Javascript configures stacked bars. Javascript configures doughnut charts. Javascript formats DataLabels.

VSI migration completes successfully.
