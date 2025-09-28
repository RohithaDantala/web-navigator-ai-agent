# agents/data_extractor.py
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)

class DataExtractor:
    def __init__(self):
        pass

    async def extract_data(self, execution_result: Dict[str, Any], expected_format: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process and structure extracted data
        """
        try:
            raw_data = execution_result.get("extracted_data", [])
            
            if not raw_data:
                return []

            # Clean and validate data
            cleaned_data = self._clean_data(raw_data)
            
            # Apply filters if specified
            filtered_data = self._apply_filters(cleaned_data, expected_format)
            
            # Sort and limit results
            final_data = self._finalize_results(filtered_data, expected_format)
            
            logger.info(f"Processed {len(final_data)} items from {len(raw_data)} raw items")
            return final_data
            
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            return []

    def _clean_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and normalize data"""
        cleaned = []
        
        for item in raw_data:
            if not isinstance(item, dict):
                continue
                
            clean_item = {}
            
            for key, value in item.items():
                if value is None or value == '':
                    continue
                    
                # Clean text values
                if isinstance(value, str):
                    cleaned_value = value.strip()
                    if cleaned_value:
                        clean_item[key] = cleaned_value
                else:
                    clean_item[key] = value
            
            # Only keep items with some content
            if len(clean_item) >= 2:
                cleaned.append(clean_item)
                
        return cleaned

    def _apply_filters(self, data: List[Dict[str, Any]], expected_format: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters based on expected format"""
        if not expected_format or not expected_format.get('filters'):
            return data
        
        filtered_data = []
        filters = expected_format.get('filters', {})
        
        for item in data:
            include_item = True
            
            # Apply price filters
            if 'price' in filters and 'price' in item:
                price_filter = filters['price']
                item_price = self._extract_numeric_value(item['price'])
                
                if item_price is not None:
                    if 'min' in price_filter and item_price < price_filter['min']:
                        include_item = False
                    if 'max' in price_filter and item_price > price_filter['max']:
                        include_item = False
            
            # Apply text filters
            if 'keywords' in filters:
                keywords = filters['keywords']
                if isinstance(keywords, list):
                    item_text = ' '.join(str(v).lower() for v in item.values())
                    if not any(keyword.lower() in item_text for keyword in keywords):
                        include_item = False
            
            if include_item:
                filtered_data.append(item)
                
        return filtered_data

    def _finalize_results(self, data: List[Dict[str, Any]], expected_format: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sort and limit results"""
        # Sort by relevance or specified criteria
        if expected_format.get('sort_by'):
            sort_field = expected_format['sort_by']
            if sort_field in ['price']:
                data.sort(key=lambda x: self._extract_numeric_value(x.get(sort_field, '0')) or 0)
        
        # Limit results
        limit = expected_format.get('limit', 50)
        return data[:limit]

    def _extract_numeric_value(self, text: str) -> float:
        """Extract numeric value from text (e.g., price)"""
        if not isinstance(text, str):
            return None
            
        import re
        # Remove currency symbols and extract numbers
        numbers = re.findall(r'[\d,]+\.?\d*', text.replace(',', ''))
        if numbers:
            try:
                return float(numbers[0])
            except:
                pass
        return None