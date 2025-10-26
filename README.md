# HNG Stage 2 Backend Task - Country Currency & Exchange API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-Latest-red.svg)](https://sqlmodel.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)](https://www.postgresql.org/)

A RESTful API built with FastAPI that fetches country data from external APIs, processes exchange rates, calculates estimated GDP, and provides comprehensive CRUD operations with filtering and sorting capabilities. Part of the HNG Internship Stage 2 Backend task.

## 🚀 Live Demo

**API Base URL:** [https://hng2-production-349e.up.railway.app](https://hng2-production-349e.up.railway.app)

**Interactive API Documentation (Swagger UI):** [https://hng2-production-349e.up.railway.app/docs](https://hng2-production-349e.up.railway.app/docs#/)

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Running Locally](#running-locally)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [External APIs](#external-apis)
- [Deployment](#deployment)
- [Error Handling](#error-handling)
- [Testing](#testing)

## ✨ Features

- **Data Aggregation**: Fetches country data from RestCountries API and exchange rates from ExchangeRate API
- **GDP Calculation**: Automatically computes estimated GDP using population, random multiplier, and exchange rates
- **PostgreSQL Database**: Persistent storage with async SQLModel ORM
- **Advanced Filtering**: Filter countries by region, currency, and sort by GDP
- **Image Generation**: Creates summary images with top 5 countries by GDP using Pillow
- **CRUD Operations**: Full Create, Read, Update, Delete functionality
- **Async Support**: Asynchronous database and HTTP operations for optimal performance
- **Smart Caching**: Refresh data on-demand, stored efficiently in database
- **Auto-Documentation**: Interactive Swagger UI and ReDoc
- **Production Ready**: Deployed on Railway with PostgreSQL

## 📁 Project Structure

```
hng_2/
│
├── src/
│   ├── countries/
│   │   ├── __init__.py          # Package initialization
│   │   ├── models.py            # SQLModel database models
│   │   ├── schemas.py           # Pydantic schemas for response validation
│   │   ├── services.py          # Business logic and external API calls
│   │   └── routes.py            # API route definitions
│   │
│   ├── db/
│   │   └── main.py              # Database connection and session management
│   │
│   └── main.py                  # FastAPI application entry point
│
├── cache/                       # Generated summary images (gitignored)
├── .env                         # Environment variables (gitignored)
├── .gitignore                   # Git ignore file
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## 🛠️ Technologies Used

- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern, fast web framework for building APIs
- **[Python 3.11+](https://www.python.org/)**: Programming language
- **[SQLModel](https://sqlmodel.tiangolo.com/)**: SQL databases with Python types (async)
- **[PostgreSQL](https://www.postgresql.org/)**: Relational database
- **[Uvicorn](https://www.uvicorn.org/)**: ASGI server for running FastAPI applications
- **[Pydantic](https://docs.pydantic.dev/)**: Data validation using Python type hints
- **[httpx](https://www.python-httpx.org/)**: Async HTTP client for external API calls
- **[Pillow (PIL)](https://pillow.readthedocs.io/)**: Image generation library
- **[Railway](https://railway.app/)**: Deployment platform

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- PostgreSQL database
- Git

### Steps

1. **Clone the repository**

```bash
git clone https://github.com/Anjola11/hng_2.git
cd hng_2
```

2. **Create a virtual environment** (recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/countries_db
```

## 🚀 Running Locally

### Method 1: Using Uvicorn (Recommended)

```bash
uvicorn src.main:app --reload
```

The API will be available at:
- **Base URL**: http://127.0.0.1:8000
- **Swagger Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Method 2: Custom host and port

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
```

## 📖 API Documentation

### 1. Refresh Countries Data

**POST** `/countries/refresh`

Fetches data from external APIs, calculates GDP, and caches in database. Also generates a summary image.

#### Response (200 OK)

```json
{
  "message": "Countries refreshed successfully",
  "total_countries": 250,
  "timestamp": "2025-10-25T15:30:16.375395+00:00"
}
```

#### Features
- Fetches ~250 countries from RestCountries API
- Gets real-time exchange rates for all currencies
- Calculates estimated GDP: `population × random(1000-2000) ÷ exchange_rate`
- Handles countries with no currency (sets GDP to 0)
- Handles currencies not in exchange API (sets exchange_rate to null)
- Updates existing countries or inserts new ones (case-insensitive matching)
- Generates summary image with top 5 countries by GDP
- Updates global refresh metadata

---

### 2. Get All Countries

**GET** `/countries` or `/countries/`

Retrieves all countries with optional filtering and sorting.

#### Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `region` | string | Filter by region (case-insensitive) | `Africa`, `Europe` |
| `currency` | string | Filter by currency code (case-insensitive) | `USD`, `NGN` |
| `sort` | string | Sort by GDP (`gdp_asc` or `gdp_desc`) | `gdp_desc` |

#### Example Requests

```bash
# Get all countries
GET /countries/

# Filter by region
GET /countries/?region=Africa

# Filter by currency
GET /countries/?currency=USD

# Sort by GDP (descending)
GET /countries/?sort=gdp_desc

# Combine filters
GET /countries/?region=Europe&sort=gdp_desc
```

#### Response (200 OK)

```json
[
  {
    "id": "179f7502-02ee-404e-a8b6-77a329dbd801",
    "name": "Algeria",
    "capital": "Algiers",
    "region": "Africa",
    "population": 44700000,
    "currency_code": "DZD",
    "exchange_rate": 130.161814,
    "estimated_gdp": 468095963.5838779,
    "flag_url": "https://flagcdn.com/dz.svg",
    "last_refreshed_at": "2025-10-25T15:30:16.375395Z"
  }
]
```

---

### 3. Get Single Country

**GET** `/countries/{country_name}`

Retrieve a specific country by name (case-insensitive).

#### Example Request

```bash
GET /countries/Nigeria
```

#### Response (200 OK)

```json
{
  "id": "1bca200e-a181-415d-b919-a857234abf72",
  "name": "Nigeria",
  "capital": "Abuja",
  "region": "Africa",
  "population": 206139587,
  "currency_code": "NGN",
  "exchange_rate": 1462.574942,
  "estimated_gdp": 242595893.58346474,
  "flag_url": "https://flagcdn.com/ng.svg",
  "last_refreshed_at": "2025-10-25T15:30:16.375395Z"
}
```

#### Error Response (404 Not Found)

```json
{
  "error": "Country not found"
}
```

---

### 4. Delete Country

**DELETE** `/countries/{country_name}`

Delete a country from the database.

#### Example Request

```bash
DELETE /countries/Nigeria
```

#### Response (200 OK)

```json
{
  "message": "Country 'Nigeria' deleted successfully"
}
```

#### Error Response (404 Not Found)

```json
{
  "error": "Country not found"
}
```

---

### 5. Get Refresh Status

**GET** `/countries/status`

Returns metadata about the last refresh operation.

#### Response (200 OK)

```json
{
  "id": 1,
  "last_refreshed_at": "2025-10-25T15:30:16.375395Z",
  "total_countries": 250
}
```

---

### 6. Get Summary Image

**GET** `/countries/image`

Serves the generated summary image showing top 5 countries by GDP.

#### Response (200 OK)

Returns a PNG image file.

#### Features
- Shows total number of countries
- Lists top 5 countries by estimated GDP
- Displays last refresh timestamp
- Generated automatically after each `/refresh` call

#### Error Response (404 Not Found)

```json
{
  "error": "Summary image not found"
}
```

---

## 🗄️ Database Schema

### Countries Table

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | No | Primary key (auto-generated) |
| `name` | VARCHAR | No | Country name (unique, indexed) |
| `capital` | VARCHAR | Yes | Capital city |
| `region` | VARCHAR | Yes | Geographic region |
| `population` | INTEGER | No | Population count |
| `currency_code` | VARCHAR | Yes | ISO currency code (e.g., USD) |
| `exchange_rate` | FLOAT | Yes | Exchange rate to USD |
| `estimated_gdp` | FLOAT | Yes | Calculated GDP estimate |
| `flag_url` | TEXT | Yes | URL to country flag image |
| `last_refreshed_at` | TIMESTAMP | No | UTC timestamp of last update |

### Refresh Metadata Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key (always 1) |
| `last_refreshed_at` | TIMESTAMP | Global last refresh timestamp |
| `total_countries` | INTEGER | Total countries in database |

---

## 🌐 External APIs

### 1. RestCountries API

**Endpoint**: `https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies`

**Purpose**: Fetches country data including name, capital, region, population, flag, and currencies.

**Rate Limit**: None specified

### 2. ExchangeRate API

**Endpoint**: `https://open.er-api.com/v6/latest/USD`

**Purpose**: Provides real-time exchange rates for all currencies relative to USD.

**Rate Limit**: None specified (free tier)

---

## 🧮 GDP Calculation Logic

The estimated GDP is calculated using the formula:

```
estimated_gdp = (population × random_multiplier) ÷ exchange_rate
```

Where:
- `population`: Country's population
- `random_multiplier`: Random float between 1000 and 2000 (recalculated on each refresh)
- `exchange_rate`: Currency's exchange rate to USD

**Special Cases**:
- No currency (`currency_code = null`): `estimated_gdp = 0`
- Currency not found in exchange API: `estimated_gdp = null`
- Multiple currencies: Only the first currency is used

---

## 🌐 Deployment

This project is deployed on **Railway** with PostgreSQL database.

### Deployment Steps

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize project**:
   ```bash
   railway init
   ```

4. **Add PostgreSQL**:
   ```bash
   railway add postgresql
   ```

5. **Set environment variables**:
   Railway automatically provides `DATABASE_URL`

6. **Deploy**:
   ```bash
   railway up
   ```

### Environment Variables on Railway

- `DATABASE_URL`: Automatically set by Railway PostgreSQL plugin
- `PORT`: Automatically set by Railway

---

## ⚠️ Error Handling

The API implements comprehensive error handling with consistent JSON responses.

### HTTP Status Codes

| Status Code | Description | Example |
|-------------|-------------|---------|
| `200 OK` | Successful GET/DELETE request | Fetching countries |
| `404 Not Found` | Resource not found | Country doesn't exist |
| `500 Internal Server Error` | Database or server error | Database connection failed |
| `503 Service Unavailable` | External API unavailable | RestCountries API down |

### Error Response Format

```json
{
  "error": "External data source unavailable",
  "details": "Could not fetch countries: Connection timeout"
}
```

---

## 🧪 Testing

### Manual Testing with cURL

1. **Refresh data**:
```bash
curl -X POST "https://hng2-production-349e.up.railway.app/countries/refresh"
```

2. **Get all countries**:
```bash
curl "https://hng2-production-349e.up.railway.app/countries/"
```

3. **Filter by region**:
```bash
curl "https://hng2-production-349e.up.railway.app/countries/?region=Africa"
```

4. **Filter by currency**:
```bash
curl "https://hng2-production-349e.up.railway.app/countries/?currency=USD"
```

5. **Sort by GDP**:
```bash
curl "https://hng2-production-349e.up.railway.app/countries/?sort=gdp_desc"
```

6. **Get single country**:
```bash
curl "https://hng2-production-349e.up.railway.app/countries/Nigeria"
```

7. **Get status**:
```bash
curl "https://hng2-production-349e.up.railway.app/countries/status"
```

8. **Get summary image**:
```bash
curl "https://hng2-production-349e.up.railway.app/countries/image" --output summary.png
```

9. **Delete country**:
```bash
curl -X DELETE "https://hng2-production-349e.up.railway.app/countries/Nigeria"
```

### Using Swagger UI

Visit [https://hng2-production-349e.up.railway.app/docs](https://hng2-production-349e.up.railway.app/docs#/) for interactive testing with a user-friendly interface.

---

## 📝 Requirements

```txt
fastapi
uvicorn[standard]
sqlmodel
asyncpg
httpx
pillow
python-dotenv
```

---

## 🤝 Contributing

This is a learning project for the HNG Internship. If you find issues or have suggestions:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is part of the HNG Internship and is for educational purposes.

---

## 🔗 Links

- **GitHub Repository**: [https://github.com/Anjola11/hng_2](https://github.com/Anjola11/hng_2)
- **Live API**: [https://hng2-production-349e.up.railway.app](https://hng2-production-349e.up.railway.app)
- **API Documentation**: [https://hng2-production-349e.up.railway.app/docs](https://hng2-production-349e.up.railway.app/docs#/)
- **HNG Internship**: [https://hng.tech/internship](https://hng.tech/internship)

---

## 👨‍💻 Author

**Anjola**

Created as part of the HNG Internship Stage 2 Backend task.

---

## 🙏 Acknowledgments

- HNG Internship for the opportunity and task requirements
- RestCountries API for providing free country data
- ExchangeRate API for real-time exchange rates
- FastAPI community for excellent documentation

---

**Note**: This project demonstrates skills in API integration, data processing, async operations, database design, and deployment - all essential for backend development.
