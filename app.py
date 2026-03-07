from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Mock Database for the "Intelligence Grid"
PORT_COORDINATES = {
    "shanghai": [31.2304, 121.4737],
    "ningbo": [29.8683, 121.5440],
    "singapore": [1.3521, 103.8198],
    "rotterdam": [51.9225, 4.4792],
    "los angeles": [34.0522, -118.2437]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_lorri():
    user_message = request.json.get("message", "").lower()
    
    # Logic: Search for port names in the user's message
    target_city = None
    for city in PORT_COORDINATES:
        if city in user_message:
            target_city = city
            break
            
    if target_city:
        coords = PORT_COORDINATES[target_city]
        response_text = f"Rerouting intelligence grid to {target_city.title()}. Optimizing for fuel efficiency..."
        return jsonify({
            "status": "success",
            "message": response_text,
            "coords": coords,
            "city": target_city.title()
        })
    
    return jsonify({
        "status": "unknown",
        "message": "I'm monitoring the global grid. Please specify a port (e.g., Singapore).",
        "coords": None
    })

if __name__ == '__main__':
    app.run(debug=True)