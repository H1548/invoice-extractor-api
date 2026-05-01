from decimal import Decimal
class TotalAmountCheck():

    def totals_check(self, cannonical_dict):
        
        subtotal = cannonical_dict.get("sub_total")
        tax = cannonical_dict.get("tax_amount")
        shipping = cannonical_dict.get("shipping_amount")
        total = cannonical_dict.get("total_amount")

        item_amounts = [item.get("amount", Decimal("0.00")) for item in cannonical_dict.get("line_items", [])]
        item_amounts_total = sum(item_amounts)
        if subtotal:
            if abs(subtotal - item_amounts_total) > 0.01:
                cannonical_dict["issues"].append("The sum of items bought does not total to the subtotal.")
                # cannonical_dict["needs_review"] = True


        if shipping is not None and tax is not None and total is not None and subtotal is not None:
            expected_total = subtotal + tax + shipping
            if abs(expected_total - total) > 0.01:
                cannonical_dict["issues"].append("Totals do not reconcile.")
                # cannonical_dict["needs_review"] = True
        elif not shipping: 
             cannonical_dict["issues"].append("Shipping is missing")
            #  cannonical_dict["needs_review"] = True
        elif not tax: 
            cannonical_dict["issues"].append("tax is missing")
            # cannonical_dict["needs_review"] = True
        elif not total:
            cannonical_dict["issues"].append("total is missing")
            # cannonical_dict["needs_review"] = True
        return cannonical_dict

            