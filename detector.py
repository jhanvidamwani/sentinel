from schemas import Event, RELIABILITY, km_between, hours_between

THRESHOLDS = {"earthquake": 5.5, "hurricane": 50, "grid_stress": 0.95}


def triage(signals):
    return [s for s in signals if s.kind not in THRESHOLDS or s.intensity >= THRESHOLDS[s.kind]]


def correlate(signals, radius_km=400, window_h=72):
    anchors = sorted((s for s in signals if s.kind != "news"), key=lambda s: -RELIABILITY.get(s.source, 0.5))
    used, events = set(), []
    for a in anchors:
        if a.id in used:
            continue
        group = [
            s for s in signals
            if s.id not in used
            and km_between(a.lat, a.lon, s.lat, s.lon) <= radius_km
            and hours_between(a.time, s.time) <= window_h
        ]
        used.update(s.id for s in group)
        events.append(Event(a.kind, a.lat, a.lon, group))
    return events


def severity(event):
    peak = max(s.intensity for s in event.signals if s.kind == event.kind)
    if event.kind == "hurricane":
        return peak, min(5, max(0, (peak - 50) / 20))
    if event.kind == "earthquake":
        return peak, min(5, max(0, (peak - 5.5) * 2))
    return peak, 2.5


def score(event, hits):
    sources = sorted({s.source for s in event.signals})
    peak, sev = severity(event)

    miss = 1.0
    for src in sources:
        miss *= 1 - RELIABILITY.get(src, 0.5)
    confidence = round(min(0.95, 1 - miss) * min(1, len(sources) / 3), 2)

    sectors = sorted({h["sector"] for h in hits})
    spread = min(5, len(hits) * 0.5 + len(sectors))
    total = round(0.5 * sev + 0.3 * spread + 2 * confidence, 2)
    tier = "CRITICAL" if total >= 4.2 else "WARNING" if total >= 3 else "WATCH"

    reason = (
        f"{len(event.signals)} signals from {len(sources)} sources ({', '.join(sources)}). "
        f"Peak {peak} gives severity {sev:.1f} of 5. "
        f"{len(hits)} insured sites in {' and '.join(sectors) or 'no sector'} give spread {spread:.1f} of 5. "
        f"The sources agree with confidence {confidence}."
    )
    return {
        "severity": round(sev, 1),
        "spread": round(spread, 1),
        "confidence": confidence,
        "horizon": "next 24 hours" if event.kind == "earthquake" else "next 72 hours",
        "score": total,
        "tier": tier,
        "rationale": reason,
    }
