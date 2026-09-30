import json
from datetime import datetime, timezone

from schemas import km_between

DAMAGE_RATIO = {
    0: (0.00, 0.01, 0.02), 1: (0.01, 0.02, 0.05), 2: (0.02, 0.05, 0.10),
    3: (0.05, 0.10, 0.20), 4: (0.10, 0.20, 0.35), 5: (0.20, 0.35, 0.60),
}
DOWNTIME_DAYS = {0: (0, 1, 2), 1: (1, 2, 4), 2: (2, 5, 10), 3: (5, 10, 21), 4: (10, 21, 45), 5: (21, 45, 90)}

CASCADE = {
    "hurricane": [
        "Refineries and LNG terminals shut, fuel and gas prices jump",
        "Grid damage leaves the metro area without power",
        "Data centers run on generators and need fuel",
        "Cloud clients lose business while data centers are down",
    ],
    "earthquake": [
        "Chip fabs evacuate and scrap wafers in progress",
        "Chip output drops while lines restart",
        "Electronics makers downstream run short of parts",
    ],
}

ROUTING = {
    "CRITICAL": ["Chief Risk Officer", "Cat claims team", "Energy and tech underwriting", "Affected clients"],
    "WARNING": ["Cat claims team", "Energy and tech underwriting"],
    "WATCH": ["Risk analyst on duty"],
}

CAVEAT = "Early estimate from public signals, not a claims forecast. Confidence reflects how well the sources agree."

BRIEF_PROMPT = """You are a catastrophe analyst at a commercial insurer.
Here is the event data as JSON: {event_json}

Write three short briefs of three or four points each, in plain language.
Health: who is exposed and how hospitals and emergency services will cope.
Wealth: which markets, sectors, tickers or commodities will move, and which way.
Insurance: which lines of business are hit, the loss range given, and what it means for reserves.
Use only facts from the data. If something is not in the data, say it is unknown.
Reply with JSON using the keys health, wealth and insurance, each a list of strings."""


def exposure(event, assets):
    radius = {"hurricane": 250, "earthquake": 150}.get(event.kind, 100)
    hits = []
    for a in assets:
        d = km_between(event.lat, event.lon, a["lat"], a["lon"])
        if d <= radius:
            hits.append({**a, "distance_km": round(d), "decay": round((1 - d / radius) ** 2, 3)})
    return hits


def loss_estimate(hits, severity):
    band = int(round(severity))
    low_mid_high = []
    for i in range(3):
        damage = sum(h["tiv_musd"] * DAMAGE_RATIO[band][i] * h["decay"] for h in hits)
        downtime = sum(h["daily_rev_musd"] * DOWNTIME_DAYS[band][i] * h["decay"] for h in hits)
        low_mid_high.append(round(damage + downtime, 1))
    return dict(zip(["low_musd", "mid_musd", "high_musd"], low_mid_high))


def write_briefs(packet, use_llm=False, model="claude-sonnet-5"):
    if use_llm:
        import anthropic
        reply = anthropic.Anthropic().messages.create(
            model=model,
            max_tokens=1200,
            messages=[{"role": "user", "content": BRIEF_PROMPT.format(event_json=json.dumps(packet))}],
        )
        text = reply.content[0].text
        return json.loads(text[text.find("{"): text.rfind("}") + 1])

    sectors = sorted({h["sector"] for h in packet["exposed_assets"]})
    loss = packet["loss"]
    return {
        "health": [f"People near the {packet['kind']} are exposed. Watch hospital power and evacuation capacity."],
        "wealth": [
            f"Sectors in the path: {', '.join(sectors) or 'none'}.",
            "Watch XLE, natural gas and crude futures, SOXX, and data center REITs like EQIX and DLR.",
        ],
        "insurance": [
            f"Estimated insured loss of {loss['low_musd']} to {loss['high_musd']} million dollars, around {loss['mid_musd']} million.",
            "Lines hit: commercial property, business interruption, contingent business interruption and energy.",
            "Flag for an early IBNR review. The range comes from the model, not from claims.",
        ],
    }


def build_alert(event, hits, score, loss, briefs):
    return {
        "alert_id": event.id,
        "tier": score["tier"],
        "peril": event.kind,
        "location": [event.lat, event.lon],
        "horizon": score["horizon"],
        "score": score,
        "loss_estimate": loss,
        "exposed_assets": [h["name"] for h in hits],
        "cascade": CASCADE.get(event.kind, []),
        "briefs": briefs,
        "route_to": ROUTING[score["tier"]],
        "sources": [{"source": s.source, "title": s.title, "url": s.url, "time": s.time} for s in event.signals],
        "caveat": CAVEAT,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
