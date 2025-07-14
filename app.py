from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os

app = FastAPI()

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

@app.get("/companies", response_model=List[Company], operation_id="get_all_companies")
def get_companies():
    companies = load_json_data("companies.json")
    return [Company(**company) for company in companies]

@app.get("/companies/{company_id}", response_model=Company, operation_id="get_company_by_id")
def get_company(company_id: int):
    companies = load_json_data("companies.json")
    company = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return Company(**company)

@app.get("/companies/{company_id}/contacts", response_model=List[Contact], operation_id="get_all_contacts_for_company_id")
def get_contacts(company_id: int):
    companies = load_json_data("companies.json")
    company = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    contacts = load_json_data("contacts.json")
    company_contacts = [c for c in contacts if c["company_id"] == company_id]
    return [Contact(**contact) for contact in company_contacts]

@app.get("/companies/{company_id}/contacts/{contact_id}", response_model=Contact, operation_id="get_contact_by_id_for_company_id")
def get_contact(company_id: int, contact_id: int):
    companies = load_json_data("companies.json")
    company = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    contacts = load_json_data("contacts.json")
    contact = next((c for c in contacts if c["id"] == contact_id and c["company_id"] == company_id), None)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return Contact(**contact)
