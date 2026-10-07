# Urja Meter Ops Protocol Notes

## 1. Overview

The upstream system is a SvelteKit-based web portal used for meter operations.

Portal:

https://urja-ops.flockenergy.tech

The goal of the investigation was to identify the network requests used by the web application and determine which endpoints could be consumed by a clean REST API wrapper.

The investigation was performed using the browser's developer tools and network inspection.

The implementation uses the discovered JSON endpoints rather than scraping rendered HTML.

---

## 2. Authentication

### Login endpoint

```http
POST /login
```

The portal uses a SvelteKit form action for authentication.

The request is sent as:

```http
Content-Type: application/x-www-form-urlencoded
Accept: application/json
X-SvelteKit-Action: true
Origin: https://urja-ops.flockenergy.tech
Referer: https://urja-ops.flockenergy.tech/login
```

The form fields are:

```text
email=<username>
password=<password>
```

A successful login does not return a conventional JSON success response. Instead, the response body indicates a redirect:

```json
{
  "type": "redirect",
  "status": 303,
  "location": "/meters"
}
```

The response also establishes an authenticated session cookie:

```text
__Secure-better-auth.session_token
```

An unsuccessful login can still return HTTP 200. The failure is represented in the response body:

```json
{
  "type": "failure",
  "status": 401
}
```

Therefore, the wrapper checks the response body instead of relying only on the HTTP status code.

The authenticated HTTP session is reused for subsequent upstream requests.

The observed session lifetime is approximately one hour. If an upstream request returns HTTP 401, the wrapper re-authenticates once and retries the request.

Credentials and session tokens are never returned by the public API.

---

## 3. Meter Search

### Endpoint

```http
GET /portal/meters/search?q={query}&page={page}
```

The portal uses this endpoint for meter search and pagination.

Example:

```http
GET /portal/meters/search?q=J100002&page=1
```

Observed response:

```json
{
  "data": [
    {
      "meterId": "J100002",
      "serialNo": "AL28136",
      "make": "L&T",
      "phaseType": "single",
      "installStatus": "Installed",
      "dtCode": "DT-003"
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 20
}
```

The portal contained approximately 403 meters at the time of investigation, with approximately 20 meters displayed per page.

The search endpoint is also used for as-you-type searching. Network requests were observed for progressively entered values such as:

```text
J
J1
J10
J1000
J100002
```

The wrapper exposes this functionality through:

```http
GET /api/v1/meters?search=J100002&page=1
```

The wrapper normalizes the upstream field names into the public API model.

---

## 4. Energy / Consumption

### Endpoint

```http
GET /portal/meters/{meter_id}/energy
```

Example:

```http
GET /portal/meters/J100002/energy
```

Observed response:

```json
{
  "data": [
    {
      "timestamp": "23/06/2026 23:30",
      "kwh": "6850.32",
      "kvah": "7398.35",
      "voltR": "227"
    }
  ]
}
```

The upstream API returns numeric measurements as strings.

Observed timestamps use the format:

```text
DD/MM/YYYY HH:mm
```

The observed energy readings were at 30-minute intervals.

The wrapper converts:

- `kwh` to `float`
- `kvah` to `float`
- `voltR` to `float`
- the upstream timestamp to ISO-8601 format

The public API exposes this through:

```http
GET /api/v1/meters/{meter_id}/consumption
```

Example normalized response:

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

---

## 5. Geo / Location

### Endpoint

```http
GET /portal/meters/{meter_id}/geo
```

Example:

```http
GET /portal/meters/J100002/geo
```

Observed response:

```json
{
  "data": {
    "latitude": "26.840224163401967",
    "longitude": "75.71461868999545"
  }
}
```

The upstream API returns latitude and longitude as strings.

The wrapper converts both values to floating-point numbers.

The public API exposes this through:

```http
GET /api/v1/meters/{meter_id}/location
```

Example normalized response:

