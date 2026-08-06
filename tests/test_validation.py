from app.validators.currency import checkCurr
from copy import deepcopy

def test_invalid_currency_adds_issue_to_invoice():
    invoice = {
        "vendor_name": "WP DESK LTD", 
        "invoice_number":"122/11/2020",
        "invoice_date":"2020-11-05", 
        "due_date":"2020-11-19", 
        "total_amount":"36.00", 
        "sub_total":"30.00",
        "tax_amount":"6.00", 
        "shipping_amount":"null", 
        "currency":"asdfas",
        "purchase_order_number":"743",
        "line_items":[{
            "description":"Design Logo",
            "quantity":"1",
            "unit_price":"30.00",
            "amount":"30.00"
        }],
        "bank_payment_details":"Account number: 0000 1111 2222 3333 4444",
        "issues": []
    }

    original_invoice = deepcopy(invoice)

    currChecker = checkCurr()

    result = currChecker.checkCurrency(invoice)

    assert result["vendor_name"] == "WP DESK LTD"
    assert result["invoice_number"] == "122/11/2020"
    assert result["invoice_date"] == "2020-11-05"
    assert result["due_date"] == "2020-11-19"

    assert result["issues"] == ["Currecny code format is either not correct or is does not exist","Not a valid currency"]

    assert result["issues"] != original_invoice["issues"]