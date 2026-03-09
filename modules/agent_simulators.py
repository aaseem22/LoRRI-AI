import random
import time
from datetime import datetime

# --- AGENT TYPES ---
AGENTS = [
    "Procurement Agent SEA-1",
    "Procurement Agent EU-2",
    "Procurement Agent US-3",
    "Optimization Engine",
    "Sustainability Intelligence",
    "Global Freight Intelligence Grid"
]

# --- ACTIONS ---
ACTIONS = [
    "analyzing freight contracts",
    "optimizing shipping routes",
    "negotiating carrier rates",
    "detecting port congestion",
    "calculating CO2 reduction",
    "monitoring freight demand",
    "updating carrier pricing",
    "evaluating procurement strategy"
]

# --- REGIONS ---
REGIONS = [
    "Port of Los Angeles",
    "Singapore Freight Hub",
    "Rotterdam Port",
    "Shanghai Logistics Corridor",
    "Dubai Trade Gateway"
]

def generate_agent_activity():
    """Generates a simulated AI agent activity log."""
    agent = random.choice(AGENTS)
    action = random.choice(ACTIONS)
    efficiency = random.randint(3, 18)

    return {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "activity": action,
        "impact": f"{efficiency}% efficiency improvement"
    }

def generate_optimization_metrics():
    """Generates simulated AI optimization metrics."""
    return {
        "cost_reduction": f"{random.randint(5,15)}%",
        "carbon_reduction": f"{round(random.uniform(3.5,10.2),1)}%",
        "contracts_analyzed": random.randint(1200, 4200),
        "active_agents": random.randint(6, 18)
    }

def generate_freight_event():
    """Simulates global freight intelligence events."""
    region = random.choice(REGIONS)
    event = random.choice([
        "demand spike detected",
        "port congestion alert",
        "carrier capacity increase",
        "route optimization triggered",
        "procurement opportunity identified"
    ])

    return {
        "region": region,
        "event": event
    }

def generate_system_snapshot():
    """Combined system state for the UI."""
    return {
        "activity": generate_agent_activity(),
        "metrics": generate_optimization_metrics(),
        "freight_event": generate_freight_event()
    }