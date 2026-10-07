# Urja Meter Ops Protocol Notes

## 1. Overview

The upstream system is a SvelteKit-based web portal used for
meter operations.

Portal:

https://urja-ops.flockenergy.tech

The goal of the investigation was to identify the network
requests used by the web application and determine which
endpoints could be consumed by a clean API wrapper.

The investigation was performed using the browser's developer
tools and network inspection.

---

## 2. Authentication

### Login endpoint

```http
POST /login