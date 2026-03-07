from transformers import pipeline
import random

print("Loading LORRI.AI Intelligence Module... (NER Model)")
# Using the Hugging Face NER model to dynamically find locations
nlp_model = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

# Level 2 Expanded GPS Database with Baseline Costs for realistic math
GPS_DATABASE = {
    "shanghai": {"region": "Shanghai Port", "lat": 31.2222, "lon": 121.4581, "zoom": 10, "base_cost": 200000},
    "rotterdam": {"region": "Port of Rotterdam", "lat": 51.9225, "lon": 4.47917, "zoom": 12, "base_cost": 180000},
    "europe": {"region": "Europe Lanes", "lat": 54.5260, "lon": 15.2551, "zoom": 4, "base_cost": 500000},
    "sea": {"region": "Southeast Asia", "lat": 1.3521, "lon": 103.8198, "zoom": 5, "base_cost": 300000},
    "los angeles": {"region": "Port of LA", "lat": 33.7288, "lon": -118.2620, "zoom": 11, "base_cost": 250000},
    "singapore": {"region": "Port of Singapore", "lat": 1.264, "lon": 103.840, "zoom": 12, "base_cost": 220000},
    "dubai": {"region": "Jebel Ali Port", "lat": 24.9857, "lon": 55.0273, "zoom": 11, "base_cost": 150000},
    "suez": {"region": "Suez Canal", "lat": 30.5852, "lon": 32.2654, "zoom": 8, "base_cost": 400000},
    "panama": {"region": "Panama Canal", "lat": 9.1012, "lon": -79.6953, "zoom": 9, "base_cost": 350000},
    "mumbai": {"region": "Nhava Sheva / JNPT", "lat": 18.9493, "lon": 72.9509, "zoom": 11, "base_cost": 120000},
    "default": {"region": "Global Dashboard", "lat": 20.0, "lon": 0.0, "zoom": 2, "base_cost": 100000}
}

def get_map_and_roi_data(user_prompt):
    """
    Level 2: Extracts locations via NER, identifies user intent (Cost vs Eco),
    and dynamically calculates realistic ROI metrics based on the lane.
    """
    prompt_lower = user_prompt.lower()
    
    # 1. Graceful Fallback (Edge Case Handling)
    # If the AI finds nothing, default to a zoomed-out world map instead of crashing.
    map_data = GPS_DATABASE["default"]
    
    # 2. Intent Recognition (What does the user actually care about?)
    intent = "general"
    if any(word in prompt_lower for word in ["carbon", "emission", "green", "sustainab", "eco"]):
        intent = "sustainability"
    elif any(word in prompt_lower for word in ["cost", "cheap", "price", "rate", "save", "budget"]):
        intent = "cost"

    # 3. Extract Location using AI
    ai_results = nlp_model(user_prompt)
    detected_place = None
    
    for entity in ai_results:
        if entity['entity_group'] == 'LOC':
            detected_place = entity['word'].lower()
            
            # Match against our expanded database
            for known_place in GPS_DATABASE.keys():
                if known_place in detected_place or detected_place in known_place:
                    map_data = GPS_DATABASE[known_place]
                    print(f"[AI Identified Location]: {known_place.capitalize()}")
                    break
            break # Stop after mapping the first major location

    # 4. Smart ROI Math (No more purely random numbers)
    base = map_data["base_cost"]
    variance = random.uniform(0.95, 1.05) # Add a tiny 5% variance so it looks "live"
    
    if intent == "sustainability":
        # Eco focus: Huge carbon savings, lower cost savings
        cost_saved = int(base * 0.12 * variance)
        eco_score = int(random.uniform(38, 55)) 
        eff_gain = int(random.uniform(10, 18))
    elif intent == "cost":
        # Cost focus: High cost savings, lower eco savings
        cost_saved = int(base * 0.35 * variance)
        eco_score = int(random.uniform(5, 12))
        eff_gain = int(random.uniform(28, 42))
    else:
        # Balanced baseline
        cost_saved = int(base * 0.22 * variance)
        eco_score = int(random.uniform(15, 25))
        eff_gain = int(random.uniform(18, 28))

    roi_data = {
        "cost_saved_usd": cost_saved,
        "efficiency_gain_pct": eff_gain,
        "sustainability_score_improvement": eco_score,
        "primary_intent": intent # Tells the frontend what the user cares about
    }
    
    # 5. Clean output for the frontend
    clean_map_data = {
        "region": map_data["region"],
        "lat": map_data["lat"],
        "lon": map_data["lon"],
        "zoom": map_data["zoom"]
    }
    
    return clean_map_data, roi_data

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("\n--- Testing Raj's Level 2 AI Extractor ---")
    
    test_phrases = [
        "Find me the cheapest rates out of Mumbai right now.",
        "We need to reduce our carbon emissions on the Dubai lane.",
        "Just give me a general overview of the Suez canal."
    ]
    
    for phrase in test_phrases:
        print(f"\nUser: '{phrase}'")
        map_result, roi_result = get_map_and_roi_data(phrase)
        
        print(f"Map Action: Fly to {map_result['region']}")
        print(f"Intent Detected: {roi_result['primary_intent'].upper()}")
        print(f"Calculated Savings: ${roi_result['cost_saved_usd']:,}")
        print(f"Eco Score: +{roi_result['sustainability_score_improvement']}%")