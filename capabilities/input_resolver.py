import json
from typing import Dict, Any

class InputResolver:
    def __init__(self, get_llm_factory):
        """
        Inject the factory function directly.
        Args:
            get_llm_factory: The `get_llm` function imported from your config file.
        """
        self.get_llm_factory = get_llm_factory

    async def resolve(self, query: str, capability: Any, context: Any) -> Dict[str, Any]:
        """
        Uses LangChain models to parse text inputs against the capability schema.
        """
        resolved_inputs = {}

        # 1. Pull pre-resolved arguments from the OS context definition
        for field in capability.input_schema.keys():
            if hasattr(context, "get_input"):
                value = context.get_input(field)
            elif isinstance(context, dict):
                value = context.get(field)
            else:
                value = getattr(context, field, None)
                
            if value is not None:
                resolved_inputs[field] = value

        # 2. Extract out parameter schema definitions for prompt visualization
        schema_instruction = json.dumps(capability.input_schema, indent=2)

        # 3. Create a rigid, non-conversational system extraction blueprint
        # ─── AGGRESSIVELY SIMPLIFIED LOCAL MODEL PROMPT ENGINE ───
        prompt = (
            "<|im_start|>system\n"
            "You are a strict JSON extraction microservice. Analyze the user text and map variables to the schema.\n\n"
            f"TARGET SCHEMA:\n{schema_instruction}\n\n"
            f"PRE-RESOLVED INPUTS:\n{json.dumps(resolved_inputs)}\n\n"
            "CRITICAL RULES:\n"
            "1. Output your answer strictly wrapped inside an explicit ---JSON--- block.\n"
            "2. Do NOT write introductions, notes, markdown formatting, or formatting descriptions.\n"
            "3. If a parameter is missing or undefined, omit its key completely.\n\n"
            "EXACT OUTPUT TEMPLATE FORMAT:\n"
            "---JSON---\n"
            "{\n"
            "  \"parameter_name\": \"extracted_value\"\n"
            "}\n"
            "---JSON---<|im_end|>\n"
            f"<|im_start|>user\nINPUT QUERY TO PARSE: \"{query}\"<|im_end|>\n"
            "<|im_start|>assistant\n"
        )

        try:
            llm = self.get_llm_factory()
            if hasattr(llm, "temperature"):
                llm.temperature = 0.0

            response = await llm.ainvoke(prompt)
            raw_content = response.content.strip()

            # ─── ADVANCED ANCHOR BLOCK SLICER ───
            # If the small model wrote conversational text but included our anchor, slice it!
            if "---JSON---" in raw_content:
                parts = raw_content.split("---JSON---")
                # Grab the content sandwiched exactly between the markers
                if len(parts) >= 3:
                    raw_content = parts[1].strip()
                else:
                    # Fallback if it only wrote one marker
                    raw_content = parts[-1].strip()

            # Defensive strip for accidental markdown code fences
            if "```" in raw_content:
                raw_content = raw_content.split("```")[1]
                if raw_content.startswith("json"):
                    raw_content = raw_content[4:]
                raw_content = raw_content.strip()

            # Find the true JSON boundaries if characters leak
            start_idx = raw_content.find("{")
            end_idx = raw_content.rfind("}")
            if start_idx != -1 and end_idx != -1:
                raw_content = raw_content[start_idx:end_idx + 1]

            extracted_json = json.loads(raw_content)

            # Normalization mapping back to capability schema
            cleaned_json = {str(k).strip().lower(): v for k, v in extracted_json.items()}
            for field in capability.input_schema.keys():
                field_lower = field.lower()
                if field_lower in cleaned_json and cleaned_json[field_lower] is not None:
                    resolved_inputs[field] = cleaned_json[field_lower]

        except Exception as e:
            print(f"[INPUT RESOLVER WARNING] Failed parsing local model payload: {str(e)}")
            
        return resolved_inputs