from dataclasses import dataclass, field
from datetime import datetime
from math import radians, sin, cos, asin, sqrt
import uuid


@dataclass
class Signal:
    source: str
    kind: str
    title: str
    lat: float
    lon: float
    time: str
    intensity: float
    url: str = ""
    lang: str = "en"
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])


@dataclass
class Event:
    kind: str
    lat: float
    lon: float
    signals: list
    id: str = field(default_factory=lambda: "EVT" + uuid.uuid4().hex[:6].upper())


RELIABILITY = {"usgs": 0.95, "nhc": 0.95, "nws": 0.9, "gdacs": 0.85, "eia": 0.9, "gdelt": 0.5}


def km_between(lat1, lon1, lat2, lon2):
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 6371 * 2 * asin(sqrt(a))


def hours_between(t1, t2):
    parse = lambda t: datetime.fromisoformat(t.replace("Z", "+00:00"))
    return abs((parse(t1) - parse(t2)).total_seconds()) / 3600
