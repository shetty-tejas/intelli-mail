from fastmcp import FastMCP
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import requests
from datetime import date

app = FastMCP("IntelliMail")

class Company(BaseModel):
    id: int
    name: str

class Contact(BaseModel):
    id: int
    name: str
    email: str
    primary: bool
    company_id: int

class Invoice(BaseModel):
    id: int
    status: str
    einvoice_status: str
    currency_code: str
    total_amount: float
    sales_tax_amount: float
    invoice_date: str
    due_date: str
    payment_date: Optional[str] = None
    company_id: int

class Payment(BaseModel):
    id: int
    company_id: int

class EmailContact(BaseModel):
    email: str
    name: str

class EmailData(BaseModel):
    to: List[EmailContact]
    cc: Optional[List[EmailContact]] = []
    bcc: Optional[List[EmailContact]] = []
    subject: str
    htmlContent: str

class Template(BaseModel):
    id: int
    name: str
    subject: str
    content: str

def load_json_data(filename: str) -> List[Dict[str, Any]]:
    filepath = os.path.join("stores", filename)
    with open(filepath, "r") as file:
        return json.load(file)

@app.tool()
async def get_companies() -> List[Company]:
    """
    Get a list of all companies in english.

    Use this tool when the user asks for a list of companies, or when you need to perform
    a name match (e.g., "Find me contacts for Tesla" → fetch all companies, then match by name).

    Returns:
        A list of Company objects, each with `id` and `name`.
    """
    companies = load_json_data("companies.json")
    return [Company(**company) for company in companies]

@app.tool()
def get_company(company_id: int) -> Company:
    """
    Get details of a specific company by its ID.

    Use this tool only if company_id is known (usually from get_companies).

    Args:
        company_id: The ID of the company.

    Returns:
        A Company object with `id` and `name`, or null if not found.
    """
    companies = load_json_data("companies.json")
    company = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        return None
    return Company(**company)

@app.tool()
def get_contacts() -> List[Contact]:
    """
    Get all contacts across all companies.

    Use this when filtering, grouping, or searching for contacts.
    Always prefer this for generic or multi-company queries.

    Returns:
        A list of Contact objects.
    """
    contacts = load_json_data("contacts.json")
    return [Contact(**contact) for contact in contacts]

@app.tool()
def get_contacts_for_company(company_id: int) -> List[Contact]:
    """
    Get all contacts for a specific company.

    Only use this when the company_id is verified or resolved via name matching.

    Args:
        company_id: ID of the company.

    Returns:
        A list of Contact objects for that company.
    """
    companies = load_json_data("companies.json")
    company = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        return None

    contacts = load_json_data("contacts.json")
    company_contacts = [c for c in contacts if c["company_id"] == company_id]
    return [Contact(**contact) for contact in company_contacts]

@app.tool()
def get_contact_for_company(company_id: int, contact_id: int) -> Contact:
    """
    Get a specific contact from a company.

    Args:
        company_id: ID of the company.
        contact_id: ID of the contact.

    Returns:
        A Contact object if found; otherwise, null.
    """
    companies = load_json_data("companies.json")
    company = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        return None
    contacts = load_json_data("contacts.json")
    contact = next((c for c in contacts if c["id"] == contact_id and c["company_id"] == company_id), None)
    if not contact:
        return None
    return Contact(**contact)

@app.tool()
def get_invoices() -> List[Invoice]:
    """
    Get all invoices across all companies.

    Use this tool when filtering by status, amount, date, or for general summaries.

    Returns:
        A list of Invoice objects.
    """
    invoices = load_json_data("invoices.json")
    return [Invoice(**invoice) for invoice in invoices]

@app.tool()
def get_invoices_by_company_id(company_id: int) -> List[Invoice]:
    """
    Get all invoices for a specific company.

    Only use this when company_id is known.

    Args:
        company_id: ID of the company.

    Returns:
        A list of Invoice objects for the specified company.
    """
    companies = load_json_data("companies.json")
    company = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        return []

    invoices = load_json_data("invoices.json")
    company_invoices = [i for i in invoices if i["company_id"] == company_id]
    return [Invoice(**invoice) for invoice in company_invoices]

@app.tool()
def get_invoice_by_id(invoice_id: int) -> Invoice:
    invoices = load_json_data("invoices.json")
    invoice = next((i for i in invoices if c["id"] == invoice_id), None)
    if not invoice:
        return None

    return Invoice(**invoice)

@app.tool()
def get_email_template(template_name: str) -> Template:
    """
    Fetch email template based on name
    
    Args:
        template_name: template name of an email template
        
    Returns:
        Template Object if template found, False otherwise
    """
    email_templates = load_json_data("email_templates.json")
    email_template = next((c for c in email_templates if c["name"] == template_name), None)
    if not email_template:
        return None

    return Template(**email_template)

@app.tool()
def send_email(to: List[EmailContact], template: Template, html_content: str, 
               cc: Optional[List[EmailContact]] = None, bcc: Optional[List[EmailContact]] = None) -> bool:
    """
    Send an email using the specified parameters.
    
    Args:
        to: List of recipients
        template: Email template
        cc: Optional list of CC recipients
        bcc: Optional list of BCC recipients
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        email_data = {
            "data": {
                "type": "Email",
                "attributes": {
                    "from": {
                        "email": "email-service-test@2n334c.onmicrosoft.com",
                        "name": "email-service-test"
                    },
                    "to": [{"email": contact.email, "name": contact.name} for contact in to],
                    "cc": [{"email": contact.email, "name": contact.name} for contact in (cc or [])],
                    "bcc": [{"email": contact.email, "name": contact.name} for contact in (bcc or [])],
                    "subject": template.subject,
                    "htmlContent": template.content,
                    "attachments": []
                }
            }
        }
        

        headers = {
            "Authorization": "Bearer " + os.getenv('NES_API_TOKEN'),
            "Connection-Id": os.getenv('NES_CONNECTION_ID'),
            "traceparent": "00-7c8780d3940f412cb7f517a33d2213d9-aab3ab3c9789551c-01",
            "Idempotency-Key": "test"
        }
        
        response = requests.post(os.getenv('NES_API_DOMAIN') + "/datasets/e8f2c703-8b97-7cca-185f-f7ecc2f68a4f/emails", json=email_data, headers=headers)
        return response.status_code == 200        
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
