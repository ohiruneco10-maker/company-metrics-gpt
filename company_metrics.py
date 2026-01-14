from flask import Flask, request, jsonify
import yfinance as yf

app = Flask(__name__)

@app.route("/metrics")
def metrics():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "code is required"})

    ticker = yf.Ticker(f"{code}.T")
    info = ticker.info

    data = {
        "code": code,
        "issued_shares": info.get("sharesOutstanding"),
        "current_assets": info.get("totalCurrentAssets"),
        "investment_securities": info.get("totalInvestments"),
        "total_liabilities": info.get("totalLiab"),
    }

    return jsonify(data)


if __name__ == "__main__":
    app.run()

