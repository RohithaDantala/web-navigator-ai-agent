# agents/task_planner.py
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)

class TaskPlanner:
    def __init__(self, llm_service):
        self.llm_service = llm_service

    async def create_plan(self, parsed_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a step-by-step execution plan based on parsed intent
        """
        system_prompt = """
        You are an expert web navigation planner. Create detailed step-by-step plans for web automation.

        Return a JSON list of steps, where each step has:
        - step_type: "navigate", "search", "click", "extract", "wait", "scroll"
        - target: CSS selector, URL, or search term
        - action: Specific action to perform
        - data_fields: Fields to extract (for extract steps)
        - options: Additional options (timeout, retry, etc.)

        Example:
        For "Search for laptops on Amazon":
        [
            {
                "step_type": "navigate",
                "target": "https://amazon.com",
                "action": "open_page",
                "options": {"timeout": 10000}
            },
            {
                "step_type": "search",
                "target": "#twotabsearchtextbox",
                "action": "type_and_submit",
                "value": "laptops",
                "options": {"wait_for_load": true}
            },
            {
                "step_type": "extract",
                "target": "[data-component-type='s-search-result']",
                "action": "extract_products",
                "data_fields": ["title", "price", "rating", "link"],
                "options": {"limit": 10}
            }
        ]
        """

        try:
            prompt = f"Create execution plan for: {json.dumps(parsed_intent)}"
            response = await self.llm_service.generate_response(system_prompt, prompt)
            
            # Extract JSON from response
            plan = self._extract_plan_from_response(response)
            
            if not plan:
                plan = self._create_basic_plan(parsed_intent)
            
            logger.info(f"Created plan with {len(plan)} steps")
            return plan
            
        except Exception as e:
            logger.error(f"Plan creation failed: {e}")
            return self._create_basic_plan(parsed_intent)

    def _extract_plan_from_response(self, response: str) -> List[Dict[str, Any]]:
        """Extract plan from LLM response"""
        try:
            # Find JSON array in response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
            return None
        except:
            return None

    def _create_basic_plan(self, parsed_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a basic fallback plan"""
        plan = []
        
        # Determine target website
        website = parsed_intent.get('website') or 'google.com'
        if not website.startswith('http'):
            website = f'https://{website}'

        # Step 1: Navigate to website
        plan.append({
            "step_type": "navigate",
            "target": website,
            "action": "open_page",
            "options": {"timeout": 10000}
        })

        # Step 2: Search (if needed)
        if parsed_intent.get('action') == 'search':
            search_selector = 'input[name="q"], input[type="search"], #search'
            plan.append({
                "step_type": "search",
                "target": search_selector,
                "action": "type_and_submit",
                "value": parsed_intent.get('target', ''),
                "options": {"wait_for_load": True}
            })

        # Step 3: Extract data
        plan.append({
            "step_type": "extract",
            "target": "body",
            "action": "extract_content",
            "data_fields": parsed_intent.get('data_fields', ['title', 'description', 'link']),
            "options": {"limit": parsed_intent.get('limit', 10)}
        })

        return plan