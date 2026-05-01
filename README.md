# Invoice Extraction & Validation API

An AI-assisted invoice processing system that extracts structured invoice data from PDFs and invoice images, maps the output into a strict schema, and applies deterministic validation checks before returning the final result through a FastAPI endpoint.

The goal of this project is not just to extract text from invoices, but to make the output reliable enough for downstream workflows by combining document parsing, LLM-based schema mapping, validation rules, and review flags.

---

## Overview

Invoices often come in different layouts, formats, and quality levels. Some are PDFs, some are scanned images, and key fields such as invoice numbers, dates, totals, tax amounts, supplier details, and line items may appear in different places.

This project handles that by using:

1. **Azure Document Intelligence** to parse PDFs/images and extract raw invoice content.
2. **OpenAI structured outputs** to map the extracted content into a strict canonical invoice schema.
3. **Validation checks** to verify the consistency and reliability of the extracted data.
4. **FastAPI** to expose the workflow as an API.
5. **Review logic** to flag invoices that remain inconsistent after retry attempts.

---

## Key Features

- Accepts invoice **PDFs** and **image files**
- Uses **Azure Document Intelligence** for document parsing
- Uses **OpenAI structured outputs** for schema-based extraction
- Returns invoice data in a strict structured format
- Applies deterministic validation checks
- Supports up to **2 re-prompt attempts** when validation fails
- Flags problematic invoices with `needs_review: true`
- Exposes the workflow through a **FastAPI API**
- Designed with reliability, validation, and downstream usability in mind

---

## Tech Stack 
- Python
- FastAPI
- Azure Document Intelligence
- OpenAI API
- Pydantic
- Docker
- Azure Container Apps

## Validation Checks

The system performs several validation checks after the invoice has been mapped into the canonical schema.

Current validation includes:

- **Schema validation**
  - Ensures the output follows the expected structure
  - Checks that required fields exist or are correctly set to `null`

- **Date validation**
  - Checks invoice dates and due dates
  - Identifies invalid or inconsistent date formats

- **Currency validation**
  - Checks that currency values are valid and consistent where possible

- **Total reconciliation**
  - Compares subtotal, tax, and total values
  - Flags cases where totals do not reconcile correctly

- **Low-confidence / uncertainty handling**
  - Flags uncertain or inconsistent outputs for review

- **Golden Evaluation Dataset**
- pipeline tested on 18 unique examples was measured at 2 layers: 
    - Field level - How accurate the pipeline is at mapping the correct information to the correct fields
    - Business - The overall usability of the pipeline's output (Do critical field exist in the output and the overall success of the output)

If validation fails, the system can re-prompt the LLM up to **2 times**.  
If the output still fails validation after those attempts, the response is returned with:

```json
"needs_review": true
```
This ensures questionable invoices are not silently accepted.

## Example Workflow
```text
            Invoice PDF/Image
                   ↓
        Azure Document Intelligence
                   ↓
        Raw extracted invoice content
                   ↓
       OpenAI structured output mapping
                   ↓
          Canonical invoice schema
                   ↓
            Validation checks
                   ↓
        Retry/re-prompt if needed
                   ↓
    Final JSON response or needs_review = true
```
## Example Successful API Response
```json
{
  "cannonical_output": {
    "vendor_name": "Bardays PLC",
    "invoice_number": "12345",
    "invoice_date": "2021-05-29",
    "due_date": "2021-06-29",
    "total_amount": 4160,
    "sub_total": 3312,
    "tax_amount": 828,
    "shipping_amount": 20,
    "currency": "GBP",
    "purchase_order_number": "A1230",
    "line_items": [
      {
        "description": "Example product",
        "quantity": 5,
        "unit_price": 60,
        "amount": 360
      },
      {
        "description": "Example work",
        "quantity": 10,
        "unit_price": 105,
        "amount": 1260
      },
      {
        "description": "Example work",
        "quantity": 10,
        "unit_price": 105,
        "amount": 1260
      },
      {
        "description": "Example work",
        "quantity": 10,
        "unit_price": 105,
        "amount": 1260
      }
    ],
    "bank_payment_details": null,
    "warnings": [],
    "needs_review": false,
    "confidence": {
      "vendor_name": 0.946,
      "invoice_number": 0.974,
      "invoice_date": 0.974,
      "due_date": 0.974,
      "total_amount": 0.919,
      "tax_amount": 0.942,
      "shipping_amount": 0.723,
      "currency": 0.874,
      "purchase_order_number": 0.854,
      "bank_payment_details": 0.934,
      "line_items": null
    },
    "issues": []
  }
}
```

