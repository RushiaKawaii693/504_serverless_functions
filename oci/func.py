import io
import json
import logging

from fdk import response

def handler(ctx, data: io.BytesIO = None):
    """
    OCI Function for fasting glucose triage.
    Classifies glucose levels as normal or abnormal.
    
    Normal: 70-99 mg/dL
    Abnormal: <70 (hypoglycemia) or >=100 (elevated)
    
    Citation: American Diabetes Association. (2024). 
    Standards of Medical Care in Diabetes—2024. 
    Diabetes Care, 47(Supplement_1), S20-S42.
    """
    try:
        # Parse JSON from request body
        try:
            body = json.loads(data.getvalue())
        except (Exception, ValueError) as ex:
            logging.error(f'Error parsing JSON: {str(ex)}')
            return response.Response(
                ctx, 
                response_data=json.dumps({
                    "error": "Request must contain valid JSON data."
                }),
                headers={"Content-Type": "application/json"},
                status_code=400
            )

        # Validate required field
        if 'glucose' not in body:
            return response.Response(
                ctx,
                response_data=json.dumps({
                    "error": "'glucose' field is required (fasting glucose in mg/dL)."
                }),
                headers={"Content-Type": "application/json"},
                status_code=400
            )

        glucose = body['glucose']

        # Validate numeric input
        try:
            glucose = float(glucose)
        except (ValueError, TypeError):
            return response.Response(
                ctx,
                response_data=json.dumps({
                    "error": "'glucose' must be a number."
                }),
                headers={"Content-Type": "application/json"},
                status_code=400
            )

        # Validate reasonable range
        if glucose < 10 or glucose > 600:
            return response.Response(
                ctx,
                response_data=json.dumps({
                    "error": "Glucose value out of reasonable range (10-600 mg/dL)."
                }),
                headers={"Content-Type": "application/json"},
                status_code=400
            )

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
        result = {
            "glucose_mg_dl": glucose,
            "status": status,
            "category": category,
            "reference_range": "70-99 mg/dL (normal fasting glucose)"
        }

        return response.Response(
            ctx,
            response_data=json.dumps(result),
            headers={"Content-Type": "application/json"},
            status_code=200
        )

    except Exception as e:
        logging.error(f'Error in handler: {str(e)}')
        return response.Response(
            ctx,
            response_data=json.dumps({
                "error": f"Internal server error: {str(e)}"
            }),
            headers={"Content-Type": "application/json"},
            status_code=500
        )
