# capabilities/input_validator.py

class InputValidator:
    async def validate(self, capability, inputs: dict) -> list:
        """
        Validates the extracted runtime arguments against the capability's 
        input schema requirements. Natively handles both flat dictionaries 
        and fully nested standard JSON-Schema formats.
        """
        missing_fields = []
        raw_schema = getattr(capability, "input_schema", {}) or {}
        
        # Ensure inputs tracking block is explicitly a dictionary container type
        if not isinstance(inputs, dict):
            inputs = {}

        # ─── EXTRACTION: DETECT JSON-SCHEMA STRUCTURE ───
        # If the schema is a standard JSON-Schema wrapper, unpack its active property layer
        if isinstance(raw_schema, dict) and "properties" in raw_schema:
            schema = raw_schema["properties"]
            # Extract standard JSON-Schema tracking arrays if present
            global_required = raw_schema.get("required", [])
        else:
            schema = raw_schema
            global_required = []

        # ─── ITERATE OVER ACTUAL ARGUMENT FIELDS ───
        for field, config in schema.items():
            
            # Evaluate if the specific parameter field is required
            if isinstance(config, dict):
                # Standard pattern: check local field flag OR global JSON-Schema required list
                is_required = config.get("required", False) or (field in global_required)
            else:
                # Flat pattern string layout: if it's explicitly listed, it's required
                is_required = True 

            # Check if the field value is genuinely missing, blank, or an empty placeholder
            val = inputs.get(field)
            if is_required:
                if field not in inputs or val is None or str(val).strip() in ["", "None", "--?"]:
                    missing_fields.append(field)
                
        return missing_fields