## Example Successful API Response, With Invoice Issues
```json
{
  "cannonical_output": {
    "vendor_name": "Bardays PLC",
    "invoice_number": "12345",
    "invoice_date": "2021-05-29",
    "due_date": "2021-06-29",
    "total_amount": 4140,
    "sub_total": 3312,
    "tax_amount": 828,
    "shipping_amount": null,
    "currency": "GBP",
    "purchase_order_number": null,
    "line_items": [
      {
        "description": "Example product",
        "quantity": 5,
        "unit_price": 60,
        "amount": 360
      },
      {
        "description": "Example work",
        "quantity": 10,
        "unit_price": 105,
        "amount": 1260
      },
      {
        "description": "Example work",
        "quantity": 10,
        "unit_price": 105,
        "amount": 1260
      },
      {
        "description": "Example work",
        "quantity": 10,
        "unit_price": 105,
        "amount": 1260
      }
    ],
    "bank_payment_details": null,
    "warnings": [
      "TaxDetails is present but contains no usable data in the parser output."
    ],
    "needs_review": true,
    "confidence": {
      "vendor_name": 0.346,
      "invoice_number": 0.974,
      "invoice_date": 0.974,
      "due_date": 0.974,
      "total_amount": 0.319,
      "tax_amount": 0.942,
      "shipping_amount": null,
      "currency": null,
      "purchase_order_number": null,
      "bank_payment_details": null,
      "line_items": null
    },
    "issues": [
      "The sum of items bought does not total to the subtotal.",
      "Shipping is missing",
      "shipping_amount's value is missing/empty",
      "purchase_order_number's value is missing/empty",
      "bank_payment_details's value is missing/empty"
    ]
  }
}
```

## Project Structure
```text
InvoiceExtractor/
│
├── app/
|   ├── llm/ 
|        ├── openai_adapter.py      # OpenAI API class logic
|        ├── prompt.py              # prompt logic for LLM
|    ├── adapter/
|        ├── parerFomatter.py       # Cleans parser's output
|        ├── textract_adapter.py    # Azure document intelligence logic
|    ├── api/ 
|        ├──  __init__.py
|        ├── main.py                # Entry point of API 
|    ├── domain/ 
|        ├── models
|            ├── inoivce.py         # Canonical Schema logic    
|    ├── services/
|        ├── __init__.py
|        ├── ingestion_service.py
|        ├── llm_maper_service.py 
|        ├── parser_service.py
|        ├── pipeline_service.py
|        ├── reprompt_service.py
|        ├── review_service.py
|        ├── validation_service.py   
|    ├── validators/
|        ├── currency.py
|        ├── dates.py
|        ├── required_field.py
|        ├── schema.py 
|        ├── totals.py
|    ├── __init__.py
├── evals/ 
|    ├── datasets
|        ├── labelled
|          ├── 18 pairs (image/pdf, json label) of invoice examples
|    ├── runners
|        ├── metrics.py
|        ├── run_eval.py
├── .dockerignore
├── .env
├── .gitignore
├── .python-version
├── Dockerfile
├── pyproject.toml
├── README.md
├── requirements.txt
├── uv.lock
```

## Setup 

### 1. Clone the repository
```bash
git clone https://github.com/H1548/invoice-extractor-api
cd InvoiceExtractor
```
### 2. Create a virtual environment
```bash
python -m venv venv
```
Activate it 
```bash
# Windows
venv\Scripts\activate
```
```bash
# Mac/Linux
source venv/bin/activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
#### 4. Create .env file
```env
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your_azure_document_intelligence_endpoint
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_azure_document_intelligence_key

OPENAI_API_KEY=your_openai_api_key
```
## Running Locally
```bash
uvicorn app.api.main:app --reload
```
Open the interactive API docs: http://yourlocalhost/docs

# Deployment 

The API has been deployed using Azure Container Apps.

Deployment flow: 
```text 
FastAPI app
   ↓
Docker container
   ↓
Azure Container Apps
   ↓
Cloud-hosted invoice extraction API
```

## Limitations
- Validation currently focuses on schema, dates, currency, and total reconciliation
- Complex invoice layouts may produce incomplete or uncertain outputs
- The system depends on the quality of Azure Document Intelligence extraction
- Human review is still required for invoices flagged with 'needs_review: true'

## Future Improvements

Planned improvements include:

Add a larger labelled evaluation set
Improve field-level accuracy tracking
Add more validation rules for supplier details and line items
Add authentication for API access
Add logging and monitoring for production use
Build a simple frontend interface for uploading invoices
Store extraction results in a database
Add batch processing for multiple invoices

## Status 

Current status: Working prototype deployed to Azure Container Apps

The system can accept invoice PDFs/images, parse them using Azure Document Intelligence, map outputs into a structured schema using OpenAI structured outputs, validate the result, retry failed outputs, and flag uncertain invoices for review.

## Author

Hasan Farooq  
MSc Cybersecurity | Machine Learning | AI 