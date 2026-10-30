# Real-Time College Bus Tracking Platform

> A multi-role Django platform for live college-bus tracking. Drivers stream GPS from a React Native app, the backend broadcasts each position over **Django Channels WebSockets**, and students and admins watch buses move on a live map.

[![Live](https://img.shields.io/badge/Live-Render-46E3B7?logo=render&logoColor=black)](https://college-bus-tracking-system-ri73.onrender.com)
[![Demo](https://img.shields.io/badge/Demo-YouTube-FF0000?logo=youtube&logoColor=white)](https://youtu.be/i2Xq8YOuVXY)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](#)
[![Channels](https://img.shields.io/badge/Django_Channels-4.1-0C4B33)](#)
[![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)](#)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](#)

**🔗 Live app:** https://college-bus-tracking-system-ri73.onrender.com (independently deployed on Render's free tier, so the first request may take ~1 min to wake the server)<br/>
**🎬 Demo video:** https://youtu.be/i2Xq8YOuVXY<br/>
**📱 Driver app:** [karrisubhash/Bus-Driver-Application](https://github.com/karrisubhash/Bus-Driver-Application)

---

## Problem

Students at our college had no way of knowing where their bus was. They waited at stops without any idea of arrival times, and the transport office couldn't see which buses were running, delayed or broken down.

## Key features

- **Three roles in one custom `User` model** (admin, driver, student), each with its own login and views.
- **JWT authentication** (SimpleJWT) for the mobile driver app, with a custom token serializer that carries the user's role.
- **Trip lifecycle**: a driver claims a trip, streams location pings, reports or resolves issues, and ends the trip.
- **Live updates over WebSockets**: every accepted ping is fanned out through a Redis channel layer to the `bus_locations` group at `ws/bus/`.
- **GPS noise filter** (geodesic distance via `geopy`) and periodic pruning of pings older than 3 hours.
- **Student view**: `GET /api/student/my-bus/` returns the bus on the student's assigned route.
- **Admin dashboard**: live map, ongoing and completed trips, issue tracking, and a Jazzmin-themed Django admin.

## Architecture

```mermaid
flowchart LR
    DA[React Native<br/>Driver App] -- "JWT · POST /api/trips/{id}/pings/ every 5 s" --> API[Django + DRF]
    API --> PG[(PostgreSQL<br/>Trip · LocationPing · BusCurrentLocation)]
    API -- group_send --> RL[(Redis<br/>channel layer)]
    RL --> WS[Channels consumer<br/>ws/bus/]
    WS -- live JSON --> ST[Student live map]
    WS -- live JSON --> AD[Admin live map / dashboard]
```

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2, Django REST Framework, SimpleJWT |
| Real time | Django Channels 4, channels-redis, Daphne (ASGI) |
| Data | PostgreSQL (`dj-database-url`, SSL), Redis |
| Geo | geopy (geodesic distance) |
| Admin UI | django-jazzmin |
| Static | WhiteNoise |
| Deployment | Render |
| Mobile | React Native ([driver app](https://github.com/karrisubhash/Bus-Driver-Application)) |

## Project structure

```
bus_tracker/
├── bus_tracker/        # settings, ASGI (HTTP + WebSocket router), URLs
├── core/
│   ├── models.py       # User(role), Bus, Route, Trip, LocationPing, BusCurrentLocation
│   ├── views.py        # REST endpoints (trips, pings, issues, admin feeds)
│   ├── consumers.py    # BusLocationConsumer (WebSocket)
│   ├── routing.py      # ws/bus/
│   └── serializers.py
├── templates/          # admin_* and student_* pages (live map, tables, login)
├── Procfile
└── requirements.txt
```

## Getting started

```bash
git clone https://github.com/karrisubhash/bus_tracker.git
cd bus_tracker
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL=postgres://user:pass@host:5432/bus   # PostgreSQL (SSL required)
export REDIS_URL=redis://localhost:6379
python manage.py migrate
python manage.py createsuperuser
daphne -b 0.0.0.0 -p 8000 bus_tracker.asgi:application    # ASGI, so WebSockets work
```

### Environment variables

| Variable | Example | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgres://user:pass@host:5432/bus` | PostgreSQL (SSL required) |
| `REDIS_URL` | `redis://localhost:6379` | Channel layer |

## API

All endpoints are under `/api/`. Authenticate with `Authorization: Bearer <access token>`.

| Method | Endpoint | Role | Purpose |
|---|---|---|---|
| POST | `/token/`, `/token/refresh/` | any | Obtain / refresh JWT |
| GET | `/trips/` | authenticated | List trips |
| POST | `/trips/{id}/claim/` | driver | Claim a trip |
| POST | `/trips/{id}/pings/` | driver (trip owner) | Send `{lat, lon}`; broadcast over WebSocket |
| GET | `/trips/{id}/latest_ping/` | authenticated | Last known position |
| GET | `/trips/{id}/route-path/` | public | Ping history for drawing the route |
| POST | `/trips/{id}/report-issue/`, `/resolve-issue/` | authenticated | Breakdown / delay reporting |
| POST | `/trips/{id}/end/` | driver | End the trip |
| GET | `/student/my-bus/` | student | Bus on the student's route |
| GET | `/admin/trips/`, `/admin/ongoing-trips/`, `/admin/completed-trips/` | admin | Trip feeds |
| GET | `/admin/live-locations/` | public | Current bus positions |

**WebSocket:** `wss://<host>/ws/bus/`. Each message looks like:

```json
{ "trip_id": 12, "lat": 17.7231, "lon": 83.3012, "bus": "AP31XX0000", "driver": "ravi", "route": "Route 4", "has_issue": false }
```


## Testing

```bash
python manage.py test core
```

No tests are written yet (`core/tests.py` is a stub). See *Future improvements*.

## Implementation notes

- Each driver ping is written to PostgreSQL first (`LocationPing` plus an upserted `BusCurrentLocation`). Only after that is it pushed to the channel layer, so a reconnecting client can always fall back to `latest_ping/`.
- The ASGI router in `bus_tracker/asgi.py` serves HTTP and WebSocket from the same process.

## Future improvements

- Run the GPS noise filter on every ping. It currently sits inside the 1-in-10 cleanup branch in `LocationPingCreateView`.
- Authenticate WebSocket connections and scope broadcasts per route instead of one global group.
- Add API and consumer tests (`channels.testing.WebsocketCommunicator`).
- Publish a load-test script and its results for the concurrency and latency figures.
- Compute ETAs from route geometry and recent speed.
