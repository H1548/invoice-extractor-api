class CheckDates(): 
    def check_date_corectness(self, cannonical_dict): 
        invoice_date = cannonical_dict.get("invoice_date")
        due_date = cannonical_dict.get("due_date")

        if not invoice_date: 
            cannonical_dict["issues"].append("invoice data does not exist check date of invoice")
            # cannonical_dict["needs_review"] = True
        elif not due_date:
            cannonical_dict["issues"].append("due date does not exist, confirm with vendor")
            # cannonical_dict["needs_review"] = True
        else: 
            if invoice_date > due_date: 
                cannonical_dict["issues"].append("Invoice/issue data is after due date, not logical")
                # cannonical_dict["needs_review"] = True
        
        return cannonical_dict