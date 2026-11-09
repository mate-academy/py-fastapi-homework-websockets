# User Activity Tracking

Welcome to the **Movie Theater API** project! This educational assignment is designed to help you develop and refine your skills in creating robust web applications using FastAPI, SQLAlchemy, and Docker. Here's what the project offers:

## Table of Contents

- [Movie Theater API Project](#movie-theater-api-project)
  - [Features](#features)
    - [Database setup](#database-setup)
    - [Data population](#data-population)
    - [Docker integration](#docker-integration)
    - [Project structure](#project-structure)
    - [Updated Project Structure Overview](#updated-project-structure-overview)
  - [Root Directory](#root-directory)
  - [Commands](#commands)
  - [Docker Configuration](#docker-configuration)
  - [Source Directory (src)](#source-directory-src)
  - [Additional Features](#additional-features)
  - [Tip: Using Dependency Injection in FastAPI](#tip-using-dependency-injection-in-fastapi)
  - [Using `get_db` for Database Dependency Injection](#using-get_db-for-database-dependency-injection)
  - [Extended Dependency Injection in FastAPI](#extended-dependency-injection-in-fastapi)
  - [Handling Authentication via Authorization Headers](#handling-authentication-via-authorization-headers)
  - [Summary](#summary)
  - [Primary Services (docker-compose.yml)](#primary-services-docker-composeyml)
    - [1. Database Service (`db`)](#1-database-service-db)
    - [2. pgAdmin Service (`pgadmin`)](#2-pgadmin-service-pgadmin)
    - [3. Backend Service (`web`)](#3-backend-service-web)
    - [4. Database Migrator (`migrator`)](#4-database-migrator-migrator)
    - [5. MailHog Service (`mailhog`)](#5-mailhog-service-mailhog)
    - [6. MinIO Object Storage (`minio`)](#6-minio-object-storage-minio)
    - [7. MinIO Client (`minio_mc`)](#7-minio-client-minio_mc)
    - [8. MongoDB (`mongodb`)](#8-mongodb-mongodb)
    - [9. Mongo Express (`mongo-express`)](#9-mongo-express-mongo-express)
  - [Testing Services (docker-compose-tests.yml)](#testing-services-docker-compose-testsyml)
    - [1. Test Backend Service (`web`)](#1-test-backend-service-web)
    - [2. Test MailHog Service (`mailhog`)](#2-test-mailhog-service-mailhog)
    - [3. Test MinIO Storage (`minio`)](#3-test-minio-storage-minio)
    - [4. Test MinIO Client (`minio_mc`)](#4-test-minio-client-minio_mc)
  - [Volumes](#volumes)
  - [Networks](#networks)
  - [Summary (again)](#summary-1)
  - [How to Run the Project](#how-to-run-the-project)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Create and Activate a Virtual Environment](#2-create-and-activate-a-virtual-environment)
    - [3. Install Dependencies with Poetry](#3-install-dependencies-with-poetry)
    - [4. Create a `.env` File](#4-create-a-env-file)
    - [5. Run the Project with Docker Compose](#5-run-the-project-with-docker-compose)
    - [6. Access the Services](#6-access-the-services)
    - [7. Verify Setup](#7-verify-setup)
    - [8. Running the Development Server without Docker](#8-running-the-development-server-without-docker)
    - [9. Running End-to-End (E2E) Tests](#9-running-end-to-end-e2e-tests)
    - [10. Running Tests Locally](#10-running-tests-locally)
      - [Project Setup Summary](#project-setup-summary)
    - [Run project with PyCharm](#run-project-with-pycharm)
  - [Models and Entities Overview](#models-and-entities-overview)
    - [Accounts Models](#accounts-models)
      - [1. UserGroupModel](#1-usergroupmodel)
      - [2. UserModel](#2-usermodel)
      - [3. UserProfileModel](#3-userprofilemodel)
      - [4. TokenBaseModel](#4-tokenbasemodel)
      - [5. ActivationTokenModel](#5-activationtokenmodel)
      - [6. PasswordResetTokenModel](#6-passwordresettokenmodel)
      - [7. RefreshTokenModel](#7-refreshtokenmodel)
    - [Movie Models](#movie-models)
      - [1. MovieModel](#1-moviemodel)
      - [2. GenreModel](#2-genremodel)
      - [3. ActorModel](#3-actormodel)
      - [4. CountryModel](#4-countrymodel)
      - [5. LanguageModel](#5-languagemodel)
      - [6. Association Tables](#6-association-tables)
  - [Task Description: Extending the Cinema Application](#task-description-extending-the-cinema-application)
  - [Tasks: Implementing Email Notifications for User Registration and Password Reset](#tasks-implementing-email-notifications-for-user-registration-and-password-reset)
  - [Task: Implement User Profile Creation and Validation Schema](#task-implement-user-profile-creation-and-validation-schema)
    - [1. Profile Schema (`schemas/profiles.py`)](#1-profile-schema-schemasprofilespy)
    - [2. Profile Creation Endpoint (`routes/profiles.py`)](#2-profile-creation-endpoint-routesprofilespy)
    - [3. Endpoint Behavior and Error Handling](#3-endpoint-behavior-and-error-handling)
      - [1️⃣ Token Validation](#1-token-validation)
      - [2️⃣ Authorization Rules](#2-authorization-rules)
      - [3️⃣ User Existence and Status](#3-user-existence-and-status)
      - [4️⃣ Check for Existing Profile](#4-check-for-existing-profile)
      - [5️⃣ Avatar Upload to S3 Storage](#5-avatar-upload-to-s3-storage)
      - [6️⃣ Profile Creation and Storage](#6-profile-creation-and-storage)
    - [4. Full List of Possible Errors](#4-full-list-of-possible-errors)
    - [5. Next Steps](#5-next-steps)
      - [Tips and Guidance](#tips-and-guidance)
      - [Running Tests](#running-tests)
        - [1️⃣ Running Unit and Integration Tests (Without Docker)](#1-running-unit-and-integration-tests-without-docker)
        - [2️⃣ Running End-to-End (E2E) Tests](#2-running-end-to-end-e2e-tests)
      - [Test Results](#test-results)


## Features

### **Database setup**
- **PostgreSQL for development**: The application uses PostgreSQL as the main database for the development environment, configured via Docker Compose.
- **SQLite for testing**: A lightweight SQLite database is utilized for testing, ensuring fast and isolated test execution.
- **MongoDB for development and testing**: The application uses MongoDB to track user activity.

### **Data population**
- The database can be automatically populated with movie data from a provided dataset. This includes associated entities such as genres, actors, languages, and countries, ensuring a rich and interconnected data structure.

### **Docker integration**
- The project is fully Dockerized, allowing seamless setup and execution of the application and its dependencies.
- Docker Compose simplifies the orchestration of services like the FastAPI application, PostgreSQL database, and other required components.
- **MailHog for email testing**: The project includes **MailHog**, which captures outgoing emails and provides a web interface for viewing test emails. This is useful for testing user registration, password reset, and account activation flows.
- **MinIO for object storage**: The project integrates **MinIO**, an S3-compatible storage solution used for handling file uploads, such as user avatars.
- **Separate Docker Compose files**:
  - `docker-compose.yml`: The main configuration for development, including FastAPI, PostgreSQL, MailHog, and MinIO.
  - `docker-compose-test.yml`: A separate configuration optimized for **end-to-end (E2E) testing**, using SQLite as the test database.

### **Project structure**
A well-organized and modular project structure is provided, including:
- **Database models** and schemas for movies and related entities.
- **Routing logic** for managing API endpoints.
- **Utility scripts** for tasks like data seeding and database migrations.
- **Testing framework** integrated with `pytest`, including unit and E2E tests for API functionality.

This setup ensures a scalable, maintainable, and testable API that adheres to best practices in web development.

### Updated Project Structure Overview

The **Movie Theater API** project maintains a structured and modular organization, making development, testing, and deployment more efficient. Below is a detailed breakdown of the project's structure:

```plaintext
.
├── Dockerfile
├── README.MD
├── alembic.ini
├── commands
│   ├── run_migration.sh
│   ├── run_web_server_dev.sh
│   ├── setup_mailhog_auth.sh
│   └── setup_minio.sh
├── docker
│   ├── mailhog
│   │   └── Dockerfile
│   ├── minio_mc
│   │   └── Dockerfile
│   └── tests
│       └── Dockerfile
├── docker-compose.yml
├── docker-compose-tests.yml
├── init.sql
├── poetry.lock
├── pyproject.toml
├── pytest.ini
└── src
    ├── config
    │   ├── __init__.py
    │   ├── dependencies.py
    │   └── settings.py
    ├── database
    │   ├── __init__.py
    │   ├── migrations
    │   │   ├── README
    │   │   ├── env.py
    │   │   ├── script.py.mako
    │   │   └── versions
    │   │       ├── 2da0dc469be8_temp_migration.py
    │   │       ├── 32b1054a69e3_initial_migration.py
    │   │       └── 41cdafa531cf_temp_migration.py
    │   ├── models
    │   │   ├── __init__.py
    │   │   ├── accounts.py
    │   │   ├── base.py
    │   │   └── movies.py
    │   ├── populate.py
    │   ├── seed_data
    │   │   ├── imdb_movies.csv
    │   │   └── test_data.csv
    │   ├── session_postgresql.py
    │   ├── session_sqlite.py
    │   ├── source
    │   │   └── theater.db
    │   └── validators
    │       ├── __init__.py
    │       └── accounts.py
    ├── exceptions
    │   ├── __init__.py
    │   ├── email.py
    │   ├── security.py
    │   └── storage.py
    ├── main.py
    ├── lifespan.py
    ├── notifications
    │   ├── __init__.py
    │   ├── emails.py
    │   ├── interfaces.py
    │   └── templates
    │       ├── activation_complete.html
    │       ├── activation_request.html
    │       ├── password_reset_complete.html
    │       └── password_reset_request.html
    ├── routes
    │   ├── __init__.py
    │   ├── accounts.py
    │   ├── movies.py
    │   └── profiles.py
    │   └── activities.py
    ├── schemas
    │   ├── __init__.py
    │   ├── accounts.py
    │   ├── examples
    │   │   ├── __init__.py
    │   │   └── movies.py
    │   ├── movies.py
    │   └── profiles.py
    │   └── user_activity.py
    ├── security
    │   ├── __init__.py
    │   ├── http.py
    │   ├── interfaces.py
    │   ├── passwords.py
    │   ├── token_manager.py
    │   └── utils.py
    ├── storages
    │   ├── __init__.py
    │   ├── interfaces.py
    │   └── s3.py
    ├── tests
    │   ├── __init__.py
    │   ├── conftest.py
    │   ├── doubles
    │   │   ├── __init__.py
    │   │   ├── fakes
    │   │   │   ├── __init__.py
    │   │   │   └── storage.py
    │   │   │   └── activity.py
    │   │   └── stubs
    │   │       ├── __init__.py
    │   │       └── emails.py
    │   ├── test_e2e
    │   │   ├── __init__.py
    │   │   ├── test_email_notification.py
    │   │   └── test_storage.py
    │   │   └── test_user_activity.py
    │   └── test_integration
    │       ├── __init__.py
    │       ├── test_accounts.py
    │       ├── test_movies.py
    │       └── test_profiles.py
    ├── user_activity
    │   ├── __init__.py
    │   ├── activity_repo.py
    │   ├── activity_service.py
    │   ├── dependencies.py
    │   ├── interfaces.py
    │   ├── ws_activity_manager.py
    └── validation
        ├── __init__.py
        └── profile.py
```

---

### **Root Directory**
- **`README.MD`**: Main project documentation.
- **`docker-compose.yml`**: Configures the main application services using PostgreSQL, FastAPI, and MinIO.
- **`docker-compose-tests.yml`**: Configures services specifically for **end-to-end (e2e) testing**, including SQLite, MailHog, and MinIO.
- **`poetry.lock`** & **`pyproject.toml`**: Poetry-based dependency management.
- **`pytest.ini`**: Configuration for running tests.

---

### **Commands**
- **`run_migration.sh`**: Script to execute database migrations using Alembic.
- **`run_web_server_dev.sh`**: Script to start the FastAPI development server.
- **`setup_mailhog_auth.sh`**: Initializes authentication for the MailHog testing environment.
- **`setup_minio.sh`**: Configures MinIO client (`mc`) to work with the application.

---

### **Docker Configuration**
The `docker` directory contains **Dockerfiles** for different services:
- **`docker/mailhog/Dockerfile`**: Builds a custom MailHog container for email testing.
- **`docker/minio_mc/Dockerfile`**: Builds a MinIO client (`mc`) container for interacting with MinIO storage.
- **`docker/tests/Dockerfile`**: Builds a container for executing **end-to-end (e2e) tests**.

---

### **Source Directory (`src`)**

#### **Configuration (`config`)**
- **`dependencies.py`**: Defines FastAPI dependencies for dependency injection.
- **`settings.py`**: Manages project settings, including database configurations and external service settings.

#### **Database (`database`)**
- **`models/`**: Defines SQLAlchemy ORM models for **Users, Movies, and related entities**.
- **`migrations/`**: Contains Alembic migration scripts.
- **`populate.py`**: Seeds the database with initial movie data.
- **`session_postgresql.py`**: PostgreSQL session for development.
- **`session_sqlite.py`**: SQLite session for testing.

#### **Exceptions (`exceptions`)**
- **`email.py`**: Custom exceptions related to email notifications.
- **`security.py`**: Handles security-related exceptions.
- **`storage.py`**: Manages MinIO/S3-related exceptions.

#### **Notifications (`notifications`)**
- **`emails.py`**: Implements the **EmailSender** interface for sending email notifications.
- **`interfaces.py`**: Defines an interface for email-related operations.
- **`templates/`**: Stores HTML email templates:
  - `activation_request.html`
  - `activation_complete.html`
  - `password_reset_request.html`
  - `password_reset_complete.html`

#### **Routes (`routes`)**
- **`accounts.py`**: API endpoints for **user authentication and account management**.
- **`movies.py`**: API endpoints for **movies and related information**.
- **`profiles.py`**: API endpoints for **user profile management**.
- **`activitites.py`**: WebSocket for processing user activity.

#### **Schemas (`schemas`)**
- **`accounts.py`**: Defines schemas for user-related requests and responses.
- **`movies.py`**: Defines schemas for movie-related API responses.
- **`profiles.py`**: Defines schemas for user profile-related API operations.
- **`user_activity.py`**: Schemas for user activity-related operations.

#### **Security (`security`)**
- **`http.py`**: Handles HTTP security-related logic.
- **`interfaces.py`**: Defines interfaces for authentication and authorization services.
- **`passwords.py`**: Implements password hashing and verification.
- **`token_manager.py`**: Manages JWT authentication tokens.
- **`utils.py`**: Security utility functions.

#### **Storage (`storages`)**
- **`s3.py`**: Implements **MinIO/S3 storage client** for handling file uploads.
- **`interfaces.py`**: Defines an interface for interacting with **S3-compatible storage**.

#### **Testing (`tests`)**
- **`conftest.py`**: Defines shared test fixtures.
- **`doubles/`**: Contains test doubles (fakes, stubs, and mocks).
  - **`fakes/storage.py`**: Fake MinIO storage implementation for **unit testing**.
  - **`fakes/activity.py`**: Fake UserActivityRepository class for **unit testing**.
  - **`stubs/emails.py`**: Stub implementation for email notifications.
- **`test_e2e/`**: **End-to-End (E2E) tests** for API endpoints.
  - **`test_email_notification.py`**: Tests email notifications using MailHog.
  - **`test_storage.py`**: Tests S3 file upload functionality with MinIO.
  - **`test_user_activity.py`**: Tests for user activity functionalities.
- **`test_integration/`**: **Integration tests** for individual components.
  - **`test_accounts.py`**: Tests user authentication and account creation.
  - **`test_movies.py`**: Tests movie API operations.
  - **`test_profiles.py`**: Tests user profile creation and management.

#### **Validation (`validation`)**
- **`profile.py`**: Implements input validation for user profile creation.

---

### **Additional Features**
- **MinIO Integration**:
  - MinIO is used as an S3-compatible object storage for storing **profile avatars**.
  - Configured via Docker and managed using the MinIO client (`mc`).

- **MailHog Integration**:
  - MailHog is used as a mock SMTP server for testing **email notifications**.
  - A separate **Docker container** ensures email delivery in the testing environment.

- **E2E Testing Setup**:
  - The `docker-compose-tests.yml` file orchestrates services for **end-to-end tests**.
  - Uses **SQLite** for an isolated testing database.

### **Services Overview**

The project is configured with multiple services in both `docker-compose.yml` and `docker-compose-tests.yml`, allowing seamless development, testing, and deployment of the **Movie Theater API**. Below is a breakdown of the services and their roles.

---

## **Primary Services (docker-compose.yml)**

### **1. Database Service (`db`)**
- **Image**: `postgres:latest`
- **Purpose**: Acts as the primary PostgreSQL database for the application.
- **Configuration**:
  - Loads an initial schema from `init.sql`.
  - Uses a persistent Docker volume `postgres_theater_data` to store data.
  - Exposes PostgreSQL on port **5432**.
- **Health Check**: Uses `pg_isready` to ensure the database is ready before dependent services start.
- **Network**: Attached to `theater_network`.

---

### **2. pgAdmin Service (`pgadmin`)**
- **Image**: `dpage/pgadmin4`
- **Purpose**: Provides a web interface for managing and monitoring the PostgreSQL database.
- **Configuration**:
  - Exposes **pgAdmin** on port **3333**.
  - Uses a persistent volume `pgadmin_theater_data` to store settings.
- **Dependency**: Waits until `db` is healthy before starting.
- **Network**: Attached to `theater_network`.

---

### **3. Backend Service (`web`)**
- **Build Context**: Uses the local directory (`.`) as the build source.
- **Purpose**: Runs the **FastAPI application**, serving API endpoints.
- **Configuration**:
  - Runs the development server via `/commands/run_web_server_dev.sh`.
  - Uses `PYTHONPATH` to reference the `src` directory.
  - Enables live file watching (`WATCHFILES_FORCE_POLLING=true`).
  - Exposes the API on port **8000**.
- **Depends on**:
  - PostgreSQL
  - MinIO
  - MongoDB
  - The backend starts only after all required services become healthy.
- **Network**: Attached to `theater_network`.

---

### **4. Database Migrator (`migrator`)**
- **Build Context**: Shares the same build context as `web`.
- **Purpose**: Runs **Alembic migrations** to keep the database schema up-to-date.
- **Configuration**:
  - Uses the `run_migration.sh` script to apply migrations.
  - Mounts the `src` directory to access migration scripts.
- **Dependency**: Starts only after `db` is healthy.
- **Network**: Attached to `theater_network`.

---

### **5. MailHog Service (`mailhog`)**
- **Build Context**: Uses a **custom MailHog image** (Dockerfile located in `docker/mailhog`).
- **Purpose**: Provides a local SMTP server for **email testing**.
- **Configuration**:
  - Runs `setup_mailhog_auth.sh` to configure authentication.
  - Exposes **MailHog UI on port 8025** and SMTP on **port 1025**.
- **Network**: Attached to `theater_network`.

---

### **6. MinIO Object Storage (`minio`)**
- **Image**: `pgsty/minio` (community fork; `minio/minio` was removed from Docker Hub)
- **Purpose**: Provides an **S3-compatible storage** for managing file uploads.
- **Configuration**:
  - Runs the MinIO server with **console access on port 9001**.
  - Uses a persistent volume `minio_data` to store objects.
- **Health Check**: Checks MinIO’s `/minio/health/live` endpoint to ensure it's ready.
- **Network**: Attached to `theater_network`.

---

### **7. MinIO Client (`minio_mc`)**
- **Build Context**: Uses a **custom MinIO Client image** (Dockerfile in `docker/minio_mc`).
- **Purpose**: Configures MinIO storage, creates required buckets, and sets permissions.
- **Configuration**:
  - Runs `setup_minio.sh` to initialize storage.
- **Dependency**: Waits until `minio` is healthy before executing commands.
- **Network**: Attached to `theater_network`.

---

### 8. MongoDB (`mongodb`)

MongoDB is used as an additional NoSQL database for storing document-oriented data.

**Configuration:**

- Uses the official `mongo:7` image.
- Persists data in the `mongo_data` Docker volume.
- Exposes port **27017**.
- Includes a health check using `mongosh`.
- Shares the common `theater_network`.

---

### 9. Mongo Express (`mongo-express`)

Mongo Express provides a web-based administration interface for MongoDB.

**Configuration:**

- Uses the official `mongo-express` image.
- Depends on the `mongodb` service.
- Exposes the web interface on **http://localhost:8081**.
- Uses environment variables from the `.env` file.
- Connected to the shared Docker network.

---

## **Testing Services (docker-compose-tests.yml)**

To support **end-to-end (E2E) testing**, the project includes a **separate testing configuration** in `docker-compose-tests.yml`.

### **1. Test Backend Service (`web`)**
- **Build Context**: Uses a **dedicated test Dockerfile** (`docker/tests/Dockerfile`).
- **Purpose**: Runs **Pytest E2E tests**.
- **Configuration**:
  - Executes `pytest` with specific flags:
    ```sh
    pytest -m e2e --maxfail=5 --disable-warnings -v --tb=short
    ```
  - Uses a dedicated **testing environment** (`ENVIRONMENT=testing`).
- **Dependencies**: Waits for `mailhog` and `minio` before running tests.
- **Network**: Uses a separate network (`theater_network_test`).

---

### **2. Test MailHog Service (`mailhog`)**
- **Image**: `mailhog/mailhog`
- **Purpose**: Provides an SMTP server for email testing.
- **Configuration**:
  - Exposes **MailHog UI on port 8025** and **SMTP on port 1025**.
- **Network**: Attached to `theater_network_test`.

---

### **3. Test MinIO Storage (`minio`)**
- **Image**: `pgsty/minio` (community fork; `minio/minio` was removed from Docker Hub)
- **Purpose**: Provides **S3-compatible storage** for E2E tests.
- **Configuration**:
  - Uses **`minio-theater-test`** as the test container name.
  - Stores test files in a separate volume (`minio_data_test`).
  - Health checks ensure MinIO is ready before tests start.
- **Network**: Attached to `theater_network_test`.

---

### **4. Test MinIO Client (`minio_mc`)**
- **Build Context**: Uses the **same MinIO Client image** as production.
- **Purpose**: Configures **MinIO storage for testing**.
- **Configuration**:
  - Runs `setup_minio.sh` to initialize test storage.
- **Dependency**: Waits for `minio` before executing.
- **Network**: Attached to `theater_network_test`.

---

## **Volumes**
| Volume Name           | Purpose |
|-----------------------|---------|
| `postgres_theater_data` | Stores **PostgreSQL database** data. |
| `pgadmin_theater_data` | Stores **pgAdmin configuration**. |
| `minio_data` | Stores **MinIO objects** (production). |
| `minio_data_test` | Stores **MinIO objects** (testing). |
| `mongo_data` | MongoDB database files  |

---

## **Networks**
| Network Name | Description |
|-------------|-------------|
| `theater_network` | Connects **production** services. |
| `theater_network_test` | Connects **test** services. |

---

## **Summary**
- The **production services** in `docker-compose.yml` include:
  - PostgreSQL (**`db`**), pgAdmin (**`pgadmin`**), FastAPI backend (**`web`**), Alembic migrations (**`migrator`**), MailHog (**`mailhog`**), MinIO storage (**`minio`**), and MinIO client (**`minio_mc`**).
- The **E2E testing services** in `docker-compose-tests.yml` include:
  - A dedicated **test backend** running **pytest**, a separate **MailHog instance**, and **MinIO storage for test uploads**.
- **Separate networks (`theater_network` and `theater_network_test`)** ensure production and test environments remain isolated.

This modular structure ensures a robust and **scalable** development workflow, supporting **local development, integration testing, and production deployment**.

### **How to Run the Project**

Follow these steps to set up and run the **Movie Theater API** project on your local machine.

---

## **1. Clone the Repository**

Start by cloning the project repository from GitHub:

```bash
git clone <repository-url>
cd <repository-folder>
```

---

## **2. Create and Activate a Virtual Environment**

It is recommended to use a virtual environment to isolate project dependencies:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

---

## **3. Install Dependencies with Poetry**

This project uses **Poetry** for dependency management. Install dependencies as follows:

```bash
# Install Poetry if not already installed
pip install poetry

# Install project dependencies
poetry install
```

---

## **4. Create a `.env` File**

Create a `.env` file in the project root directory with the following variables. Customize the values as needed:

```env
# PostgreSQL
POSTGRES_DB=movies_db
POSTGRES_DB_PORT=5432
POSTGRES_USER=admin
POSTGRES_PASSWORD=some_password
POSTGRES_HOST=postgres_theater

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@gmail.com
PGADMIN_DEFAULT_PASSWORD=admin

# JWT keys
SECRET_KEY_ACCESS=838qKq7dGp34hWij3c8txA5ZD2qm9ybt
SECRET_KEY_REFRESH=cFzRk8kllHMW71wQKLXBqDzl24fkhisw
JWT_SIGNING_ALGORITHM=HS256

# MailHog
MAILHOG_USER=admin
MAILHOG_PASSWORD=some_password

# Email settings for MailHog
EMAIL_HOST=mailhog_theater
EMAIL_PORT=1025
EMAIL_HOST_USER=testuser@mate.com
EMAIL_HOST_PASSWORD=test_password
EMAIL_USE_TLS=False

# MinIO (S3-Compatible Storage)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=some_password
MINIO_HOST=minio-theater
MINIO_PORT=9000
MINIO_STORAGE=theater-storage

#MongoDB
MONGO_DB=movies
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=some_password
ME_CONFIG_MONGODB_ADMINUSERNAME=admin
ME_CONFIG_MONGODB_ADMINPASSWORD=some_password
ME_CONFIG_MONGODB_URL=mongodb://admin:some_password@mongodb:27017/
ME_CONFIG_BASICAUTH_USERNAME=admin
ME_CONFIG_BASICAUTH_PASSWORD=some_password
```

---

## **5. Run the Project with Docker Compose**

The project is **Dockerized** for easy setup. To start all the required services (**PostgreSQL, pgAdmin, FastAPI app, MailHog, MinIO, and Alembic migrator**), run:

```bash
docker-compose up --build
```

**Notes**:
- The first run **may take some time** as the database will be populated with initial data.
- Logs for services can be viewed using:

  ```bash
  docker-compose logs -f
  ```

---

## **6. Access the Services**

| Service        | URL |
|---------------|-------------------------|
| **API**       | `http://localhost:8000` |
| **pgAdmin**   | `http://localhost:3333` (Use `.env` credentials) |
| **MailHog UI** | `http://localhost:8025` (SMTP testing) |
| **MinIO Console** | `http://localhost:9001` (S3-compatible storage) |
| **Mongo Express** | `http://localhost:8081` |
| **MongoDB** | `mongodb://localhost:27017` |
---

## **7. Verify Setup**

After all services are running, you can test the API by accessing the **OpenAPI documentation**:

```plaintext
http://localhost:8000/docs
```

---

## **8. Running the Development Server without Docker**

If you prefer running the application **without Docker**, follow these steps:

1. **Ensure PostgreSQL is running** on your system with credentials matching `.env`.
2. **Apply migrations manually**:

   ```bash
   poetry run alembic upgrade head
   ```

3. **Start the development server**:

   ```bash
   poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## **9. Running End-to-End (E2E) Tests**

The project includes **E2E tests** that validate the system using a **separate testing environment**. These tests run inside **dedicated containers** using `docker-compose-tests.yml`.

### **Steps to Run E2E Tests**
1. **Start the test environment**:
   ```bash
   docker-compose -f docker-compose-tests.yml up --build
   ```

2. **Run E2E tests manually (inside a container)**:
   ```bash
   docker exec -it backend_theater_test pytest -m e2e --maxfail=5 --disable-warnings -v --tb=short
   ```

3. **Stop the test environment**:
   ```bash
   docker-compose -f docker-compose-tests.yml down -v
   ```

---

## **10. Running Tests Locally**

For **unit and integration tests**, use:

```bash
pytest -m "unit or integration" --disable-warnings -v
```

---

### **Project Setup Summary**
| Task | Command |
|------|---------|
| **Run all services (Dockerized)** | `docker-compose up --build` |
| **Run development server manually** | `poetry run uvicorn src.main:app --reload` |
| **Apply database migrations** | `poetry run alembic upgrade head` |
| **Run E2E tests** | `docker-compose -f docker-compose-tests.yml up --build` |
| **Run unit/integration tests** | `pytest -m "unit or integration" -v` |

---

### Run project with PyCharm

1. Mark the `src` directory as root
    ![mark src directory as root](./assets/images/1_mark_directory_as_source_root.png)
2. Close all open code tabs
3. Restart `PyCharm`
4. Create a new Run Configuration for the `FastAPI` project
    ![create new fastapi run configuration](./assets/images/2_create_new_run_config.png)
5. Add the required environment variables to the Run Configuration.
6. Start the local Docker Compose services:
    ```bash
    docker-compose -f docker-compose-local.yml up --build -d
    ```
7. Wait for the initial database seeding to finish (this may take a moment the first time).
    ![seed db](./assets/images/4_seed_db.png)  
8. Run the project via `PyCharm` and use breakpoints for debugging
9. If you need to apply database migrations manually, run:
    ```bash
    docker-compose -f docker-compose-local.yml up --build migrator
    ```

---

### Task Description: Implement user activity tracking functionality in a FastAPI project using WebSockets.
The project already has a skeleton for the "who's online" feature:

- `POST /api/v1/accounts/login/` — already calls `activity_repo.create_user_activity(...)` after a successful login;
- `GET /api/v1/activity/users/` WebSocket endpoint — already wired up and delegates all work to the service;
- Pydantic schemas (`UserBaseDTO`, `UpdateUserActivitySchema`, `UserActivitySchema`) — ready;
- abstract interfaces (`UserActivityRepoInterface`, `UserActivityWebSocketManagerInterface`,
  `UserActivityServiceInterface`) — ready, this is your contract;
- DI wiring (`dependencies.py`) — already assembles the components together.

**Your task** is to implement three classes whose method bodies have been stripped out:

1. `UserActivityRepository` (MongoDB)
2. `UserActivityWebSocketManager` (in-memory connection manager)
3. `UserActivityService.process` (orchestration of a single WebSocket connection)

---

### Step 0. Understand the "map" of the system

A single WebSocket connection goes through this path:

```
Client -> WS endpoint -> UserActivityService.process()
                              ├─ authenticate via token
                              ├─ activity_repo.update_user_activity(status=online)
                              ├─ ws_manager.connect(...)
                              ├─ send the client an online_users snapshot
                              └─ read messages until the client disconnects
                                     └─ ws_manager.disconnect(...)
                                     └─ activity_repo.update_user_activity(status=offline)
```

`UserActivityWebSocketManager` is the "address book" of active sockets in the
process memory (`Dict[user_id, List[WebSocket]]`), which knows how to
broadcast events to other users.

`UserActivityRepository` is the persistence layer in MongoDB, which simply
stores the current status (`online`/`offline`) and timestamps.

---

## Data model & payload reference

This is the part that's usually missing when people implement this feature
from scratch — the exact field names matter, because the tests assert on
them directly.

### MongoDB document (`user_activity` collection)

One document per user:

```json
{
  "user_id": 1,
  "email": "user@example.com",
  "status": "online",
  "connected_at": "2026-01-01T12:00:00Z",
  "disconnected_at": null
}
```

- `user_id` — the lookup key (`update_one({"user_id": ...})`), **not** `_id`.
- `status` — either `"online"` or `"offline"`.
- `connected_at` / `disconnected_at` — set only when relevant; the other one
  is simply absent/`null` until it happens at least once.

### WebSocket message payloads (exact shapes expected by the tests)

**1. `online_users`** — sent as a *personal* message to the user right after
they connect. `users` is a list of full `UserActivitySchema` objects:

```json
{
  "event": "online_users",
  "users": [
    {"user_id": 1, "email": "user1@example.com", "status": "online", "connected_at": "...", "disconnected_at": null},
    {"user_id": 2, "email": "user2@example.com", "status": "online", "connected_at": "...", "disconnected_at": "..."}
  ]
}
```

**2. `user_connected`** — *broadcast* to everyone except the user who just
connected. `user` is the single full `UserActivitySchema` of that user
(the same object `update_user_activity` returned for them):

```json
{
  "event": "user_connected",
  "user": {"user_id": 2, "email": "user2@example.com", "status": "online", "connected_at": "...", "disconnected_at": null}
}
```

**3. `user_disconnected`** — *broadcast* to everyone. Note this one carries
only the bare `user_id`, **not** a nested `user` object:

```json
{
  "event": "user_disconnected",
  "user_id": 2
}
```

### Step 1. `UserActivityRepository` (MongoDB)

File: `src/user_activity/activity_repo.py`

Implement the three methods of the `UserActivityRepoInterface` interface:

#### `create_user_activity(user_data: UserBaseDTO) -> None`
Called once on login. Must **create or overwrite** the user's document in the
`user_activity` collection with status `"offline"`.

Hints:
- use `update_one(..., upsert=True)`, not `insert_one` — login can happen
  more than once;
- the lookup key is `user_id`.

#### `update_user_activity(user_data: UpdateUserActivitySchema) -> UserActivitySchema`
Called on WebSocket connect/disconnect. Must:
1. Update only the fields that are not `None` (leave `connected_at` or `disconnected_at` as they are).
2. Read the full document back and return it as a `UserActivitySchema`.

Hint: don't forget `{"_id": 0}` in the `find_one` projection, so you don't
pull a non-serializable `ObjectId` into the Pydantic schema.

#### `get_all_active_users() -> List[UserActivitySchema]`
Returns all users with status `"online"`.

---

### Step 2. `UserActivityWebSocketManager` (in-memory)

File: `src/user_activity/ws_activity_manager.py`

State — `self.active_connections: Dict[int, List[WebSocket]]`, already
declared in `__init__`.

#### `connect(websocket, user_data) -> None`
1. Add the socket to this `user_id`'s list of connections (create the list
   if it doesn't exist yet).
2. If this is the user's **first** active connection — broadcast an event to all **other** users:
   ```json
   {"event": "user_connected", "user": {...}}
   ```
   and `exclude=user_data.user_id` — i.e. everyone gets the message **except
   the user who just connected** (they already got their own state via the
   `online_users` snapshot in the service, so they don't need to be told
   about themselves).
   If the user already has another active tab open, the event should **not**
   be broadcast at all (see the duplicate-connection test below).

#### `disconnect(user_id, websocket) -> None`
1. Remove the specific socket from the user's list of connections.
2. If the list is **empty** after removal — delete the key and broadcast an
   event to everyone:
   ```json
   {"event": "user_disconnected", "user_id": ...}
   ```
   If the user still has another active tab open, the event should not be
   broadcast.

#### `_broadcast(message, exclude=None) -> None`
Send `message` to all active sockets of all users, except `exclude` (if
provided).

#### `send_personal_message(message, user_id) -> None`
Send `message` to all active sockets of **one specific** user (there may be
several tabs).

---

### Step 3. `UserActivityService.process`

File: `user_activity/activity_service.py`

This is the "conductor" — it ties together the repository, the manager, and
the raw `WebSocket`. Sequence of actions:

1. `await websocket.accept()`.
2. Wait for the first message from the client with a timeout (e.g. 30
   seconds) — expected to be a JSON payload like `{"token": "..."}`.
   - No message within the timeout → close with code
     `status.WS_1008_POLICY_VIOLATION`.
   - No `token` field in the message → close with the same code.
3. Decode the token via `jwt_auth_manager.decode_access_token(token)`.
   - On `TokenExpiredError` / `InvalidTokenError`, or a missing `user_id` in
     the payload → close with code `status.WS_1008_POLICY_VIOLATION`.
4. Mark the user as `online` via `activity_repo.update_user_activity(...)`
   (with `connected_at`).
5. Register the connection via `activity_ws_manager.connect(websocket, ...)`.
6. Send **this specific** user a snapshot of all active users:
   ```json
   {"event": "online_users", "users": [...]}
   ```
   via `send_personal_message`.
7. Loop reading incoming messages (`websocket.receive_json()`) until the
   client disconnects.
8. On `WebSocketDisconnect`:
   - call `activity_ws_manager.disconnect(user_id, websocket)`;
   - mark the user as `offline` via `update_user_activity(...)` (with
     `disconnected_at`).

---

### **Tips and Guidance**

If you’re unsure about the expected behavior or need clarification, **refer to the provided test suite**. Running the tests will:

- Show the expected logic and flow for each endpoint.
- Help you identify edge cases and handle errors correctly.
- Ensure your implementation aligns with the project's requirements.

### **Running Tests**

#### **1️⃣ Running Unit and Integration Tests (Without Docker)**
You can run the unit and integration tests **directly** using `pytest`:

```bash
pytest src/tests/test_integration/
```
This will execute **only the integration tests**, ensuring that your API logic functions correctly **without spinning up Docker containers**.

#### **2️⃣ Running End-to-End (E2E) Tests**
To run the full **E2E test suite**, you need to start the test environment using Docker:

```bash
docker-compose -f docker-compose-tests.yml up --build
```
This will spin up all necessary services (database, MinIO, MailHog, FastAPI instance) and execute the **end-to-end tests** inside the test container.

### **Test Results**
- The test logs will **highlight any failures** and discrepancies between your implementation and expected behavior.
- Use the error messages from the test output to **fix issues and adjust your code accordingly**.

By following these steps, you can ensure your implementation is correct and fully aligned with the **Movie Theater API** project requirements.
