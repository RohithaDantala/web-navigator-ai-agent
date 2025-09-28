# agents/web_navigator_selenium.py
import asyncio
import time
import json
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import logging

logger = logging.getLogger(__name__)

class SeleniumWebNavigator:
    def __init__(self):
        self.driver = None

    async def initialize(self, headless=True):
        """Initialize Selenium WebDriver with Chrome 140+ compatibility"""
        try:
            chrome_options = Options()
            
            # Essential options for Chrome 140+
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--remote-allow-origins=*")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            chrome_options.add_argument("--window-size=1920,1080")
            
            if headless:
                chrome_options.add_argument("--headless=new")
            
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.208 Safari/537.36")
            
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            logger.info("Setting up ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Test connection
            logger.info("Testing browser connection...")
            self.driver.get("https://httpbin.org/ip")
            time.sleep(2)
            
            logger.info("Selenium WebDriver initialized successfully with Chrome 140+ compatibility")
            
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            raise

    async def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver cleaned up successfully")
            except:
                pass

    async def execute_task(self, instruction: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a web navigation task"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting task execution for: {instruction}")
            
            if not self.driver:
                raise Exception("WebDriver not initialized")
                
            try:
                self.driver.current_url
            except Exception as e:
                logger.error(f"WebDriver session died: {e}")
                raise Exception("WebDriver session lost")
            
            parsed_intent = await self._parse_instruction(instruction)
            logger.info(f"Parsed intent: {parsed_intent}")
            
            if 'amazon' in instruction.lower():
                logger.info("Executing Amazon search")
                results = await self._search_amazon(parsed_intent)
            else:
                logger.info("Executing Google search")
                results = await self._search_google(parsed_intent)
            
            execution_time = time.time() - start_time
            logger.info(f"Task completed. Found {len(results)} results in {execution_time:.2f}s")
            
            return {
                "data": results,
                "message": f"Successfully found {len(results)} results for: {instruction}",
                "execution_time": execution_time,
                "success": len(results) > 0
            }
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                "data": [],
                "message": f"Task failed: {str(e)}",
                "execution_time": time.time() - start_time,
                "success": False
            }

    async def _parse_instruction(self, instruction: str) -> Dict[str, Any]:
        """Basic instruction parsing"""
        instruction_lower = instruction.lower()
        
        price_range = None
        if 'under' in instruction_lower or 'below' in instruction_lower:
            words = instruction_lower.split()
            for i, word in enumerate(words):
                if word in ['under', 'below'] and i + 1 < len(words):
                    try:
                        price_range = int(''.join(filter(str.isdigit, words[i + 1])))
                    except:
                        pass
        
        return {
            "query": instruction,
            "target_site": "amazon" if "amazon" in instruction_lower else "google",
            "data_fields": ["title", "price", "link", "rating"],
            "limit": 8,
            "price_range": price_range
        }

    async def _dismiss_amazon_popups(self):
        """Handle all common Amazon popups"""
        popup_selectors = [
            # Location popup
            "[data-action-type='DISMISS']",
            ".a-button-close",
            "#nav-global-location-popover-link",
            
            # Cookie banner
            "#sp-cc-accept",
            "#sp-cc-rejectall-link",
            
            # Prime popup
            ".a-popover-close",
            
            # General close buttons
            "[aria-label='Close']",
            ".a-icon-close",
        ]
        
        for selector in popup_selectors:
            try:
                element = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                element.click()
                logger.info(f"Dismissed popup with selector: {selector}")
                time.sleep(1)
            except:
                continue

    async def _search_amazon(self, parsed_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Amazon for products with robust error handling"""
        results = []
        
        try:
            logger.info("Navigating to Amazon...")
            self.driver.get("https://www.amazon.com")
            time.sleep(4)  # Give more time for page load
            
            # Dismiss any popups
            await self._dismiss_amazon_popups()
            
            logger.info("Looking for search box...")
            
            # Try multiple search box selectors and approaches
            search_box = None
            search_selectors = [
                "#twotabsearchtextbox",
                "input[type='text'][name='field-keywords']",
                "input[placeholder*='Search']",
                "#nav-search-bar-form input"
            ]
            
            for selector in search_selectors:
                try:
                    search_box = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if search_box:
                        logger.info(f"Found search box with selector: {selector}")
                        break
                except:
                    continue
            
            if not search_box:
                logger.error("Could not find Amazon search box")
                return []
            
            # Clean up search query
            search_query = parsed_intent["query"]
            search_query = search_query.replace("Search for", "").replace("search for", "")
            search_query = search_query.replace("on Amazon", "").replace("Amazon", "")
            search_query = search_query.replace("under $1500", "").strip()
            
            if not search_query:
                search_query = "gaming laptops"
            
            logger.info(f"Searching for: '{search_query}'")
            
            # Try clicking first, then clear and type
            try:
                search_box.click()
                time.sleep(1)
            except:
                pass
            
            try:
                search_box.clear()
                search_box.send_keys(search_query)
                search_box.send_keys(Keys.RETURN)
            except ElementNotInteractableException:
                # Try JavaScript approach if clicking fails
                self.driver.execute_script("arguments[0].value = arguments[1];", search_box, search_query)
                self.driver.execute_script("arguments[0].form.submit();", search_box)
            
            logger.info("Waiting for search results...")
            time.sleep(5)
            
            # Wait for results with multiple selectors
            result_container_found = False
            result_selectors = [
                "[data-component-type='s-search-result']",
                ".s-result-item",
                "[data-asin]"
            ]
            
            for selector in result_selectors:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    result_container_found = True
                    logger.info(f"Results container found with selector: {selector}")
                    break
                except:
                    continue
            
            if not result_container_found:
                logger.warning("No results container found, trying to extract anyway...")
            
            # Find products
            products = []
            for selector in result_selectors:
                try:
                    products = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if products:
                        logger.info(f"Found {len(products)} products with selector: {selector}")
                        break
                except:
                    continue
            
            if not products:
                logger.error("No products found with any selector")
                return []
            
            # Extract product data
            for i, product in enumerate(products[:8]):
                try:
                    item_data = {}
                    
                    # Extract title with multiple attempts
                    title_selectors = [
                        "h2 a span",
                        "h2 span",
                        ".a-size-medium span",
                        ".s-size-mini span",
                        "[data-cy='title-recipe-1'] span",
                        ".a-color-base"
                    ]
                    
                    title = None
                    for sel in title_selectors:
                        try:
                            title_elem = product.find_element(By.CSS_SELECTOR, sel)
                            title = title_elem.text.strip()
                            if title and len(title) > 10:  # Reasonable title length
                                break
                        except:
                            continue
                    
                    if not title:
                        logger.debug(f"Product {i}: No valid title found")
                        continue
                    
                    item_data["title"] = title
                    
                    # Extract price with multiple attempts
                    price_selectors = [
                        ".a-price .a-offscreen",
                        ".a-price-whole",
                        ".a-price-symbol + .a-price-whole",
                        ".a-price"
                    ]
                    
                    price = "Price not available"
                    for sel in price_selectors:
                        try:
                            price_elem = product.find_element(By.CSS_SELECTOR, sel)
                            price_text = price_elem.text.strip()
                            if price_text and any(char in price_text for char in ['$', '€', '£']):
                                price = price_text
                                break
                        except:
                            continue
                    
                    item_data["price"] = price
                    
                    # Extract rating
                    try:
                        rating_selectors = [
                            ".a-icon-alt",
                            "[aria-label*='stars']",
                            ".a-star-medium .a-icon-alt"
                        ]
                        
                        for sel in rating_selectors:
                            try:
                                rating_elem = product.find_element(By.CSS_SELECTOR, sel)
                                rating_text = rating_elem.get_attribute("textContent") or rating_elem.get_attribute("aria-label") or ""
                                if rating_text:
                                    rating_parts = rating_text.split()
                                    if rating_parts and rating_parts[0].replace('.', '').isdigit():
                                        item_data["rating"] = f"{rating_parts[0]} stars"
                                        break
                            except:
                                continue
                    except:
                        pass
                    
                    # Extract link
                    try:
                        link_selectors = ["h2 a", "a[href*='/dp/']", ".a-link-normal"]
                        for sel in link_selectors:
                            try:
                                link_elem = product.find_element(By.CSS_SELECTOR, sel)
                                href = link_elem.get_attribute("href")
                                if href and "/dp/" in href:
                                    item_data["link"] = href
                                    break
                            except:
                                continue
                    except:
                        pass
                    
                    # Apply price filter if specified
                    if parsed_intent.get("price_range") and item_data.get("price") != "Price not available":
                        try:
                            price_numbers = ''.join(c for c in item_data["price"] if c.isdigit() or c == '.')
                            if price_numbers:
                                price_num = float(price_numbers)
                                if price_num > parsed_intent["price_range"]:
                                    logger.debug(f"Product {i}: Price ${price_num} exceeds limit ${parsed_intent['price_range']}")
                                    continue
                        except:
                            pass
                    
                    if len(item_data) >= 2:  # At least title and one other field
                        results.append(item_data)
                        logger.info(f"Added product {len(results)}: {title[:50]}...")
                    else:
                        logger.debug(f"Product {i}: Insufficient data - {list(item_data.keys())}")
                        
                except Exception as e:
                    logger.debug(f"Error processing product {i}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(results)} Amazon products")
            
        except Exception as e:
            logger.error(f"Amazon search failed: {e}")
            
        return results

    async def _search_google(self, parsed_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Google - simplified for now"""
        results = []
        
        try:
            logger.info("Google search - returning sample data for testing")
            # Return some sample data to test the frontend
            results = [
                {
                    "title": "Sample Search Result 1",
                    "description": "This is a sample result to test the system",
                    "link": "https://example.com/1"
                },
                {
                    "title": "Sample Search Result 2", 
                    "description": "Another sample result for testing",
                    "link": "https://example.com/2"
                }
            ]
            
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            
        return results


class WebNavigatorAgent:
    def __init__(self):
        self.navigator = SeleniumWebNavigator()

    async def initialize(self):
        """Initialize the navigator"""
        try:
            await self.navigator.initialize(headless=True)
            logger.info("Web Navigator Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise

    async def cleanup(self):
        """Clean up resources"""
        await self.navigator.cleanup()

    async def execute_task(self, instruction: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a web navigation task"""
        return await self.navigator.execute_task(instruction, options)