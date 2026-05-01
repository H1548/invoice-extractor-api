# from domain.models.invoice import CanonicalInvoice
from app.services.parser_service import Parser
from app.services.ingestion_service import Ingestion
from app.services.llm_mapper_service import LLMMapper
from app.services.validation_service import ValidatationService
from app.services.review_service import ReviewInvoice
from app.domain.models.invoice import CanonicalInvoice
import json 



class Pipeline(): 
    def __init__(self):
        self.llm_mapper = LLMMapper()
        self.parser = Parser()
        self.pydantic_schema = CanonicalInvoice
        self.ingestion  = Ingestion()
        self.detValCheck = ValidatationService()
        self.reviewer = ReviewInvoice()
    def process_invoice(self, file):
        can_schema = self.ingestion.recieve_input()
        parsed_output = self.parser.parse_input(file)
        canoncial_invoice = self.llm_mapper.mapToSchema(parsed_output, can_schema)
        try:
            canonical_dict = json.loads(canoncial_invoice)
        except json.JSONDecodeError:
            return {
                "status": "error",
                "error_type": "invalid_llm_json",
                "raw_llm_output": canoncial_invoice,
                "needs_review": True
            }
        checked_canonical_invoice = self.detValCheck.det_valcheck(canonical_dict, self.pydantic_schema)
        reviewed_canonical_invoice = self.reviewer.review_loop(self.pydantic_schema, can_schema,checked_canonical_invoice, parsed_output, canoncial_invoice)
        
        

        return reviewed_canonical_invoice



