from flask import Flask, render_template, request, jsonify
from modules.intent_processor import get_map_and_roi_data
from modules.ai_chat_module import generate_lorri_response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_lorri():
    user_message = request.json.get("message", "")
    
    # 1. Run Raj's NER & ROI Logic
    map_data, roi_data = get_map_and_roi_data(user_message)
    
    # 2. Run Asim's DialoGPT Logic (The conversational intro)
    chat_reply = generate_lorri_response(user_message)
    
    # 3. GENERATE THE DYNAMIC EXPLANATION (NEW)
    # This translates the math into a readable sentence so the user understands the UI.
    intent_str = roi_data['primary_intent'].upper()
    region_str = map_data['region']
    savings = f"${roi_data['cost_saved_usd']:,}"
    eco = f"{roi_data['sustainability_score_improvement']}%"
    fleet = f"{roi_data['active_fleet']:,}"
    
    explanation = (
        f"<br><br>"
        f"<small class='text-secondary'>⚡ SYSTEM REPORT:</small><br>"
        f"<em>I have locked the map to the <strong>{region_str}</strong>. "
        f"Based on your request, my primary optimization target is <strong>{intent_str}</strong>. "
        f"By analyzing {fleet} active vessels in this lane, I am projecting a savings of <strong>{savings}</strong> "
        f"while improving our carbon footprint by <strong>{eco}</strong>.</em>"
    )
    
    # Combine Asim's chat with the dynamic system report
    final_message = chat_reply + explanation
    
    # 4. Send everything back to Esha's UI
    return jsonify({
        "message": final_message,
        "map_action": map_data,
        "roi_calc": roi_data
    })

if __name__ == '__main__':
    app.run(debug=True)