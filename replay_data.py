from schemas import Signal
from pipeline import run_pipeline

# Insured values and daily revenue are made up for the demo.
ASSETS = [
    {"name": "Baytown refinery complex", "sector": "energy", "lat": 29.75, "lon": -95.01, "tiv_musd": 4000, "daily_rev_musd": 25},
    {"name": "Freeport LNG terminal", "sector": "energy", "lat": 28.94, "lon": -95.31, "tiv_musd": 3000, "daily_rev_musd": 12},
    {"name": "Texas City refinery", "sector": "energy", "lat": 29.37, "lon": -94.93, "tiv_musd": 3500, "daily_rev_musd": 20},
    {"name": "Houston West data center", "sector": "tech", "lat": 29.78, "lon": -95.62, "tiv_musd": 800, "daily_rev_musd": 2},
    {"name": "Ashburn data center", "sector": "tech", "lat": 39.04, "lon": -77.49, "tiv_musd": 1500, "daily_rev_musd": 4},
    {"name": "Hsinchu fab cluster", "sector": "tech", "lat": 24.77, "lon": 121.01, "tiv_musd": 20000, "daily_rev_musd": 60},
    {"name": "Taichung fab cluster", "sector": "tech", "lat": 24.21, "lon": 120.62, "tiv_musd": 15000, "daily_rev_musd": 45},
]

BERYL = [
    Signal("gdelt", "news", "Freeport LNG shuts ahead of Beryl", 28.94, -95.31, "2024-07-07T18:00:00Z", 0),
    Signal("nws", "hurricane", "Hurricane warning for Harris County", 29.76, -95.37, "2024-07-07T21:00:00Z", 65),
    Signal("nhc", "hurricane", "Beryl makes landfall near Matagorda, Texas", 28.6, -96.0, "2024-07-08T09:00:00Z", 70),
    Signal("eia", "grid_stress", "Houston grid load collapses as power goes out", 29.76, -95.37, "2024-07-08T15:00:00Z", 0.97),
]

TAIWAN = [
    Signal("usgs", "earthquake", "M7.4 earthquake off Hualien, Taiwan", 23.82, 121.56, "2024-04-02T23:58:00Z", 7.4),
    Signal("gdacs", "earthquake", "GDACS red alert for Taiwan", 23.82, 121.56, "2024-04-03T00:10:00Z", 7.4),
    Signal("gdelt", "news", "台积电 疏散 晶圆厂 (TSMC evacuates fabs)", 24.77, 121.01, "2024-04-03T01:00:00Z", 0, lang="zh"),
]

if __name__ == "__main__":
    for name, signals in [("Hurricane Beryl", BERYL), ("Hualien earthquake", TAIWAN)]:
        for alert in run_pipeline(signals, ASSETS):
            loss = alert["loss_estimate"]
            print(f"{name}: {alert['tier']}, score {alert['score']['score']}")
            print(f"  Loss {loss['low_musd']} to {loss['high_musd']} million")
            print(f"  {alert['score']['rationale']}")
