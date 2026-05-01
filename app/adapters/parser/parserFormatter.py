
from app.adapters.parser.textract_adapter import analyze_invoice 
def get_currency_amount(field):
    if not field or not getattr(field, "value_currency", None):
        return None
    return field.value_currency.amount


def get_string(field):
    if not field:
        return None
    return getattr(field, "value_string", None)


def get_number(field):
    if not field:
        return None
    return getattr(field, "value_number", None)


def get_date(field):
    if not field:
        return None
    value = getattr(field, "value_date", None)
    return str(value) if value else None


def format_parser_output(result):
    
    output = {"documents": []}

    for doc in result.documents:
        doc_payload = {
            "doc_type": doc.doc_type,
            "fields": {},
            "line_items": [],
        }

        for field_name, field_value in doc.fields.items():
            if field_name == "Items":
                extracted_items = []

                if not getattr(field_value, "value_array", None):
                    doc_payload["fields"][field_name] = []
                    continue

                for item in field_value.value_array:
                    item_obj = getattr(item, "value_object", None)
                    if not item_obj:
                        continue

                    description = get_string(item_obj.get("Description"))
                    if description: 
                        description = description.replace("\n", " ").strip()
                    extracted_items.append({
                        "description": description,
                        "quantity": get_number(item_obj.get("Quantity")),
                        "unit_price": get_currency_amount(item_obj.get("UnitPrice")),
                        "amount": get_currency_amount(item_obj.get("Amount")),
                        "product_code": get_string(item_obj.get("ProductCode")),
                        "unit": get_string(item_obj.get("Unit")),
                        "tax": get_currency_amount(item_obj.get("Tax")),
                        "tax_rate": get_string(item_obj.get("TaxRate")),
                        "date": get_date(item_obj.get("Date")),
                    })

                doc_payload["line_items"] = extracted_items
                continue

            simplified_field = {
                "value_type": field_value.type.value if getattr(field_value, "type", None) else None,
                "content": getattr(field_value, "content", None),
                "confidence": getattr(field_value, "confidence", None),
            }

            if hasattr(field_value, "value_string"):
                simplified_field["value_string"] = field_value.value_string

            if hasattr(field_value, "value_number"):
                simplified_field["value_number"] = field_value.value_number

            if hasattr(field_value, "value_date"):
                simplified_field["value_date"] = (
                    str(field_value.value_date) if field_value.value_date else None
                )

            if hasattr(field_value, "value_currency") and field_value.value_currency:
                simplified_field["value_currency"] = {
                    "amount": field_value.value_currency.amount,
                    "currency_symbol": field_value.value_currency.currency_symbol,
                    "currency_code": getattr(field_value.value_currency, "currency_code", None),
                }

            doc_payload["fields"][field_name] = simplified_field

        output["documents"].append(doc_payload)

    return output

        