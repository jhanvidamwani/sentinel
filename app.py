import pandas as pd
import streamlit as st

from pipeline import detector_agent, analyst_agent
from replay_data import ASSETS, BERYL, TAIWAN

st.set_page_config(page_title="Sentinel", layout="wide")
st.title("Sentinel")
st.caption("The Detector finds and scores events. The Analyst works out what is exposed and what to do. Asset values are made up.")

scenarios = {"Hurricane Beryl, Houston (July 2024)": BERYL, "Hualien earthquake, Taiwan (April 2024)": TAIWAN}
choice = st.sidebar.selectbox("Replay", list(scenarios))
use_llm = st.sidebar.toggle("Let Claude write the briefs", value=False)
signals = sorted(scenarios[choice], key=lambda s: s.time)

count = st.slider("Signals received", 1, len(signals), 1)
seen = signals[:count]

left, right = st.columns(2)

with left:
    st.subheader("Detector")
    for s in seen:
        st.markdown(f"**{s.source.upper()}**, {s.time[:16].replace('T', ' ')} UTC  \n{s.title}")
    events = detector_agent(seen)
    st.metric("Events open", len(events))

with right:
    st.subheader("Analyst")
    if not events:
        st.info("Nothing confirmed yet. News on its own does not open an event.")
    for event in events:
        alert = analyst_agent(event, ASSETS, use_llm)
        color = {"CRITICAL": "red", "WARNING": "orange", "WATCH": "blue"}[alert["tier"]]
        st.markdown(f"### :{color}[{alert['tier']}] {alert['peril'].title()}, score {alert['score']['score']}")

        loss = alert["loss_estimate"]
        a, b, c = st.columns(3)
        a.metric("Severity", f"{alert['score']['severity']} of 5")
        b.metric("Confidence", f"{alert['score']['confidence']:.0%}")
        c.metric("Estimated loss", f"${loss['mid_musd']:,.0f}M", help=f"${loss['low_musd']:,.0f}M to ${loss['high_musd']:,.0f}M")

        st.write("**Exposed:**", ", ".join(alert["exposed_assets"]) or "nothing yet")
        st.write("**What happens next:**")
        for step in alert["cascade"]:
            st.write(step)

        health, wealth, insurance, why = st.tabs(["Health", "Wealth", "Insurance", "Why this score"])
        for tab, key in [(health, "health"), (wealth, "wealth"), (insurance, "insurance")]:
            tab.markdown("\n".join(f"* {line}" for line in alert["briefs"][key]))
        why.write(alert["score"]["rationale"])
        why.dataframe(pd.DataFrame(alert["sources"]))
        st.caption(f"Send to: {', '.join(alert['route_to'])}. {alert['caveat']}")

points = [{"lat": s.lat, "lon": s.lon, "color": "#b3261e", "size": 30000} for s in seen]
points += [{"lat": a["lat"], "lon": a["lon"], "color": "#1c2394", "size": 15000} for a in ASSETS]
st.map(pd.DataFrame(points), color="color", size="size")