```json
{
  "meter_id": "J100002",
  "latitude": 26.840224163401967,
  "longitude": 75.71461868999545
}
```

---

## 6. Meter Detail and Hierarchy

The portal exposes an individual meter page at:

```http
/meter/{meter_id}
```

The actual observed route is:

```http
/meters/{meter_id}
```

The meter detail UI displays meter metadata and network hierarchy information.

The observed hierarchy included:

```text
Zone
  └── Circle
      └── Division
          └── Subdivision
              └── Substation
                  └── Feeder
                      └── Distribution Transformer
```

For the investigated meter, an example hierarchy was:

```text
Jaipur Zone 3 (Z-03)
  → Circle 3 (C-03)
  → Division 3 (D-03)
  → Subdivision 3 (SD-03)
  → Substation 3 (SS-03)
  → Feeder 3 (F-003)
  → Vaishali DT 3 (DT-003)
```

The SvelteKit application also uses internal page-data requests such as:

```http
/meters/{meter_id}/__data.json
```

The implementation intentionally does not depend on this internal page-data endpoint when an explicit JSON API endpoint is available.

The current public API focuses on the core meter metadata, consumption, and location requirements rather than exposing the complete network hierarchy.

---

## 7. Upstream Endpoints Used by the Wrapper

The implementation relies on the following upstream endpoints:

| Purpose | Method | Endpoint |
|---|---|---|
| Authentication | POST | `/login` |
| Meter search | GET | `/portal/meters/search` |
| Energy readings | GET | `/portal/meters/{meter_id}/energy` |
| Location | GET | `/portal/meters/{meter_id}/geo` |

These endpoints were selected because they are direct JSON/network interfaces used by the portal.

The wrapper does not scrape HTML pages for the core API functionality.

---

## 8. Response Normalization

The upstream API is primarily designed for consumption by the portal UI rather than external API clients.

The wrapper therefore normalizes several upstream characteristics.

### Field names

Upstream camelCase fields are converted into snake_case public API fields.

Examples:

```text
meterId       → meter_id
serialNo      → serial_number
phaseType     → phase_type
installStatus → installation_status
dtCode        → distribution_transformer
```

### Numeric values

The upstream energy and geo APIs return numeric values as strings.

The wrapper converts these to appropriate numeric types.

Examples:

```text
"kwh": "6850.32"       → "kwh": 6850.32
"kvah": "7398.35"     → "kvah": 7398.35
"voltR": "227"        → "voltage_r": 227.0
```

### Timestamps

The upstream timestamp:

```text
23/06/2026 23:30
```

is parsed and returned as:

```text
2026-06-23T23:30:00
```

### Response models

Pydantic models are used to provide a stable response contract for API consumers.

---

## 9. Error Handling

The wrapper distinguishes between client validation errors and upstream failures.

### Request validation

FastAPI validates API parameters before the request reaches the service layer.

Examples include:

```text
page < 1
meter_id is empty
meter_id exceeds the allowed length
```

Invalid parameters return:

```http
422 Unprocessable Entity
```

### Meter not found

If a requested meter cannot be found through the upstream search endpoint, the wrapper returns:

```http
404 Not Found
```

Example:

```json
{
  "detail": "Meter 'INVALID_ID' not found"
}
```

### Upstream failures

Unexpected failures while communicating with the portal are translated into:

```http
502 Bad Gateway
```

Example:

```json
{
  "detail": "Failed to retrieve meter from upstream portal"
}
```

This prevents raw upstream implementation details from leaking through the public API.

---

## 10. Reverse-Engineering Approach

The portal was investigated through browser developer tools and network inspection.

The main steps were:

1. Open the portal and authenticate normally.
2. Inspect network requests generated by the UI.
3. Identify requests made when loading the meter list.
4. Identify requests made while searching for a meter.
5. Inspect requests made when opening an individual meter.
6. Inspect requests made for energy data.
7. Inspect requests made for geographic data.
8. Reproduce the requests outside the browser.
9. Verify the response structures and field types.
10. Implement the smallest stable wrapper around the discovered JSON endpoints.

