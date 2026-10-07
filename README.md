# Urja Meter API

A clean REST API wrapper around the legacy **Urja Meter Ops** web portal.

The project reverse-engineers the portal's network APIs and exposes a simpler, typed, documented API for retrieving meter information, consumption data, and geographic location.

---

## 1. Overview

The upstream system is a SvelteKit-based web portal used for meter operations.

Instead of exposing the legacy portal directly to consumers, this service provides a small, stable REST API over the portal's existing JSON endpoints.

### High-level architecture

```text
                    ┌──────────────────────┐
                    │     API Consumer     │
                    └──────────┬───────────┘
                               │
                               │ HTTP
                               ▼
                    ┌──────────────────────┐
                    │     FastAPI API      │
                    │                      │
                    │  /api/v1/meters      │
                    │  /consumption        │
                    │  /location           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     MeterService     │
                    │                      │
                    │ Validation / Mapping │
                    │ Data normalization   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    PortalClient      │
                    │                      │
                    │ Authentication       │
                    │ Session management   │
                    │ Upstream requests    │
                    └──────────┬───────────┘
                               │
                               │ HTTPS
                               ▼
                    ┌──────────────────────┐
                    │   Urja Meter Ops     │
                    │   Legacy Portal      │
                    └──────────────────────┘
```

### Main responsibilities

- Discover and consume the portal's JSON endpoints
- Handle portal authentication and session management
- Provide a clean REST API
- Normalize inconsistent upstream response formats
- Validate API inputs
- Translate upstream failures into appropriate HTTP responses
- Keep portal-specific implementation details isolated from the API layer

---

## 2. Features

- FastAPI-based REST API
- Portal authentication using the existing login flow
- Reusable authenticated HTTP session
- Automatic re-authentication after an upstream `401`
- Meter search with pagination
- Individual meter lookup
- Energy/consumption readings
- Geographic coordinates
- Pydantic response models
- Input validation
- Upstream error handling
- Unit tests with mocked upstream calls
- Live integration test against the portal
- OpenAPI specification
- Swagger UI and ReDoc
- Environment-based configuration
- No credentials committed to the repository

---

## 3. API Endpoints

Base API path:

```text
/api/v1
```

### 3.1 Search meters

```http
GET /api/v1/meters
```

Query parameters:

| Parameter | Type | Default | Description |
|---|---|---:|---|
| `search` | string | `""` | Meter ID or search text |
| `page` | integer | `1` | Page number, must be >= 1 |

Example:

```http
GET /api/v1/meters?search=J100002&page=1
```

Example response:

