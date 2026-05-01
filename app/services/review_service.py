from app.services.reprompt_service import Reprompter
from app.services.validation_service import ValidatationService

class ReviewInvoice():
    def __init__(self): 
        self.reprompter = Reprompter()
        self.valCheck = ValidatationService()
    def review_loop(self,pydantic_schema, can_schema, val_can_dict, parser_output, llm_output):

        tries = 0
        total_retries = 2
# load dict[issues] if it exists 
# extract issues
# then pass it over to the reprompt file
# then validate again, set limit
        while tries < total_retries:

            if not val_can_dict["issues"]: 
                return val_can_dict
            
            issues = val_can_dict["issues"]

            modified_schema = self.reprompter.execute_reprompt(can_schema, parser_output, llm_output, issues)
            val_can_dict = self.valCheck.det_valcheck(modified_schema, pydantic_schema)
            tries += 1
        val_can_dict["needs_review"] = True
        return {"cannonical_output":val_can_dict}



    
        
        

        
