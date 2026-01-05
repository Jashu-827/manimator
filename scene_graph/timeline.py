def build_timeline(events):
    timeline = []

    for e in events:
        timeline.append({
            "time_range": f"{e['start']} → {e['end']}",
            "action": f"{e['type']}({e['target']})"
        })

    return timeline
