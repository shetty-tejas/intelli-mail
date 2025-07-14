from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_get_companies():
    response = client.get("/companies")
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) == 4
    assert companies[0]["name"] == "Acme Corporation"
    assert companies[1]["name"] == "Big Theta Corp"

def test_get_company():
    response = client.get("/companies/1")
    assert response.status_code == 200
    company = response.json()
    assert company["id"] == 1
    assert company["name"] == "Acme Corporation"

def test_get_company_not_found():
    response = client.get("/companies/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found"

def test_get_contacts():
    response = client.get("/companies/1/contacts")
    assert response.status_code == 200
    contacts = response.json()
    assert len(contacts) == 2
    assert contacts[0]["name"] == "Rakesh Pawar"
    assert contacts[0]["company_id"] == 1
    assert contacts[1]["name"] == "Tejas Shetty"
    assert contacts[1]["company_id"] == 1

def test_get_contacts_company_not_found():
    response = client.get("/companies/999/contacts")
    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found"

def test_get_contact():
    response = client.get("/companies/1/contacts/1")
    assert response.status_code == 200
    contact = response.json()
    assert contact["id"] == 1
    assert contact["name"] == "Rakesh Pawar"
    assert contact["email"] == "rakesh.pawar@sage.com"
    assert contact["primary"] == True
    assert contact["company_id"] == 1

def test_get_contact_company_not_found():
    response = client.get("/companies/999/contacts/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found"

def test_get_contact_not_found():
    response = client.get("/companies/1/contacts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"

def test_get_contact_wrong_company():
    response = client.get("/companies/2/contacts/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"

def test_get_contacts_empty_company():
    response = client.get("/companies/4/contacts")
    assert response.status_code == 200
    contacts = response.json()
    assert len(contacts) == 1
    assert contacts[0]["name"] == "Avirup Patra"