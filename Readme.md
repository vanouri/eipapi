

# 📈 P2P Market Prediction API

A clean, open-source API providing real-time market sentiment signals. This service processes public P2P indicators to generate actionable trading bias: **Long**, **Short**, or **Neutral**.

## 🌐 Public Endpoint & Documentation

You can integrate these predictions into your trading bots or explore the API structure via the interactive documentation:

* **Base URL:** `http://217.182.105.192:8000`
* **Swagger UI (Docs):** [http://217.182.105.192:8000/docs](http://217.182.105.192:8000/docs)

---

## 🛰 API Reference

### Get Market Prediction

Returns the current directional signal calculated from P2P market data.

* **Endpoint:** `/prediction`
* **Method:** `GET`
* **Response Format:** `application/json`

#### Example Request

```bash
curl -X GET "http://217.182.105.192:8000/prediction"

```

#### Example Response

```json
{
  "prediction": 1
}

```

---

## 📊 Signal Interpretation

The `prediction` value follows a standard trading logic to help automate your decision-making process:

| Value | Sentiment | Action |
| --- | --- | --- |
| **`1`** | **Bullish** | **Long Position**: Positive momentum detected. |
| **`0`** | **Neutral** | **No Position**: Market uncertainty / Exit current trade. |
| **`-1`** | **Bearish** | **Short Position**: Negative momentum detected. |

---

## 🧪 Testing

To ensure the API is responding correctly and returning valid data structures, you can run the provided unit test suite.

1. **Ensure you have `requests` installed:**
```bash
pip install requests

```


2. **Run the tests:**
```bash
python3 unit.py

```



---

## 🛠 Integration Example (JavaScript/Fetch)

```javascript
const getSignal = async () => {
    const response = await fetch('http://217.182.105.192:8000/prediction');
    const data = await response.json();
    
    if (data.prediction === 1) {
        console.log("🚀 Signal: LONG");
    } else if (data.prediction === -1) {
        console.log("📉 Signal: SHORT");
    } else {
        console.log("💤 Signal: NEUTRAL");
    }
};

```

## ⚖️ License & Disclaimer

This project is open-source. Please note that these predictions are based on mathematical indicators and do not constitute financial advice. **Trade at your own risk.**
