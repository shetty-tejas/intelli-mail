from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os

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

def load_json_data(filename: str) -> List[Dict[str, Any]]:
    filepath = os.path.join("stores", filename)
    with open(filepath, "r") as file:
        return json.load(file)

@app.tool()
async def get_companies() -> List[Company]:
    """
    Get a list of all companies.

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

    Use this tool when the user refers to a company by its numeric ID.
    You can use it after getting company_id via name-matching with get_companies().

    Args:
        company_id: The ID of the company (integer).

    Returns:
        A Company object with `id` and `name`, or null if not found.
    """
    companies = load_json_data("companies.json")
    company = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        return None
    return Company(**company)

@app.tool()
def get_contacts_for_company(company_id: int):
    """
    Get all contacts for a specific company.

    Use this tool when the user asks for:
      - All contacts at a company
      - The primary contact at a company
      - Contact emails or names belonging to a company

    First, ensure that the company exists using `get_companies()` or `get_company()`.

    Args:
        company_id: The ID of the company (integer).

    Returns:
        A list of Contact objects with `id`, `name`, `email`, `primary`, and `company_id`.
    """
    companies = load_json_data("companies.json")
    company = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    contacts = load_json_data("contacts.json")
    company_contacts = [c for c in contacts if c["company_id"] == company_id]
    return [Contact(**contact) for contact in company_contacts]

@app.tool()
def get_contact_for_company(company_id: int, contact_id: int):
    """
    Get a specific contact within a given company.

    Use this tool when the user asks for a single contact by ID, within the context of a company.
    This is helpful for confirming ownership of a contact within a company.

    Args:
        company_id: The ID of the company the contact belongs to.
        contact_id: The ID of the contact to fetch.

    Returns:
        A Contact object if found, or null if either the company or contact is not found.
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
