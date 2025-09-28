# agents/browser_controller.py
from typing import Dict, List, Any, Optional
from playwright.async_api import Browser, Page
import asyncio
import logging

logger = logging.getLogger(__name__)

class BrowserController:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.current_page: Optional[Page] = None

    async def execute_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute the navigation plan step by step
        """
        try:
            self.current_page = await self.browser.new_page()
            results = {
                "pages_visited": [],
                "extracted_data": [],
                "step_results": []
            }

            for i, step in enumerate(plan):
                logger.info(f"Executing step {i+1}: {step.get('step_type')}")
                
                try:
                    step_result = await self._execute_step(step)
                    results["step_results"].append({
                        "step": i+1,
                        "type": step.get('step_type'),
                        "success": True,
                        "result": step_result
                    })
                    
                    # Collect extracted data
                    if step.get('step_type') == 'extract' and step_result:
                        results["extracted_data"].extend(step_result)
                        
                except Exception as e:
                    logger.error(f"Step {i+1} failed: {e}")
                    results["step_results"].append({
                        "step": i+1,
                        "type": step.get('step_type'),
                        "success": False,
                        "error": str(e)
                    })

            await self.current_page.close()
            return results
            
        except Exception as e:
            logger.error(f"Plan execution failed: {e}")
            if self.current_page:
                await self.current_page.close()
            raise

    async def _execute_step(self, step: Dict[str, Any]) -> Any:
        """Execute a single step"""
        step_type = step.get('step_type')
        target = step.get('target')
        action = step.get('action')
        options = step.get('options', {})

        if step_type == "navigate":
            return await self._navigate(target, options)
        elif step_type == "search":
            return await self._search(target, step.get('value'), options)
        elif step_type == "click":
            return await self._click(target, options)
        elif step_type == "extract":
            return await self._extract(target, step.get('data_fields', []), options)
        elif step_type == "wait":
            return await self._wait(options)
        elif step_type == "scroll":
            return await self._scroll(options)
        else:
            logger.warning(f"Unknown step type: {step_type}")
            return None

    async def _navigate(self, url: str, options: Dict) -> Dict:
        """Navigate to a URL"""
        timeout = options.get('timeout', 30000)
        await self.current_page.goto(url, timeout=timeout)
        await self.current_page.wait_for_load_state('networkidle')
        
        return {
            "url": self.current_page.url,
            "title": await self.current_page.title()
        }

    async def _search(self, selector: str, query: str, options: Dict) -> Dict:
        """Perform search operation"""
        try:
            # Try multiple common search selectors
            selectors = [selector, 'input[name="q"]', 'input[type="search"]', '#search', '.search-input']
            
            search_input = None
            for sel in selectors:
                try:
                    search_input = await self.current_page.wait_for_selector(sel, timeout=5000)
                    if search_input:
                        break
                except:
                    continue
            
            if not search_input:
                raise Exception("Search input not found")
            
            await search_input.fill(query)
            await search_input.press('Enter')
            
            if options.get('wait_for_load'):
                await self.current_page.wait_for_load_state('networkidle')
            
            return {"query": query, "success": True}
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    async def _click(self, selector: str, options: Dict) -> Dict:
        """Click an element"""
        element = await self.current_page.wait_for_selector(selector, timeout=options.get('timeout', 10000))
        await element.click()
        return {"clicked": selector}

    async def _extract(self, selector: str, data_fields: List[str], options: Dict) -> List[Dict]:
        """Extract data from page"""
        try:
            limit = options.get('limit', 10)
            extracted_data = []

            # Wait for content to load
            await self.current_page.wait_for_timeout(2000)

            # Try to find elements
            elements = await self.current_page.query_selector_all(selector)
            
            if not elements:
                # Fallback to common selectors for different types of content
                fallback_selectors = [
                    'article', '.result', '.product', '.item', 
                    'h3', 'h2', '.title', '[data-testid]'
                ]
                for fb_sel in fallback_selectors:
                    elements = await self.current_page.query_selector_all(fb_sel)
                    if elements:
                        break

            for i, element in enumerate(elements[:limit]):
                if not element:
                    continue
                    
                item_data = {}
                
                # Extract different types of data
                for field in data_fields:
                    try:
                        if field == 'title':
                            title = await self._extract_title(element)
                            if title:
                                item_data['title'] = title
                        elif field == 'price':
                            price = await self._extract_price(element)
                            if price:
                                item_data['price'] = price
                        elif field == 'link':
                            link = await self._extract_link(element)
                            if link:
                                item_data['link'] = link
                        elif field == 'description':
                            desc = await self._extract_description(element)
                            if desc:
                                item_data['description'] = desc
                        elif field == 'rating':
                            rating = await self._extract_rating(element)
                            if rating:
                                item_data['rating'] = rating
                    except Exception as e:
                        logger.debug(f"Failed to extract {field}: {e}")

                if item_data:
                    extracted_data.append(item_data)

            logger.info(f"Extracted {len(extracted_data)} items")
            return extracted_data

        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            return []

    async def _extract_title(self, element) -> Optional[str]:
        """Extract title from element"""
        try:
            # Try different title selectors
            selectors = ['h1', 'h2', 'h3', '.title', '[data-testid*="title"]', 'a', '.product-title']
            
            for sel in selectors:
                title_elem = await element.query_selector(sel)
                if title_elem:
                    text = await title_elem.text_content()
                    if text and text.strip():
                        return text.strip()
            
            # Fallback to element text
            text = await element.text_content()
            if text and len(text.strip()) > 5:
                return text.strip()[:200]  # Limit length
                
        except:
            pass
        return None

    async def _extract_price(self, element) -> Optional[str]:
        """Extract price from element"""
        try:
            # Price-specific selectors
            selectors = [
                '.price', '.cost', '[data-testid*="price"]',
                '.amount', '.currency', '.price-current'
            ]
            
            for sel in selectors:
                price_elem = await element.query_selector(sel)
                if price_elem:
                    text = await price_elem.text_content()
                    if text and ('$' in text or '₹' in text or '€' in text or '£' in text):
                        return text.strip()
                        
        except:
            pass
        return None

    async def _extract_link(self, element) -> Optional[str]:
        """Extract link from element"""
        try:
            # Try to find link
            link_elem = await element.query_selector('a')
            if link_elem:
                href = await link_elem.get_attribute('href')
                if href:
                    # Make absolute URL
                    if href.startswith('/'):
                        base_url = f"{self.current_page.url.split('/')[0]}//{self.current_page.url.split('/')[2]}"
                        href = base_url + href
                    elif not href.startswith('http'):
                        href = f"{self.current_page.url.rstrip('/')}/{href}"
                    return href
                    
        except:
            pass
        return None

    async def _extract_description(self, element) -> Optional[str]:
        """Extract description from element"""
        try:
            selectors = ['.description', '.summary', 'p', '.content', '.excerpt']
            
            for sel in selectors:
                desc_elem = await element.query_selector(sel)
                if desc_elem:
                    text = await desc_elem.text_content()
                    if text and len(text.strip()) > 10:
                        return text.strip()[:500]  # Limit length
                        
        except:
            pass
        return None

    async def _extract_rating(self, element) -> Optional[str]:
        """Extract rating from element"""
        try:
            selectors = ['.rating', '.stars', '[data-testid*="rating"]', '.review-score']
            
            for sel in selectors:
                rating_elem = await element.query_selector(sel)
                if rating_elem:
                    text = await rating_elem.text_content()
                    if text and any(char.isdigit() for char in text):
                        return text.strip()
                        
        except:
            pass
        return None

    async def _wait(self, options: Dict) -> Dict:
        """Wait for specified time or condition"""
        timeout = options.get('timeout', 3000)
        await self.current_page.wait_for_timeout(timeout)
        return {"waited": timeout}

    async def _scroll(self, options: Dict) -> Dict:
        """Scroll the page"""
        direction = options.get('direction', 'down')
        amount = options.get('amount', 1000)
        
        if direction == 'down':
            await self.current_page.evaluate(f'window.scrollBy(0, {amount})')
        else:
            await self.current_page.evaluate(f'window.scrollBy(0, -{amount})')
            
        return {"scrolled": direction, "amount": amount}
