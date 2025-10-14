import json
import functions_framework

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Expects JSON or query params with 'glucose'.
    Returns a JSON classification focused on hypoglycemia and hyperglycemia.
    """

    data = request.get_json(silent=True) or {}
    args = request.args or {}

    glucose = data.get("glucose", args.get("glucose"))

    # Presence check
    if glucose is None:
        return (
            json.dumps({"error": "Field 'glucose' is required."}),
            400,
            {"Content-Type": "application/json"},
        )

    # Type/convert check
    try:
        glucose_val = float(glucose)
    except (TypeError, ValueError):
        return (
            json.dumps({"error": "'glucose' must be a number."}),
            400,
            {"Content-Type": "application/json"},
        )

    # Classification logic for hypo/hyperglycemia
    if glucose_val < 54:
        category = "Severe Hypoglycemia"
        status = "emergency"
    elif 54 <= glucose_val < 70:
        category = "Hypoglycemia"
        status = "abnormal"
    elif 70 <= glucose_val <= 180:
        category = "Normal / Target Range"
        status = "normal"
    elif 181 <= glucose_val <= 250:
        category = "Hyperglycemia"
        status = "abnormal"
    else:  # >250
        category = "Severe Hyperglycemia / Possible DKA Risk"
        status = "emergency"

    payload = {
        "glucose": glucose_val,
        "status": status,
        "category": category,
    }

    return json.dumps(payload), 200, {"Content-Type": "application/json"}

