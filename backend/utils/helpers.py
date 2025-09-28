# utils/helpers.py
import re
import hashlib
import asyncio
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

class WebNavigatorHelpers:
    @staticmethod
    def generate_task_id(instruction: str) -> str:
        """Generate unique task ID from instruction"""
        hash_object = hashlib.md5(instruction.encode())
        return f"task_{hash_object.hexdigest()[:8]}"

    @staticmethod
    def clean_url(url: str, base_url: str = None) -> str:
        """Clean and validate URL"""
        if not url:
            return ""
        
        # Remove extra whitespace
        url = url.strip()
        
        # Handle relative URLs
        if url.startswith('/') and base_url:
            return urljoin(base_url, url)
        elif not url.startswith('http') and base_url:
            return urljoin(base_url, url)
        elif not url.startswith('http'):
            return f"https://{url}"
        
        return url

    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""

    @staticmethod
    def clean_text(text: str, max_length: int = None) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters
        cleaned = re.sub(r'[^\w\s\-\.,$%]', '', cleaned)
        
        # Limit length if specified
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length].strip()
        
        return cleaned

    @staticmethod
    def extract_price_number(price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove currency symbols and extract numbers
        numbers = re.findall(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if numbers:
            try:
                return float(numbers[0])
            except:
                pass
        return None

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def detect_content_type(text: str) -> str:
        """Detect the type of content based on text patterns"""
        text_lower = text.lower()
        
        if any(currency in text for currency in [',', '€', '£', '₹', 'usd', 'eur']):
            return "product"
        elif any(word in text_lower for word in ['article', 'news', 'blog', 'post']):
            return "article"
        elif any(word in text_lower for word in ['contact', 'phone', 'email', 'address']):
            return "contact"
        elif any(word in text_lower for word in ['review', 'rating', 'stars']):
            return "review"
        else:
            return "general"

    @staticmethod
    async def retry_async(func, max_attempts: int = 3, delay: float = 1.0, *args, **kwargs):
        """Retry async function with exponential backoff"""
        for attempt in range(max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise e
                
                wait_time = delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

    @staticmethod
    def validate_selector(selector: str) -> bool:
        """Validate CSS selector"""
        try:
            # Basic validation for common CSS selectors
            if not selector or len(selector.strip()) == 0:
                return False
            
            # Check for dangerous selectors
            dangerous_patterns = ['javascript:', 'eval(', 'alert(']
            for pattern in dangerous_patterns:
                if pattern in selector.lower():
                    return False
            
            return True
        except:
            return False