from app.adapters.parser.textract_adapter import analyze_invoice
from app.adapters.parser.parserFormatter import format_parser_output


class Parser(): 
    def parse_input(self, file):
        res = analyze_invoice(file)
        formatted_res = format_parser_output(res)
        return formatted_res
    


