from transformers import pipeline
import random
import hashlib
import requests # <-- NEW: Needed to talk to the global map API

print("Loading LORRI.AI Intelligence Module... (NER Model)")
nlp_model = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

def get_dynamic_coordinates(place_name):
    """Hits a free global API to find the latitude/longitude of ANY place on Earth."""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={place_name}&format=json&limit=1"
        # The API requires a user-agent header
        headers = {'User-Agent': 'LorriAI-Hackathon-Prototype'} 
        response = requests.get(url, headers=headers, timeout=3).json()
        
        if len(response) > 0:
            return float(response[0]['lat']), float(response[0]['lon']), response[0]['display_name']
    except Exception as e:
        print(f"API Error or Location not found: {e}")
    return None, None, None

def get_map_and_roi_data(user_prompt):
    prompt_lower = user_prompt.lower()
    
    # 1. Base default map (Global View)
    map_data = {"region": "Global Dashboard", "lat": 20.0, "lon": 0.0, "zoom": 2, "base_cost": 100000}
    
    # 2. Intent Recognition
    intent = "general"
    if any(word in prompt_lower for word in ["carbon", "emission", "green", "sustainab", "eco"]):
        intent = "sustainability"
    elif any(word in prompt_lower for word in ["cost", "cheap", "price", "rate", "save", "budget"]):
        intent = "cost"

    # 3. Extract Location using AI & Hit the Live API
    ai_results = nlp_model(user_prompt)
    for entity in ai_results:
        if entity['entity_group'] == 'LOC':
            detected_place = entity['word'].lower()
            print(f"[AI Identified Location]: {detected_place.capitalize()} - Searching Global Grid...")
            
            # THE UPGRADE: Ask the live internet for the coordinates
            live_lat, live_lon, live_name = get_dynamic_coordinates(detected_place)
            
            if live_lat and live_lon:
                map_data = {
                    "region": live_name.split(',')[0], # Just get the city/area name
                    "lat": live_lat, 
                    "lon": live_lon, 
                    "zoom": 10, # Zoom in close for specific places
                    "base_cost": random.randint(150000, 400000) # Dynamic base cost
                }
            break

    # 4. Math Seed Logic (To keep numbers consistent for the same query)
    meaning_string = f"{map_data['region']}_{intent}"
    seed_value = int(hashlib.md5(meaning_string.encode('utf-8')).hexdigest(), 16) % 10000
    random.seed(seed_value)

    # 5. Smart ROI Math
    base = map_data["base_cost"]
    variance = random.uniform(0.95, 1.05) 
    
    if intent == "sustainability":
        cost_saved = int(base * 0.12 * variance)
        eco_score = int(random.uniform(38, 55)) 
        eff_gain = int(random.uniform(10, 18))
    elif intent == "cost":
        cost_saved = int(base * 0.35 * variance)
        eco_score = int(random.uniform(5, 12))
        eff_gain = int(random.uniform(28, 42))
    else:
        cost_saved = int(base * 0.22 * variance)
        eco_score = int(random.uniform(15, 25))
        eff_gain = int(random.uniform(18, 28))

    roi_data = {
        "cost_saved_usd": cost_saved,
        "efficiency_gain_pct": eff_gain,
        "sustainability_score_improvement": eco_score,
        "primary_intent": intent,
        "active_fleet": random.randint(850, 4200)
    }
    
    random.seed()
    
    clean_map_data = {
        "region": map_data["region"],
        "lat": map_data["lat"],
        "lon": map_data["lon"],
        "zoom": map_data["zoom"]
    }
    
    return clean_map_data, roi_data