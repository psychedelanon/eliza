"""
Runtime map of agent‑name → live instance.
run.py registers the object after construction so SwarmCoordinator
can summon them for cross‑engagement.
"""
LIVE_AGENTS: dict[str, "TwitterAgent"] = {}

# Agent class mapping for dynamic loading
AGENT_CLASS_MAP = {
    "Agent1": "agents.agent1:Agent1",
    "Agent2": "agents.agent2:Agent2", 
    "Agent3": "agents.agent3:Agent3",
    "Agent4": "agents.agent4:Agent4",
    "Agent5": "agents.agent5:Agent5",
    "Agent6": "agents.agent6:Agent6",
    "Agent7": "agents.agent7:Agent7",
    "Agent8": "agents.agent8:Agent8",
    "Agent9": "agents.agent9:Agent9",
    "Agent10": "agents.agent10:Agent10",
    "Agent11": "agents.agent11:Agent11",
    "Agent12": "agents.agent12:Agent12",
    "Agent13": "agents.agent13:Agent13",
    "Agent14": "agents.agent14:Agent14",
    "Agent15": "agents.agent15:Agent15",
    "Agent16": "agents.agent16:Agent16",
    "Agent17": "agents.agent17:Agent17",
    "Agent18": "agents.agent18:Agent18",
    "Agent19": "agents.agent19:Agent19",
    "Agent20": "agents.agent20:Agent20",
    "Agent21": "agents.agent21:Agent21",
    "Agent22": "agents.agent22:Agent22",
    "Agent23": "agents.agent23:Agent23",
    "Agent24": "agents.agent24:Agent24",
    "Agent25": "agents.agent25:Agent25",
    "Agent26": "agents.agent26:Agent26",
    "Agent27": "agents.agent27:Agent27",
    "Agent28": "agents.agent28:Agent28",
    "Agent29": "agents.agent29:Agent29",
    "Agent30": "agents.agent30:Agent30",
    "LoreMaster": "agents.personas:LoreMaster",
    "MemeLord": "agents.personas:MemeLord", 
    "AlphaScry": "agents.personas:AlphaScry",
    "GremlinGM": "agents.personas:GremlinGM",
    "SwarmCoordinator": "agents.swarm:SwarmCoordinator",
    "EnhancedSwarmCoordinator": "agents.EnhancedSwarmCoordinator:EnhancedSwarmCoordinator",
} 