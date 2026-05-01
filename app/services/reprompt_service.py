from app.services.llm_mapper_service import LLMMapper
import json 

class Reprompter(): 
    def __init__(self):
        self.llm = LLMMapper()
    def execute_reprompt(self, can_schema,parser_output, llm_output, issues): 
        # take the inputs and call the llm function 
        # output the llm output
        # return the llms output
        print("reprompting modeL....")
        modifeid_schema = self.llm.mapToSchema(parser_output,can_schema,reprompt=True, llm_output=llm_output, issues=issues)
        modifeid_schema_dict = json.loads(modifeid_schema)
        
        return modifeid_schema_dict