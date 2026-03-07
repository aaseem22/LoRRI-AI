import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ─── MODEL CONFIG ─────────────────────────────────────────────────────────────

MODEL_NAME     = "microsoft/DialoGPT-small"
MAX_NEW_TOKENS = 120
TEMPERATURE    = 0.72
TOP_P          = 0.90
TOP_K          = 50

# ─── LAZY LOADER (load once, reuse forever) ───────────────────────────────────

_tokenizer = None
_model     = None


def _load_model():
    global _tokenizer, _model
    if _tokenizer is None:
        print("[LORRI] Loading DialoGPT-small — one-time download on first run...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model     = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        _model.eval()
        print("[LORRI] Model ready.")


# ─── LORRI PERSONA SEED ───────────────────────────────────────────────────────
# DialoGPT-small has no system-prompt slot.
# We prime the token history with two LORRI-branded Q&A pairs before
# every conversation, giving the model a personality anchor.

PERSONA_SEED = [
    (
        "Who are you?",
        "I am LORRI — LORRI.AI's Freight Optimization Engine. "
        "I analyse global freight lanes, carrier rates, and sustainability "
        "metrics in real time to surface the best routes worldwide.",
    ),
    (
        "What do you do?",
        "I optimise freight lanes, surface the lowest-cost and lowest-emission "
        "carriers, flag congestion hotspots, and calculate live ROI and CO2 "
        "impact for every route decision.",
    ),
]

# ─── NLU: KEYWORD → SIMULATED KPI DATA ───────────────────────────────────────

ROUTE_SIGNALS = {
    "shanghai":    {"port_alt": "Ningbo (NGB)",          "congestion_index": 78},
    "rotterdam":   {"region":   "North Sea Gateway",      "dwell_avg": "1.2 days"},
    "singapore":   {"port_alt": "Tanjung Pelepas (PTP)",  "congestion_index": 42},
    "los angeles": {"port_alt": "Long Beach (LGB)",        "congestion_index": 61},
    "hamburg":     {"region":   "Northern Range Hub",      "dwell_avg": "0.9 days"},
    "ningbo":      {"port_alt": "Shanghai (PVG)",          "congestion_index": 35},
    "dubai":       {"port_alt": "Jebel Ali (JXBA)",        "congestion_index": 29},
}

INTENT_SIGNALS = {
    "sustainab":  {"co2_saving_pct": 22,      "sustainability_score": 87},
    "green":      {"co2_saving_pct": 18,      "sustainability_score": 82},
    "emission":   {"co2_saving_pct": 20,      "sustainability_score": 85},
    "cost":       {"cost_saving_usd": 140_000, "roi_weeks": 3},
    "cheap":      {"cost_saving_usd":  95_000, "roi_weeks": 2},
    "fast":       {"transit_reduction_days": 4, "eta_confidence": "94%"},
    "urgent":     {"transit_reduction_days": 6, "eta_confidence": "91%"},
    "congestion": {"congestion_risk_avoided_pct": 88},
    "optimis":    {"lanes_analysed": 3_400,   "best_lane_delta_usd": 112_000},
    "optimiz":    {"lanes_analysed": 3_400,   "best_lane_delta_usd": 112_000},
}


def _extract_context(prompt: str) -> dict:
    p = prompt.lower()
    ctx: dict = {"routes": {}, "intents": {}}
    for kw, data in ROUTE_SIGNALS.items():
        if kw in p:
            ctx["routes"][kw] = data
    for kw, data in INTENT_SIGNALS.items():
        if kw in p:
            ctx["intents"][kw] = data
    return ctx


# ─── BRAND WRAPPING ───────────────────────────────────────────────────────────

def _status_prefix(ctx: dict) -> str:
    parts = []
    if ctx["intents"].get("optimis") or ctx["intents"].get("optimiz"):
        sig = ctx["intents"].get("optimis", ctx["intents"].get("optimiz", {}))
        parts.append(f"{sig.get('lanes_analysed', 3400):,} lanes analysed")
    if ctx["routes"]:
        parts.append("signals active: " + ", ".join(k.title() for k in ctx["routes"]))
    if ctx["intents"].get("sustainab") or ctx["intents"].get("green"):
        parts.append("sustainability module — engaged")
    body = " | ".join(parts) if parts else "query received"
    return f"▸ Optimization Engine — active | {body}.\n\n"


def _kpi_suffix(ctx: dict) -> str:
    lines = []
    for port, data in ctx["routes"].items():
        if "congestion_index" in data:
            alt = f"  →  alt: {data['port_alt']}" if "port_alt" in data else ""
            lines.append(f"  • {port.title()} congestion index: {data['congestion_index']}/100{alt}")
    i = ctx["intents"]
    if "congestion" in i:
        lines.append(f"  • Congestion risk avoided: {i['congestion']['congestion_risk_avoided_pct']}%")
    if "cost" in i or "cheap" in i:
        s = i.get("cost", i.get("cheap", {}))
        lines.append(f"  • Estimated cost saving:  ${s.get('cost_saving_usd', 0):,}")
        lines.append(f"  • Payback period:          {s.get('roi_weeks', 3)} weeks")
    if any(k in i for k in ("sustainab", "green", "emission")):
        s = i.get("sustainab", i.get("green", i.get("emission", {})))
        lines.append(f"  • CO₂ reduction:           {s.get('co2_saving_pct', 18)}%")
        lines.append(f"  • Sustainability score:    {s.get('sustainability_score', 82)}/100")
    if "fast" in i or "urgent" in i:
        s = i.get("fast", i.get("urgent", {}))
        lines.append(f"  • Transit reduction:       {s.get('transit_reduction_days', 4)} days")
        lines.append(f"  • ETA confidence:          {s.get('eta_confidence', '94%')}")
    if not lines:
        return ""
    return "\n\n" + "─" * 50 + "\n  LORRI KPI SNAPSHOT\n" + "\n".join(lines)


def _post_process(raw: str, ctx: dict) -> str:
    raw = raw.strip()
    if not raw:
        raw = (
            "Processing your freight parameters across global lanes. "
            "Provide an origin, destination, or optimization objective "
            "to activate the full intelligence suite."
        )
    raw = re.sub(r"\s+", " ", raw)
    raw = raw[0].upper() + raw[1:]
    return _status_prefix(ctx) + raw + _kpi_suffix(ctx)


# ─── INFERENCE ────────────────────────────────────────────────────────────────

def _build_seed_ids() -> torch.Tensor:
    ids = None
    for u_txt, b_txt in PERSONA_SEED:
        u = _tokenizer.encode(u_txt + _tokenizer.eos_token, return_tensors="pt")
        b = _tokenizer.encode(b_txt + _tokenizer.eos_token, return_tensors="pt")
        ids = torch.cat([ids, u, b], dim=-1) if ids is not None else torch.cat([u, b], dim=-1)
    return ids


def _infer(user_prompt: str, history_ids=None):
    _load_model()
    new_ids = _tokenizer.encode(user_prompt + _tokenizer.eos_token, return_tensors="pt")
    if history_ids is None:
        history_ids = _build_seed_ids()
    bot_input = torch.cat([history_ids, new_ids], dim=-1)
    if bot_input.shape[-1] > 1024:
        bot_input = bot_input[:, -1024:]
    with torch.no_grad():
        out = _model.generate(
            bot_input,
            max_new_tokens=MAX_NEW_TOKENS,
            pad_token_id=_tokenizer.eos_token_id,
            do_sample=True,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
        )
    new_tokens = out[:, bot_input.shape[-1]:]
    text = _tokenizer.decode(new_tokens[0], skip_special_tokens=True)
    return text, out


# ─── PUBLIC API ───────────────────────────────────────────────────────────────

def generate_lorri_response(user_prompt: str) -> str:
    """
    Primary entry point.

    Parameters
    ----------
    user_prompt : str   Raw message from the end user.

    Returns
    -------
    str   LORRI-branded response with KPI snapshot where relevant.
    """
    if not user_prompt or not user_prompt.strip():
        return (
            "▸ LORRI Intelligence Grid — standby | Awaiting freight query.\n"
            "Provide an origin, destination, or optimization objective to begin."
        )
    ctx = _extract_context(user_prompt)
    raw, _ = _infer(user_prompt)
    return _post_process(raw, ctx)


def generate_lorri_response_with_history(
    user_prompt: str,
    history_ids=None,
):
    """
    Multi-turn variant — preserves DialoGPT token history for context-aware
    follow-up queries (e.g. "What about via Suez instead?").

    Parameters
    ----------
    user_prompt  : str             Latest user message.
    history_ids  : torch.Tensor | None   Tensor returned by previous call.

    Returns
    -------
    tuple[str, torch.Tensor]   (response text, updated history tensor)
    """
    if not user_prompt or not user_prompt.strip():
        return (
            "▸ LORRI Intelligence Grid — standby | Awaiting freight query.",
            history_ids,
        )
    ctx = _extract_context(user_prompt)
    raw, updated_ids = _infer(user_prompt, history_ids)
    return _post_process(raw, ctx), updated_ids