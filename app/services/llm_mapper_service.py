from app.adapters.llm.prompt import Prompt
from app.adapters.llm.openai_adapter import OpenAIAPI


class LLMMapper():
    def __init__(self):
        self.prompter = Prompt()
        
    def mapToSchema(self, payload_parser, can_schema, reprompt = False, llm_output = None, issues = None): 
        if not reprompt:
            message = self.prompter.createPrompt(payload_parser)
            llm = OpenAIAPI(can_schema)
            result = llm.get_completion(message)
            return result
        else: 
            message = self.prompter.rePrompt(payload_parser,llm_output, issues)
            llm = OpenAIAPI(can_schema)
            result = llm.get_completion(message)
            return result
    