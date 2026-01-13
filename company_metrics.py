from typing import Optional, Dict, Any
from flask import Flask, request, jsonify
import os
import yfinance as yf
import pandas as pd

app = Flask(__name__)

def normalize_code_to_ticker(code: str) -> str:
    code = code.strip()
    if "." in code:
        return code
    if code.isdigit():
        return f"{code}.T"
    return code

def find_from_bs(df: Optional[pd.DataFrame], candidates):
    if df is None or df.empty:
        return None
    latest_col = df.columns[0]
    for idx in df.index:
        for c in candidates:
            if c.lower() in str(idx).lower():
                try:
                    return int(df.loc[idx, latest_col])
                except Exception:
                    pass
    return None

def get_metrics_for_ticker(ticker: str) -> Dict[str, Any]:
    t = yf.Ticker(ticker)
    info = {}
    try:
        info = t.info or {}
    except Exception:
        pass

    result = {
        "ticker": ticker,
        "shares_outstanding": info.get("sharesOutstanding"),
        "current_assets": None,
        "investment_securities": None,
        "total_liabilities": None,
        "currency": info.get("financialCurrency"),
        "source": "yfinance"
    }

    try:
        bs = t.quarterly_balance_sheet
        if bs is None or bs.empty:
            bs = t.balance_sheet
    except Exception:
        bs = None

    if bs is not None:
        result["current_assets"] = find_from_bs(bs, ["Current Assets"])
        result["investment_securities"] = find_from_bs(bs, ["Investments"])
        result["total_liabilities"] = find_from_bs(bs, ["Total Liabilities"])

    return result

@app.route("/metrics", methods=["GET"])
def metrics():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "code is required"}), 400
    ticker = normalize_code_to_ticker(code)
    return jsonify(get_metrics_for_ticker(ticker))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
