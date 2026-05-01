class checkCurr():
    def checkCurrency(self, invoice): 
        currency = invoice.get("currency")
        VALID_CURRENCIES = {"USD", "GBP", "EUR", "AUD", "CAD", "JPY"}
        

        if not currency or len(currency) != 3: 
            invoice["issues"].append("Currecny code format is either not correct or is does not exist")
            # invoice["needs_review"] = True
        
        if currency not in VALID_CURRENCIES: 
            invoice["issues"].append("Not a valid currency")
            # invoice["needs_review"] = True
        return invoice

        