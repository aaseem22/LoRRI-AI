import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "microsoft/DialoGPT-small"
MAX_NEW_TOKENS = 60
TEMPERATURE = 0.7

_tokenizer = None
_model = None
_chat_history_ids = None

def _load_model():
    global _tokenizer, _model
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        # FIX 1: Set the pad token to avoid the warning
        _tokenizer.pad_token = _tokenizer.eos_token 
        _model.eval()

def generate_lorri_response(user_prompt: str) -> str:
    global _chat_history_ids
    _load_model()
    
    if not user_prompt.strip():
        return "Awaiting freight query."

    # Encode user input
    new_ids = _tokenizer.encode(user_prompt + _tokenizer.eos_token, return_tensors="pt")
    
    # Append to history
    if _chat_history_ids is None:
        bot_input = new_ids
    else:
        bot_input = torch.cat([_chat_history_ids, new_ids], dim=-1)
        
    if bot_input.shape[-1] > 1000:
        bot_input = bot_input[:, -1000:]

    # FIX 2: Create the attention mask to clear the red terminal warning
    attention_mask = torch.ones(bot_input.shape, dtype=torch.long)

    with torch.no_grad():
        out = _model.generate(
            bot_input,
            attention_mask=attention_mask, # Pass the mask here
            max_new_tokens=MAX_NEW_TOKENS,
            pad_token_id=_tokenizer.eos_token_id,
            do_sample=True,
            top_p=0.9,
            temperature=TEMPERATURE,
        )
        
    _chat_history_ids = out
    new_tokens = out[:, bot_input.shape[-1]:]
    reply_text = _tokenizer.decode(new_tokens[0], skip_special_tokens=True).strip()
    
    # FIX 3: The Professional Guardrail. 
    # If the Reddit model gets confused and tries to ask a weird question, override it.
    if not reply_text or reply_text.endswith("?") or "you" in reply_text.lower():
        reply_text = "I am processing the logistics parameters for your route and updating the dashboard now."
        
    return reply_text[0].upper() + reply_text[1:]