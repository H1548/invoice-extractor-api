class SchemaCheck():
    def schema_check(self, canonical_dict, canconical_inv):
        try:
            canonical_dict = canconical_inv.model_validate(canonical_dict)
        except Exception as e: 
            canonical_dict["issues"].append(f"Schema validation failed: {str(e)}")
        return canonical_dict