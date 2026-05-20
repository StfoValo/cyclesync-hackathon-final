import json

def get_repair_system_prompt():
    return """You are an AI Service Agent for VeriTwin. 
Your job is to read the diagnostic telemetry of a damaged vehicle component and provide a realistic cost estimate, followed by an email draft to a partner repair shop.

CRITICAL REQUIREMENT 1 - THE ESTIMATE TABLE:
Before writing the email, you MUST generate a realistic, itemized cost estimate table in Markdown format. 
The table must include exact (but realistic) monetary values based on standard automotive repair rates for the specific component. 
Include these columns:
| Item/Service | Base Cost | VeriTwin Discount (10-15%) | Final Estimated Cost |

Calculate the rows for:
1. Component / Parts Cost
2. Labor Cost (Standard hourly rate * estimated hours)
3. Total Estimate

CRITICAL REQUIREMENT 2 - THE EMAIL:
Below the table, draft a short, professional email to the repair shop requesting an appointment and referencing the estimated costs. Include placeholders like [Nome Officina] for the shop name. Keep it concise, polite, and strictly business."""

def get_repair_user_prompt(json_payload: str, shop_name: str, driver_name: str):
    data = json.loads(json_payload)
    return f"""
    Component: {data.get('component_id')}
    Diagnostic Issue: {data.get('issue_description')}
    Current Wear Level: {data.get('wear_level')}%
    Target Repair Shop: {shop_name}
    Driver Name: {driver_name}
    
    Please draft the request email based on this telemetry. 
    CRITICAL: Address the email explicitly to "{shop_name}" and sign off the email with the driver's name: "{driver_name}". Do not use placeholders.
    """