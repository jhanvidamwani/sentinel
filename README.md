# Sentinel

Built by Jhanvi Damwani and Amrit Chhabda for the Chubb challenge at the Stevens Business AI Hackathon.

When a hurricane or an earthquake starts to build, the signs show up in public data long before the claims do. The hard part for an underwriter is not seeing the storm. It is working out which of their policies sit in its path, what to do first, and whether to keep writing new business. Sentinel does that work for them.

![Sentinel dashboard](demo/dashboard-screenshot.png)

## What is in here

The dashboard folder holds index.html, which is the demo we presented. Open it in any browser. It needs no install and works offline. Press Replay to watch two real events from 2024 unfold, or click any signal on the timeline to jump to that moment.

The agents folder holds the Python version of the two agents, plus a small Streamlit app that shows the same thing.

The demo folder has a short screen recording of the dashboard and a screenshot of it.

The docs folder has our build notes, with the reasoning behind the scoring and the loss numbers.

The slides folder has the presentation as a PowerPoint file.

## How it works

There are two agents, and one passes its work to the other.

The Detector reads public feeds: USGS for earthquakes, NOAA and the National Weather Service for storms, GDACS for global disaster alerts, EIA for the power grid, and GDELT for news in many languages. It throws out anything too small to matter, groups signals that happen close together in place and time, and scores each event. The score comes from plain rules, not from a language model, so anyone can check how it was reached. A news story on its own never opens an event. Confidence only goes up when independent sources agree.

The Analyst takes each event and checks which insured sites fall inside its footprint. It estimates the loss as a low, middle and high range, and ranks what the desk should do first across every active event. Each action gets an owner and a deadline. It also looks at new submissions waiting for a quote and says whether to write them, write them with changes, or hold off. Claude is only used to write the short health, markets and claims notes. It never sets a score.

## How the risk score works

Every event gets a score built from three parts.

Severity, from 0 to 5, is how strong the event is. For an earthquake it is the magnitude above 5.5, doubled. For a hurricane it is the wind speed above 50 knots, divided by 20.

Spread, from 0 to 5, is how much of our book it touches. Each insured site in the path adds half a point and each sector hit adds one.

Confidence, up to 0.95, is how sure we are the event is real. Every source has a reliability weight, and confidence only reaches the top when at least three independent sources agree.

The score is 0.5 times severity, plus 0.3 times spread, plus 2 times confidence. The highest score is handled first. The weights are a starting point we chose by judgment. With real loss history they would be fitted by backtesting past events.

## Running the Python version

    cd agents
    pip install -r requirements.txt
    python replay_data.py
    streamlit run app.py

The first command prints both replays in the terminal. The second opens the app in your browser. If you want Claude to write the notes, put your Anthropic key in a file called .env using .env.example as a guide, then switch it on in the app's sidebar. Without a key, the app writes simple notes on its own.

## What is real and what is not

The two event timelines are real. The Hualien earthquake hit Taiwan on 3 April 2024 and TSMC evacuated its fabs. Hurricane Beryl came ashore in Texas on 8 July 2024 and knocked out power across Houston.

The insured values, the book of business, the three clients waiting for quotes and the policy terms are made up for the demo. The Chubb numbers we quote, such as the 1 in 100 year loss estimates, the 1.47 billion dollar wildfire loss and the combined ratios, come from Chubb's 2025 annual report and 10K filing.
