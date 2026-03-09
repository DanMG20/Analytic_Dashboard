# Technical Architecture Manifest

## 1. Architecture Pattern: Decoupled ETL
The system is divided into independent layers (Extract, Transform, Load) to ensure that changes in the YouTube API or the Database engine do not break the entire pipeline.

## 2. Directory Structure
```text
project/
├── main.py                 # Application bootstrap and dependency injection.
├── config.py               # Global constants and API configurations.
├── api/                    # Extraction Layer (Raw data retrieval).
│   ├── youtube_auth.py     # OAuth2 credentials lifecycle management.
│   ├── youtube_data.py     # YouTube Data API v3 client (Metadata).
│   ├── youtube_analytics.py# YouTube Analytics API v2 client (Metrics).
│   └── data_builder.py     # Facade orchestrating multi-API extraction.
├── models/                 # Data Transfer Objects (API Contracts).
│   ├── raw_data.py         # Container for complete extraction results.
│   └── ...                 
├── database/               # Persistence Layer (Storage logic).
│   ├── connection.py       # DatabaseManager (Transactional Context Manager).
│   ├── models.py           # Pydantic models for DB validation.
│   └── repository.py       # SQL operations (Data Access Object).
├── services/               # Logic Layer (Processing & Control).
│   ├── data_processor.py   # Translation from API models to DB models.
│   └── updater.py          # Central Orchestrator (Business logic/Decisions).
├── scheduler/              # Automation Layer.
│   └── trigger.py          # APScheduler implementation.
└── utils/                  # Cross-cutting concerns.
    ├── logger.py           # Global logging configuration.
    ├── paths.py            # OS-independent path management.
    └── retry.py            # Resilience and retry logic.
```

## 3. Layer Responsibilities
**Extraction Layer (`api/`)**: Communicates with Google Services. It returns objects defined in `models/`. It is strictly "Read-only" regarding YouTube.

**Orchestration Layer (`services/updater.py`)**: Acts as the "Brain". It requests control dates from the Repository, decides the synchronization window, and commands the DataBuilder and DataProcessor.

**Transformation Layer (`services/data_processor.py`)**: Pure logic. It handles type conversion (e.g., ISO Strings to `datetime.date`) and structural mapping.

**Persistence Layer (`database/`)**: Handles the "Write" operations. It ensures data integrity through Pydantic validation and SQL transactions.

## 4. Design Principles Applied
* **Single Responsibility Principle (SRP):** Each class has one reason to change.
* **Dependency Injection:** Services are injected into the Updater and Repository, allowing for easier testing and modularity.
* **Early Returns:** Implemented across all logic to minimize nesting.
* **Type Safety:** Strict use of Pydantic and Type Hints for a robust data pipeline.

