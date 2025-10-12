import functions_framework
from flask import jsonify

@functions_framework.http
def glucose_triage(request):
    """
    HTTP Cloud Function for fasting glucose triage.
    Classifies glucose levels as normal or abnormal.
    
    Normal: 70-99 mg/dL
    Abnormal: <70 (hypoglycemia) or >=100 (elevated)
    
    Citation: American Diabetes Association. (2024). 
    Standards of Medical Care in Diabetes—2024. 
    Diabetes Care, 47(Supplement_1), S20-S42.
    """
    # Handle CORS for web requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)

    headers = {'Access-Control-Allow-Origin': '*'}

    try:
        # Parse JSON from request
        request_json = request.get_json(silent=True)
        
        if not request_json:
            return jsonify({
                "error": "Request must contain JSON data."
            }), 400, headers

        # Validate required field
        if 'glucose' not in request_json:
            return jsonify({
                "error": "'glucose' field is required (fasting glucose in mg/dL)."
            }), 400, headers

        glucose = request_json['glucose']

        # Validate numeric input
        try:
            glucose = float(glucose)
        except (ValueError, TypeError):
            return jsonify({
                "error": "'glucose' must be a number."
            }), 400, headers

        # Validate reasonable range (10-600 mg/dL)
        if glucose < 10 or glucose > 600:
            return jsonify({
                "error": "Glucose value out of reasonable range (10-600 mg/dL)."
            }), 400, headers

        # Apply clinical rule (ADA 2024 guidelines)
        if 70 <= glucose < 100:
            status = "normal"
            category = "Normal (70-99 mg/dL)"
        elif glucose < 70:
            status = "abnormal"
            category = "Hypoglycemia (<70 mg/dL)"
        else:  # glucose >= 100
            status = "abnormal"
            category = "Elevated (≥100 mg/dL - Prediabetes/Diabetes range)"

        # Return structured response
        return jsonify({
            "glucose_mg_dl": glucose,
            "status": status,
            "category": category,
            "reference_range": "70-99 mg/dL (normal fasting glucose)"
        }), 200, headers

    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500, headers
