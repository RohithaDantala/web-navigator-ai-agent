# agents/intent_parser.py
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class IntentParser:
    def __init__(self, llm_service):
        self.llm_service = llm_service

    async def parse_instruction(self, instruction: str) -> Dict[str, Any]:
        """
        Parse natural language instruction into structured intent
        """
        system_prompt = """
        You are an expert at parsing web navigation instructions. Convert natural language instructions into structured JSON format.

        Return JSON with these fields:
        - action: The main action (search, scrape, navigate, compare, etc.)
        - target: What to search/scrape for
        - website: Suggested website(s) to use (optional)
        - filters: Any filtering criteria
        - data_fields: Expected data fields to extract
        - limit: Number of results (if specified)
        - additional_actions: Any follow-up actions

        Examples:
        Input: "Search for gaming laptops under $1000 on Amazon and list top 5 with prices"
        Output: {
            "action": "search",
            "target": "gaming laptops",
            "website": "amazon.com",
            "filters": {"price": {"max": 1000}},
            "data_fields": ["title", "price", "rating", "link"],
            "limit": 5,
            "additional_actions": []
        }

        Input: "Find the latest iPhone reviews and extract ratings"
        Output: {
            "action": "search",
            "target": "latest iPhone reviews",
            "website": null,
            "filters": {},
            "data_fields": ["title", "rating", "review_text", "source"],
            "limit": 10,
            "additional_actions": ["extract_ratings"]
        }
        """

        try:
            response = await self.llm_service.generate_response(
                system_prompt, 
                f"Parse this instruction: {instruction}"
            )
            
            # Try to extract JSON from response
            parsed_intent = self._extract_json_from_response(response)
            
            if not parsed_intent:
                # Fallback to basic parsing
                parsed_intent = self._basic_parse(instruction)
            
            logger.info(f"Parsed intent: {parsed_intent}")
            return parsed_intent
            
        except Exception as e:
            logger.error(f"Intent parsing failed: {e}")
            return self._basic_parse(instruction)

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        try:
            # Find JSON in the response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
            return None
        except:
            return None

    def _basic_parse(self, instruction: str) -> Dict[str, Any]:
        """Basic fallback parsing"""
        instruction_lower = instruction.lower()
        
        # Determine action
        action = "search"
        if "scrape" in instruction_lower:
            action = "scrape"
        elif "compare" in instruction_lower:
            action = "compare"
        elif "navigate" in instruction_lower:
            action = "navigate"

        # Extract limit
        limit = 10
        for word in instruction.split():
            if word.isdigit():
                limit = int(word)
                break

        return {
            "action": action,
            "target": instruction,
            "website": None,
            "filters": {},
            "data_fields": ["title", "description", "link"],
            "limit": limit,
            "additional_actions": []
        }