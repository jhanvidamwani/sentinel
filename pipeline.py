from dataclasses import asdict

from detector import triage, correlate, score
from analyst import exposure, loss_estimate, write_briefs, build_alert, CASCADE


def detector_agent(signals):
    return correlate(triage(signals))


def analyst_agent(event, assets, use_llm=False):
    hits = exposure(event, assets)
    result = score(event, hits)
    loss = loss_estimate(hits, result["severity"])
    packet = {
        "kind": event.kind,
        "score": result,
        "loss": loss,
        "exposed_assets": hits,
        "cascade": CASCADE.get(event.kind, []),
        "signals": [asdict(s) for s in event.signals],
    }
    return build_alert(event, hits, result, loss, write_briefs(packet, use_llm))


def run_pipeline(signals, assets, use_llm=False):
    return [analyst_agent(event, assets, use_llm) for event in detector_agent(signals)]
