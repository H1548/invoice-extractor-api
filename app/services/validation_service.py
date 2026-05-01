from app.validators.totals import TotalAmountCheck
from app.validators.dates import CheckDates
from app.validators.currency import checkCurr
from app.validators.required_field import RequiredFields
from app.validators.schema import SchemaCheck

class ValidatationService(): 
    def __init__(self):
        self.totalCheck = TotalAmountCheck()
        self.dataCheck = CheckDates()
        self.currCheck = checkCurr()
        self.reqFieldCheck = RequiredFields()
        self.schemaCheck = SchemaCheck()

    def det_valcheck(self, pred_schema, pydantic_schema):
        pred_schema["issues"] = []
        schema = self.schemaCheck.schema_check(pred_schema, pydantic_schema)
        schema = self.totalCheck.totals_check(pred_schema)
        schema = self.dataCheck.check_date_corectness(pred_schema)
        schema = self.currCheck.checkCurrency(pred_schema)
        schema = self.reqFieldCheck.required_fields_check(pred_schema)
        return schema


