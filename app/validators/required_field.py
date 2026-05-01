class RequiredFields(): 
    def required_fields_check(self, invoice): 

        for k in invoice: 
            if invoice[k] == None: 
                invoice["issues"].append(f"{k}'s value is missing/empty")
                # invoice["needs_review"] = True
        return invoice
        

            