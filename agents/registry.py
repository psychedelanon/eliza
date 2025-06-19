"""
Runtime map of agent‑name → live instance.
run.py registers the object after construction so SwarmCoordinator
can summon them for cross‑engagement.
"""
LIVE_AGENTS: dict[str, "TwitterAgent"] = {} 