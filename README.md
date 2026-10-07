# Urja Meter API

A clean REST API wrapper around the legacy **Urja Meter Ops** web portal.

The project reverse-engineers the portal's network APIs and exposes a simpler,
typed, documented API for retrieving meter information, consumption data, and
geographic location.

---

## 1. Overview

The upstream system is a SvelteKit-based web portal used for meter operations.

Instead of exposing the legacy portal directly to consumers, this service
provides a small, stable REST API over the portal's existing JSON endpoints.

### High-level architecture

```text
                    ┌──────────────────────┐
                    │      API Consumer    │
                    └──────────┬───────────┘
                               │
                               │ HTTP
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI API     │
                    │                      │
                    │  /api/v1/meters      │
                    │  /consumption        │
                    │  /location           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    MeterService      │
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
                    │  Urja Meter Ops      │
                    │  Legacy Portal       │
                    └──────────────────────┘
```