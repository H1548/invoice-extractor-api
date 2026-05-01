import json 


class Prompt(): 

    def createPrompt(self, payload_parser):
        
        developer_message =  """
        You are a data normalization assistant.

        Convert invoice parser output into our canonical invoice schema.

        Rules:
        - Use only evidence present in the parser output.
        - Never invent values.
        - Use null for missing or uncertain fields.
        - Normalize dates to ISO 8601 when possible.
        - Normalize currency codes when possible.
        - Return output that matches the schema exactly.
        """

        user_message = "Here is the invoice parser output as JSON.\n\n"f"{json.dumps(payload_parser, indent=2)}"
        final_message = [
            {
                'role': 'developer', 'content': developer_message
            },
            {
                'role' : 'user', 
                'content': user_message
            }
        ]
        return final_message
    
    def rePrompt(self, payload_parser, llm_output, issues):
        formatted_issues = "\n-".join(issues)
        
        developer_message =  f"""
        You previously converted invoice parser output into the canonical invoice schema, but the result failed validation.


        Read the issues with the previous output and correct the previous output using only the parser evidence.

        Rules:
        - Do not invent values.
        - Keep all valid fields unchanged unless they directly cause a listed issue.
        - use the issues listed to attend to correct field
        - If a field cannot be supported by parser evidence, set it to null.
        - if there are no issues then set issues to null
        - Return valid JSON matching the schema exactly.

        Validation issues:
        - {formatted_issues}

        Original parser output:
        {payload_parser}

        Previous output:
        {llm_output}
        """

        return developer_message
        