```json
{
  "data": [
    {
      "meter_id": "J100002",
      "serial_number": "AL28136",
      "make": "L&T",
      "phase_type": "single",
      "installation_status": "Installed",
      "distribution_transformer": "DT-003"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

---

### 3.2 Get a meter

```http
GET /api/v1/meters/{meter_id}
```

Example:

```http
GET /api/v1/meters/J100002
```

Example response:

```json
{
  "meter_id": "J100002",
  "serial_number": "AL28136",
  "make": "L&T",
  "phase_type": "single",
  "installation_status": "Installed",
  "distribution_transformer": "DT-003"
}
```

If the meter cannot be found:

```http
404 Not Found
```

---

### 3.3 Get consumption data

```http
GET /api/v1/meters/{meter_id}/consumption
```

Example:

```http
GET /api/v1/meters/J100002/consumption
```

Example response:

```json
{
  "meter_id": "J100002",
  "readings": [
    {
      "timestamp": "2026-06-23T23:30:00",
      "kwh": 6850.32,
      "kvah": 7398.35,
      "voltage_r": 227.0
    }
  ]
}
```

The upstream portal returns numeric values as strings and timestamps in:

```text
DD/MM/YYYY HH:mm
```

The API converts these into appropriate numeric types and ISO-8601 timestamps.

---

### 3.4 Get meter location

```http
GET /api/v1/meters/{meter_id}/location
```

Example:

```http
GET /api/v1/meters/J100002/location
```

Example response:

```json
{
  "meter_id": "J100002",
  "latitude": 26.840224163401967,
  "longitude": 75.71461868999545
}
```

---

## 4. Health Check

The service exposes a simple health endpoint:

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

A root endpoint is also available:

```http
GET /
```

Response:

```json
{
  "service": "Urja Meter API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

## 5. Interactive API Documentation

Once the application is running, FastAPI provides interactive documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

### OpenAPI specification

```text
http://127.0.0.1:8000/openapi.json
```

A static copy of the OpenAPI specification is also included in:

```text
openapi.json
```

---

## 6. Project Structure

```text
urja-meter-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── meter.py
│   │
│   ├── portal/
│   │   ├── __init__.py
│   │   └── client.py
│   │
│   └── services/
│       ├── __init__.py
│       └── meter_service.py
│
├── tests/
│   ├── test_api.py
│   ├── test_portal_client.py
│   └── test_portal_manual.py
│
├── .gitignore
├── README.md
├── PROTOCOL.md
├── openapi.json
├── pytest.ini
└── requirements.txt
```

### Layer responsibilities

#### `app/api`

Contains FastAPI routes and HTTP-level validation/error handling.

#### `app/services`

Contains application-level logic and transformation of upstream data into public API models.

#### `app/portal`

Contains all communication with the legacy Urja portal, including authentication and session handling.

#### `app/models`

Contains Pydantic models defining the API contract.

#### `tests`

Contains unit tests and a live integration test.

---

## 7. Technology Stack

- Python 3.14
- FastAPI
- Pydantic
- Pydantic Settings
- HTTPX
- Pytest
- Respx
- Uvicorn

---

## 8. Installation

Clone the repository:

```bash
git clone https://github.com/sumanthvardhinedi/urja-meter-api.git
cd urja-meter-api
```

Create a virtual environment:

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 9. Configuration

Create a `.env` file in the project root.

```env
URJA_BASE_URL=https://urja-ops.flockenergy.tech
URJA_USERNAME=<your-username>
URJA_PASSWORD=<your-password>
```

The actual credentials must not be committed to Git.

The repository's `.gitignore` excludes `.env`.

---

## 10. Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Verify the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## 11. Example API Usage

### Search for a meter

```bash
curl "http://127.0.0.1:8000/api/v1/meters?search=J100002&page=1"
```

### Get meter details

```bash
curl "http://127.0.0.1:8000/api/v1/meters/J100002"
```

### Get consumption

```bash
curl "http://127.0.0.1:8000/api/v1/meters/J100002/consumption"
```

### Get location

```bash
curl "http://127.0.0.1:8000/api/v1/meters/J100002/location"
```

---

## 12. Upstream Portal Protocol

The API communicates with the following discovered portal endpoints:

| Purpose | Method | Upstream endpoint |
|---|---|---|
| Authentication | POST | `/login` |
| Meter search | GET | `/portal/meters/search` |
| Energy readings | GET | `/portal/meters/{meter_id}/energy` |
| Location | GET | `/portal/meters/{meter_id}/geo` |

More detailed reverse-engineering notes are documented in:

```text
PROTOCOL.md
```

The protocol documentation covers:

- Authentication
- Session handling
- Meter search
- Energy data
- Geo data
- Meter hierarchy
- Response formats
- Error behavior
- Reverse-engineering approach
- Security considerations
- Known limitations

---

## 13. Authentication and Session Management

The portal uses a SvelteKit form action for login.

The wrapper sends credentials to:

```http
POST /login
```

using form-encoded data.

A successful login returns a redirect-style JSON response and establishes an authenticated session cookie.

The wrapper stores the session inside a reusable HTTPX client.

The flow is:

```text
API request
     │
     ▼
PortalClient
     │
     ├── Session exists ──► Upstream request
     │
     └── No session ──────► Login
                              │
                              ▼
                         Store session
                              │
                              ▼
                       Upstream request
```

If an upstream request returns `401`, the client:

1. Marks the session as unauthenticated.
2. Logs in again.
3. Retries the original request once.

Passwords and session tokens are never returned through the public API.

---

## 14. Response Normalization

The legacy portal was designed primarily for its frontend, so some response fields are not ideal for an external API.

The wrapper normalizes these responses.

Examples:

```text
meterId       → meter_id
serialNo      → serial_number
phaseType     → phase_type
installStatus → installation_status
dtCode        → distribution_transformer
```

Numeric strings are converted into numeric values:

```text
"kwh": "6850.32"
        ↓
"kwh": 6850.32
```

Timestamps are converted from:

```text
23/06/2026 23:30
```

to:

```text
2026-06-23T23:30:00
```

This keeps the public API independent of the upstream response representation.

---

## 15. Error Handling

The API uses standard HTTP status codes for common failure scenarios.

| Situation | Status |
|---|---:|
| Successful request | `200` |
| Invalid request parameters | `422` |
| Meter not found | `404` |
| Upstream service failure | `502` |

For example, an invalid page:

```http
GET /api/v1/meters?page=0
```

returns:

```http
422 Unprocessable Entity
```

An unknown meter:

```http
GET /api/v1/meters/INVALID_ID
```

returns:

```http
404 Not Found
```

Unexpected upstream failures are represented as:

```http
502 Bad Gateway
```

The wrapper intentionally avoids exposing raw upstream exception details to API consumers.

---

## 16. Testing

The project contains both mocked unit tests and a live integration test.

### Run normal tests

```bash
python -m pytest -v -m "not integration"
```

These tests do not require access to the live portal.

They cover:

- API health endpoint
- Meter search
- Meter lookup
- Consumption endpoint
- Location endpoint
- Request validation
- Upstream failure handling
- Portal client authentication
- Portal client requests
- Login failure handling

### Run the live integration test

```bash
python -m pytest -v -m integration
```

The integration test uses the credentials configured in `.env` and verifies connectivity with the actual portal.

It checks:

- Portal login
- Meter search
- Energy endpoint
- Geo endpoint

The integration test is intentionally separated from the normal test suite because it depends on external credentials and network availability.

---

## 17. Reverse-Engineering Approach

The portal was investigated using browser developer tools and network inspection.

The investigation process was:

1. Open the portal.
2. Authenticate through the normal login flow.
3. Inspect network requests generated by the UI.
4. Identify the meter search request.
5. Observe the live/as-you-type search behavior.
6. Open an individual meter.
7. Identify the energy endpoint.
8. Identify the geo endpoint.
9. Inspect the response structures.
10. Reproduce the requests independently using HTTPX.
11. Implement a dedicated upstream client.
12. Normalize the responses into typed Pydantic models.

The implementation intentionally uses direct JSON endpoints instead of scraping HTML.

This makes the wrapper simpler and less dependent on the frontend's rendered structure.

---

## 18. Design Decisions

### Separate API, service, and portal layers

The application follows:

```text
API Layer
    ↓
Service Layer
    ↓
Portal Client
    ↓
Legacy Portal
```

This keeps the legacy protocol isolated from the public API.

### Pydantic response models

Pydantic models provide a stable and documented API contract.

They also ensure that numeric fields and response structures are validated.

### Shared HTTP session

A reusable HTTPX client is used instead of creating a new HTTP client for every request.

This allows the authentication session to be reused.

### Re-authentication on 401

The upstream session can expire.

The client therefore re-authenticates once when an upstream request returns `401`.

### Direct JSON APIs instead of HTML scraping

The portal already exposes JSON endpoints used by its frontend.

Using those endpoints is more reliable than parsing rendered HTML.

### No database

A database was intentionally not introduced because this assignment focuses on building a REST wrapper around the existing portal.

---

## 19. Trade-offs

### No persistent storage

The wrapper retrieves data from the upstream portal on demand.

**Advantage:**

- Simple architecture
- No synchronization process
- Data comes directly from the source system

**Trade-off:**

- API availability depends on the upstream portal
- No historical storage
- No offline access

### Limited API surface

Only the required/core meter operations are exposed.

**Advantage:**

- Small and focused API
- Less unnecessary coupling to the portal

**Trade-off:**

- Some information visible in the portal, such as the full network hierarchy, is not exposed

### Broad upstream exception handling

The current API translates unexpected upstream exceptions into `502 Bad Gateway`.

**Advantage:**

- Prevents implementation details from leaking
- Simple failure contract

**Trade-off:**

- A production implementation could distinguish between more upstream failure types

### No API authentication

The assignment did not require authentication for consumers of the wrapper.

**Trade-off:**

For a production deployment, consumer authentication and authorization would be required.

---

## 20. Security Considerations

Credentials are supplied through environment variables.

They are not hardcoded into application source code.

The `.env` file is ignored by Git.

Sensitive values such as:

- passwords
- session cookies
- authentication tokens

are not returned by the API.

The application should also be deployed behind appropriate HTTPS, access controls, and secret-management infrastructure in a production environment.

---

## 21. Assumptions

The implementation makes the following assumptions:

1. The discovered JSON endpoints are the intended interfaces used by the portal frontend.
2. The portal authentication flow remains compatible with the observed SvelteKit login behavior.
3. Meter IDs returned by the search endpoint can be used with the energy and geo endpoints.
4. The upstream energy timestamp format remains `DD/MM/YYYY HH:mm`.
5. The upstream numeric fields remain parseable as numbers.
6. The portal remains reachable using the configured credentials.
7. The upstream portal remains the source of truth for the returned data.

---

## 22. Known Limitations

The following were intentionally not implemented:

- Persistent database/storage
- Background data synchronization
- Caching
- Rate limiting
- Consumer authentication/authorization
- Complete meter network hierarchy
- Advanced filtering
- Advanced sorting
- Production-grade metrics
- Distributed tracing
- Historical data persistence

The service currently operates as a synchronous, on-demand wrapper around the upstream portal.

---

## 23. Future Improvements

If this were developed further for production, I would consider:

### Reliability

- Retry policies with exponential backoff
- Circuit breaker around the upstream portal
- More granular upstream error mapping
- Configurable timeouts

### Performance

- Redis caching
- Connection pooling improvements
- Cached meter metadata
- Background synchronization

### Observability

- Structured logging
- Request IDs
- Metrics
- Distributed tracing
- Upstream latency monitoring

### Security

- API authentication
- Role-based authorization
- Managed secret storage
- Request rate limiting
- Security headers

### Data

- Persistent meter database
- Historical consumption storage
- Full network hierarchy
- Query/filter capabilities

---

## 24. Deliverables

This repository contains the requested assignment artifacts:

```text
Source code
README.md
PROTOCOL.md
openapi.json
Tests
```

### Repository

https://github.com/sumanthvardhinedi/urja-meter-api

---

## 25. Reflection

### What assumptions did you make?

I assumed that the JSON endpoints observed through the portal's network activity were the appropriate interfaces to wrap.

I also assumed that the observed authentication and response formats would remain stable during the assignment evaluation.

### What was the hardest part?

The most challenging part was understanding the portal's authentication behavior.

A successful login returns HTTP 200 even though the response represents a redirect, while failed authentication can also return HTTP 200 with a failure object.

Therefore, checking only the HTTP status code would be incorrect.

Network inspection and reproducing the browser requests were important for understanding this behavior.

### If you had another day, what would you improve?

I would add:

- Persistent storage
- Caching
- More detailed upstream error handling
- Structured logging
- Metrics
- API authentication
- More complete meter hierarchy support
- Stronger integration testing

### What mistake did you make?

An early implementation treated HTTP 200 as sufficient evidence that login had succeeded.

After inspecting the actual response body, I changed the implementation to check the SvelteKit response type and explicitly detect authentication failure.

Another debugging mistake was printing sensitive authentication/session information during development. That output was removed, and credentials and session tokens are not included in the repository.

### What would you critique about your implementation?

The implementation is intentionally scoped to the assignment rather than being a complete production platform.

The main areas I would improve are persistence, caching, observability, consumer authentication, and more granular upstream error handling.

The current architecture nevertheless keeps the legacy portal integration isolated and provides a clean REST contract for the required operations.

---

## 26. Quick Start

For convenience:

```bash
git clone https://github.com/sumanthvardhinedi/urja-meter-api.git
cd urja-meter-api

python -m venv .venv
```

Activate the environment and install dependencies:

```bash
pip install -r requirements.txt
```

Configure:

```env
URJA_BASE_URL=https://urja-ops.flockenergy.tech
URJA_USERNAME=<your-username>
URJA_PASSWORD=<your-password>
```

Run:

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

The API is ready to use.