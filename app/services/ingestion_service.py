from app.domain.models.invoice import CanonicalInvoice


class Ingestion():
    def __init__(self):
        self.can_schema = CanonicalInvoice.model_json_schema()
    def recieve_input(self): 
            return self.can_schema