The investigation focused on network requests rather than reverse-engineering the frontend implementation itself.

The goal was to identify stable HTTP interfaces that could be consumed independently of the SvelteKit UI.

---

## 11. Security Considerations

Credentials are loaded from environment variables rather than being hardcoded in source code.

Example configuration:

```env
URJA_BASE_URL=https://urja-ops.flockenergy.tech
URJA_USERNAME=<username>
URJA_PASSWORD=<password>
```

The `.env` file is excluded from Git using `.gitignore`.

Credentials are not included in the repository.

Session tokens are kept inside the authenticated HTTP client session and are not returned by the wrapper API.

The API does not expose the upstream authentication credentials or session cookie.

Debug logging should not print authentication responses, passwords, or session cookies.

---

## 12. Known Limitations

The implementation intentionally focuses on the core assignment requirements.

The following features were not implemented:

- Persistent database/storage
- Background synchronization
- Caching
- Rate limiting
- API authentication for consumers of the wrapper
- Full meter network hierarchy in the public API
- Advanced filtering and sorting
- Production-grade observability and metrics
- Automatic historical data persistence

The wrapper currently retrieves data from the upstream portal on demand.

The upstream portal remains the source of truth.

A production implementation could add:

- Redis or another caching layer
- Persistent storage
- Background synchronization jobs
- Structured logging
- Metrics and tracing
- Retry policies with exponential backoff
- API authentication and authorization
- More detailed domain models
- Stronger handling of upstream-specific error types

---

## 13. Design Decisions

The implementation separates responsibilities into three main layers:

```text
API Layer
    ↓
Service Layer
    ↓
Portal Client
    ↓
Urja Meter Ops Portal
```

### API layer

The API layer is responsible for:

- HTTP routing
- Query/path parameter validation
- HTTP status codes
- Public response models
- Translating service errors into API errors

### Service layer

The service layer is responsible for:

- Business-level transformations
- Mapping upstream fields to public models
- Converting numeric strings to numeric values
- Parsing timestamps
- Combining upstream data into stable API responses

### Portal client

The portal client is responsible for:

- Authentication
- Session management
- Calling upstream endpoints
- Handling session expiry
- Retrying authentication once after a 401 response

This separation keeps legacy portal protocol details isolated from the public REST API.

---

## 14. Trade-offs

### Direct upstream calls

The wrapper makes requests to the portal on demand instead of maintaining a local copy of the data.

**Advantage:**

The API returns current upstream data without requiring a synchronization pipeline.

**Trade-off:**

Availability and latency depend on the upstream portal.

### No database

A database was intentionally not introduced because the assignment primarily requires a REST wrapper over an existing system.

**Advantage:**

Less infrastructure and simpler deployment.

**Trade-off:**

There is no historical storage, caching, or offline access.

### Limited public API surface

Only the core required operations are exposed.

**Advantage:**

The API remains small and focused.

**Trade-off:**

Some information visible in the portal, such as the full network hierarchy, is not currently exposed.

### Reusing the authenticated HTTP session

The portal client maintains a reusable HTTP session.

**Advantage:**

Avoids logging in for every API request and keeps authentication logic centralized.

**Trade-off:**

The application must handle session expiry and re-authentication correctly.

---

## 15. Summary

The reverse-engineering work identified the portal's authentication flow and the JSON endpoints required for meter search, energy data, and geographic data.

The final wrapper exposes these capabilities through a cleaner REST API:

```text
GET /api/v1/meters
GET /api/v1/meters/{meter_id}
GET /api/v1/meters/{meter_id}/consumption
GET /api/v1/meters/{meter_id}/location
```

The implementation keeps the legacy portal protocol isolated behind a dedicated client and provides normalized, documented API responses for consumers.