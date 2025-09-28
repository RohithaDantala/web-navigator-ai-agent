# enhanced_web_navigator.py
import asyncio
import time
import json
import logging
import sys
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
from selenium.webdriver.common.action_chains import ActionChains
import re
from urllib.parse import urljoin, urlparse

# Import LLM services
from services.llm_service import LLMService

# Configure clean logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Suppress low-level browser logs
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class UniversalWebNavigator:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.llm_service = LLMService()

    async def initialize(self, headless=True, verbose_chrome=False):
        """Initialize Chrome with optimized settings"""
        logger.info("Starting browser initialization...")
        
        try:
            chrome_options = Options()
            
            # Performance and compatibility options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--remote-allow-origins=*")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Anti-detection
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent to avoid blocks
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.208 Safari/537.36")
            
            # Handle headless mode
            if headless:
                chrome_options.add_argument("--headless=new")
            
            # Suppress Chrome logs unless verbose mode
            if not verbose_chrome:
                chrome_options.add_argument("--log-level=3")
                chrome_options.add_argument("--silent")
                chrome_options.add_argument("--disable-logging")
                chrome_options.add_argument("--disable-gpu-logging")
                chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Suppress specific warnings
                chrome_options.add_argument("--disable-software-rasterizer")
                chrome_options.add_argument("--disable-background-media-suspend")
                chrome_options.add_argument("--disable-client-side-phishing-detection")
                chrome_options.add_argument("--disable-sync")
                chrome_options.add_argument("--metrics-recording-only")
                chrome_options.add_argument("--no-report-upload")
            
            # Create service with suppressed output
            service = Service(
                ChromeDriverManager().install(),
                log_path='NUL' if sys.platform.startswith('win') else '/dev/null'
            )
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            # Hide automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Browser initialization failed: {e}")
            return False

    async def cleanup(self):
        """Clean up browser resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser cleaned up successfully")
            except:
                pass
        
        # Close LLM service
        await self.llm_service.close()

    async def execute_task(self, instruction: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute universal web navigation task with LLM integration"""
        start_time = time.time()
        logger.info(f"Starting LLM-powered task: {instruction}")
        
        try:
            if not self.driver:
                raise Exception("Browser not initialized")
            
            # Step 1: Use LLM to parse instruction and determine intent
            parsed = await self._parse_instruction_with_llm(instruction)
            logger.info(f"LLM parsed - Site: {parsed['site']} | Content Type: {parsed['content_type']} | Query: {parsed['query']}")
            
            # Step 2: Execute based on detected site and content type
            if 'amazon' in parsed['site'].lower():
                results = await self._search_amazon(parsed)
            elif 'github' in parsed['site'].lower():
                results = await self._search_github(parsed)
            elif 'linkedin' in parsed['site'].lower():
                results = await self._search_linkedin(parsed)
            elif 'indeed' in parsed['site'].lower():
                results = await self._search_indeed(parsed)
            elif 'stackoverflow' in parsed['site'].lower():
                results = await self._search_stackoverflow(parsed)
            elif 'youtube' in parsed['site'].lower():
                results = await self._search_youtube(parsed)
            else:
                # Universal fallback for any website
                results = await self._search_universal(parsed)
            
            # Step 3: Use LLM to enhance and categorize results
            enhanced_results = await self._enhance_results_with_llm(results, parsed)
            
            execution_time = time.time() - start_time
            logger.info(f"Task completed: Found {len(enhanced_results)} results in {execution_time:.2f}s")
            
            return {
                "data": enhanced_results,
                "message": f"Found {len(enhanced_results)} results for '{instruction}'",
                "execution_time": execution_time,
                "success": True,
                "content_type": parsed['content_type'],
                "site": parsed['site']
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Task failed after {execution_time:.2f}s: {e}")
            return {
                "data": [],
                "message": f"Search failed: {str(e)}",
                "execution_time": execution_time,
                "success": False,
                "content_type": "unknown",
                "site": "unknown"
            }

    async def _parse_instruction_with_llm(self, instruction: str) -> Dict[str, Any]:
        """Use LLM to parse instruction and determine intent"""
        system_prompt = """
        You are an expert at analyzing web search instructions. Parse the user's request and return a JSON response with:
        
        {
            "site": "target website (amazon.com, github.com, linkedin.com, indeed.com, youtube.com, etc.)",
            "query": "cleaned search query",
            "content_type": "products|jobs|repositories|videos|questions|articles|general",
            "intent": "what the user wants to find"
        }
        
        Examples:
        - "Find gaming laptops on Amazon" → {"site": "amazon.com", "query": "gaming laptops", "content_type": "products", "intent": "shopping"}
        - "Python jobs on LinkedIn" → {"site": "linkedin.com", "query": "Python jobs", "content_type": "jobs", "intent": "job_search"}
        - "React tutorials on YouTube" → {"site": "youtube.com", "query": "React tutorials", "content_type": "videos", "intent": "learning"}
        - "JavaScript questions on Stack Overflow" → {"site": "stackoverflow.com", "query": "JavaScript", "content_type": "questions", "intent": "problem_solving"}
        """
        
        try:
            response = await self.llm_service.generate_response(system_prompt, f"Parse this instruction: {instruction}")
            
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                parsed = json.loads(json_str)
                return parsed
        except Exception as e:
            logger.warning(f"LLM parsing failed: {e}, using fallback")
        
        # Fallback parsing
        return self._parse_universal_instruction(instruction)

    async def _enhance_results_with_llm(self, results: List[Dict], parsed: Dict) -> List[Dict]:
        """Use LLM to enhance and categorize results"""
        if not results:
            return results
        
        try:
            # Add content type and action text to each result
            content_type = parsed.get('content_type', 'general')
            
            for result in results:
                result['content_type'] = content_type
                
                # Set appropriate action text based on content type
                if content_type == 'products':
                    result['action_text'] = 'View Product'
                elif content_type == 'jobs':
                    result['action_text'] = 'View Job'
                elif content_type == 'repositories':
                    result['action_text'] = 'View Repository'
                elif content_type == 'videos':
                    result['action_text'] = 'Watch Video'
                elif content_type == 'questions':
                    result['action_text'] = 'View Question'
                else:
                    result['action_text'] = 'View Details'
            
            return results
            
        except Exception as e:
            logger.warning(f"Result enhancement failed: {e}")
            return results

    def _parse_universal_instruction(self, instruction: str) -> Dict[str, Any]:
        """Fallback parsing when LLM fails"""
        instruction_lower = instruction.lower()
        
        # Site detection patterns
        site_patterns = {
            'amazon': ['amazon.com', 'amazon', 'buy', 'shop', 'product'],
            'github': ['github.com', 'github', 'repository', 'repo', 'code'],
            'linkedin': ['linkedin.com', 'linkedin', 'job', 'career', 'professional'],
            'indeed': ['indeed.com', 'indeed', 'job search', 'careers', 'employment'],
            'stackoverflow': ['stackoverflow.com', 'stackoverflow', 'stack overflow', 'programming questions'],
            'youtube': ['youtube.com', 'youtube', 'video', 'tutorial', 'watch'],
            'google': ['google.com', 'google', 'search'],
        }
        
        # Content type detection
        content_patterns = {
            'products': ['product', 'buy', 'shop', 'purchase', 'price', 'laptop', 'phone', 'headphones'],
            'jobs': ['job', 'career', 'employment', 'hiring', 'position', 'salary'],
            'repositories': ['repository', 'repo', 'code', 'library', 'framework'],
            'videos': ['video', 'tutorial', 'watch', 'learn', 'how to'],
            'questions': ['question', 'problem', 'help', 'error', 'bug'],
        }
        
        detected_site = 'google.com'  # default
        for site, patterns in site_patterns.items():
            if any(pattern in instruction_lower for pattern in patterns):
                detected_site = f"{site}.com" if not site.endswith('.com') else site
                break
        
        detected_content_type = 'general'
        for content_type, patterns in content_patterns.items():
            if any(pattern in instruction_lower for pattern in patterns):
                detected_content_type = content_type
                break
        
        # Extract search query
        query = instruction
        # Remove site references
        for patterns in site_patterns.values():
            for pattern in patterns:
                query = re.sub(rf'\b{re.escape(pattern)}\b', '', query, flags=re.IGNORECASE)
        
        # Clean up query
        query = re.sub(r'\b(search for|find|look for|on|in)\b', '', query, flags=re.IGNORECASE)
        query = query.strip()
        
        return {
            'site': detected_site,
            'query': query,
            'content_type': detected_content_type,
            'intent': 'search',
            'original': instruction
        }

    async def _search_youtube(self, parsed: Dict) -> List[Dict[str, Any]]:
        """YouTube video search"""
        logger.info("Navigating to YouTube...")
        results = []
        
        try:
            self.driver.get("https://www.youtube.com")
            await asyncio.sleep(3)
            
            # Handle cookie consent and popups
            await self._dismiss_popups([
                "button[aria-label='Accept all']",
                "button[aria-label='Accept the use of cookies and other data for the purposes described']",
                "#yDmH0d c-wiz div[role='button']",
                ".eom-buttons .VfPpkd-LgbsSe"
            ])
            
            # Find search box
            search_box = await self._find_element_universal([
                "input#search",
                "input[name='search_query']",
                "#search-input #search",
                "input[placeholder*='Search']"
            ])
            
            if not search_box:
                raise Exception("YouTube search box not found")
            
            logger.info(f"Searching YouTube for: {parsed['query']}")
            search_box.clear()
            search_box.send_keys(parsed['query'])
            search_box.send_keys(Keys.RETURN)
            
            await asyncio.sleep(4)
            
            # Extract videos
            videos = self.driver.find_elements(By.CSS_SELECTOR, 
                "ytd-video-renderer, #contents ytd-rich-item-renderer")
            
            logger.info(f"Found {len(videos)} video containers")
            
            for i, video in enumerate(videos[:10]):
                try:
                    item = {}
                    
                    # Video title
                    title_elem = await self._find_element_in_container(video, [
                        "#video-title", "h3 a", "#video-title-link", "a#thumbnail + div h3 a"
                    ])
                    if title_elem:
                        item["title"] = title_elem.text.strip()
                        item["link"] = urljoin("https://youtube.com", title_elem.get_attribute("href"))
                    
                    # Channel name
                    channel_elem = await self._find_element_in_container(video, [
                        "#channel-info #text a", ".ytd-channel-name a", "#owner-text a"
                    ])
                    if channel_elem:
                        item["channel"] = channel_elem.text.strip()
                    
                    # View count
                    views_elem = await self._find_element_in_container(video, [
                        "#metadata-line span:first-child", ".view-count"
                    ])
                    if views_elem:
                        item["views"] = views_elem.text.strip()
                    
                    # Duration
                    duration_elem = await self._find_element_in_container(video, [
                        ".ytd-thumbnail-overlay-time-status-renderer", "#overlays .badge-style-type-simple"
                    ])
                    if duration_elem:
                        item["duration"] = duration_elem.text.strip()
                    
                    if len(item) >= 2:
                        results.append(item)
                        
                except Exception as e:
                    logger.debug(f"Error extracting video {i}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(results)} YouTube videos")
            
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            
        return results

    async def _search_amazon(self, parsed: Dict) -> List[Dict[str, Any]]:
        """Enhanced Amazon search"""
        logger.info("Navigating to Amazon...")
        results = []
        
        try:
            self.driver.get("https://www.amazon.com")
            await asyncio.sleep(3)
            
            # Handle popups
            await self._dismiss_popups([
                "[data-action-type='DISMISS']",
                "#sp-cc-accept",
                ".a-button-close"
            ])
            
            # Find search box with multiple strategies
            search_box = await self._find_element_universal([
                "#twotabsearchtextbox",
                "input[name='field-keywords']",
                "input[placeholder*='Search']",
                "input[type='search']"
            ])
            
            if not search_box:
                raise Exception("Amazon search box not found")
            
            logger.info(f"Searching Amazon for: {parsed['query']}")
            search_box.clear()
            search_box.send_keys(parsed['query'])
            search_box.send_keys(Keys.RETURN)
            
            await asyncio.sleep(4)
            
            # Extract products
            products = self.driver.find_elements(By.CSS_SELECTOR, 
                "[data-component-type='s-search-result'], .s-result-item, [data-asin]")
            
            logger.info(f"Found {len(products)} product containers")
            
            for i, product in enumerate(products[:10]):
                try:
                    item = {}
                    
                    # Title
                    title_elem = await self._find_element_in_container(product, [
                        "h2 a span", "h2 span", ".a-size-medium span", "[data-cy='title-recipe-1'] span"
                    ])
                    if title_elem:
                        item["title"] = title_elem.text.strip()
                    
                    # Price
                    price_elem = await self._find_element_in_container(product, [
                        ".a-price .a-offscreen", ".a-price-whole", ".a-price"
                    ])
                    if price_elem:
                        item["price"] = price_elem.text.strip()
                    
                    # Rating
                    rating_elem = await self._find_element_in_container(product, [
                        ".a-icon-alt", "[aria-label*='stars']"
                    ])
                    if rating_elem:
                        rating_text = rating_elem.get_attribute("aria-label") or rating_elem.text
                        if rating_text:
                            item["rating"] = rating_text.split()[0] + " stars"
                    
                    # Link
                    link_elem = await self._find_element_in_container(product, [
                        "h2 a", "a[href*='/dp/']"
                    ])
                    if link_elem:
                        href = link_elem.get_attribute("href")
                        if href:
                            item["link"] = href
                    
                    if len(item) >= 2:
                        results.append(item)
                        
                except Exception as e:
                    logger.debug(f"Error extracting product {i}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(results)} Amazon products")
            
        except Exception as e:
            logger.error(f"Amazon search failed: {e}")
            
        return results

    async def _search_github(self, parsed: Dict) -> List[Dict[str, Any]]:
        """GitHub repository search"""
        logger.info("Navigating to GitHub...")
        results = []
        
        try:
            self.driver.get("https://github.com")
            await asyncio.sleep(2)
            
            # Find search box
            search_box = await self._find_element_universal([
                "input[name='q']",
                ".header-search-input",
                "[placeholder*='Search GitHub']"
            ])
            
            if not search_box:
                # Try the search icon first
                search_btn = await self._find_element_universal([
                    ".header-search-button",
                    "[aria-label='Search GitHub']"
                ])
                if search_btn:
                    search_btn.click()
                    await asyncio.sleep(1)
                    search_box = await self._find_element_universal([
                        "input[name='q']",
                        ".header-search-input"
                    ])
            
            if not search_box:
                raise Exception("GitHub search box not found")
            
            logger.info(f"Searching GitHub for: {parsed['query']}")
            search_box.clear()
            search_box.send_keys(parsed['query'])
            search_box.send_keys(Keys.RETURN)
            
            await asyncio.sleep(4)
            
            # Extract repositories
            repos = self.driver.find_elements(By.CSS_SELECTOR, 
                ".repo-list-item, [data-testid='results-list'] > div")
            
            logger.info(f"Found {len(repos)} repository containers")
            
            for i, repo in enumerate(repos[:10]):
                try:
                    item = {}
                    
                    # Repository name/title
                    title_elem = await self._find_element_in_container(repo, [
                        "h3 a", ".f4 a", "[data-testid='listitem-title'] a"
                    ])
                    if title_elem:
                        item["title"] = title_elem.text.strip()
                        item["link"] = urljoin("https://github.com", title_elem.get_attribute("href"))
                    
                    # Description
                    desc_elem = await self._find_element_in_container(repo, [
                        ".repo-list-description p", ".color-fg-muted", "[data-testid='listitem-description']"
                    ])
                    if desc_elem:
                        item["description"] = desc_elem.text.strip()
                    
                    # Language
                    lang_elem = await self._find_element_in_container(repo, [
                        "[itemprop='programmingLanguage']", ".color-fg-muted .text-bold"
                    ])
                    if lang_elem:
                        item["language"] = lang_elem.text.strip()
                    
                    # Stars
                    stars_elem = await self._find_element_in_container(repo, [
                        "[href$='/stargazers']", ".octicon-star + *"
                    ])
                    if stars_elem:
                        item["stars"] = stars_elem.text.strip()
                    
                    if len(item) >= 2:
                        results.append(item)
                        
                except Exception as e:
                    logger.debug(f"Error extracting repo {i}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(results)} GitHub repositories")
            
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
            
        return results

    async def _search_linkedin(self, parsed: Dict) -> List[Dict[str, Any]]:
        """LinkedIn job search (limited without login)"""
        logger.info("Navigating to LinkedIn...")
        results = []
        
        try:
            # Use LinkedIn job search without login
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={parsed['query'].replace(' ', '%20')}"
            self.driver.get(search_url)
            await asyncio.sleep(4)
            
            # Handle potential popups
            await self._dismiss_popups([
                "[data-tracking-control-name='public_jobs_contextual-sign-up-modal_modal_dismiss']",
                ".modal__dismiss"
            ])
            
            # Extract job listings
            jobs = self.driver.find_elements(By.CSS_SELECTOR, 
                ".jobs-search__results-list li, .job-search-card")
            
            logger.info(f"Found {len(jobs)} job containers")
            
            for i, job in enumerate(jobs[:8]):
                try:
                    item = {}
                    
                    # Job title
                    title_elem = await self._find_element_in_container(job, [
                        ".base-search-card__title", "h3 a", ".job-search-card__title"
                    ])
                    if title_elem:
                        item["title"] = title_elem.text.strip()
                    
                    # Company
                    company_elem = await self._find_element_in_container(job, [
                        ".base-search-card__subtitle", ".job-search-card__subtitle-primary-grouping"
                    ])
                    if company_elem:
                        item["company"] = company_elem.text.strip()
                    
                    # Location
                    location_elem = await self._find_element_in_container(job, [
                        ".job-search-card__location", "[data-test='job-search-card-location']"
                    ])
                    if location_elem:
                        item["location"] = location_elem.text.strip()
                    
                    # Link
                    link_elem = await self._find_element_in_container(job, [
                        "a", ".base-card__full-link"
                    ])
                    if link_elem:
                        href = link_elem.get_attribute("href")
                        if href:
                            item["link"] = href
                    
                    if len(item) >= 2:
                        results.append(item)
                        
                except Exception as e:
                    logger.debug(f"Error extracting job {i}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(results)} LinkedIn jobs")
            
        except Exception as e:
            logger.error(f"LinkedIn search failed: {e}")
            
        return results

    async def _search_indeed(self, parsed: Dict) -> List[Dict[str, Any]]:
        """Indeed job search"""
        logger.info("Navigating to Indeed...")
        results = []
        
        try:
            self.driver.get("https://indeed.com")
            await asyncio.sleep(3)
            
            # Find job search input
            job_input = await self._find_element_universal([
                "#text-input-what",
                "input[name='q']",
                "input[aria-label*='job']"
            ])
            
            if not job_input:
                raise Exception("Indeed search box not found")
            
            logger.info(f"Searching Indeed for: {parsed['query']}")
            job_input.clear()
            job_input.send_keys(parsed['query'])
            
            # Click search button
            search_btn = await self._find_element_universal([
                ".yosegi-InlineWhatWhere-primaryButton",
                "button[type='submit']",
                ".icl-Button--primary"
            ])
            
            if search_btn:
                search_btn.click()
            else:
                job_input.send_keys(Keys.RETURN)
            
            await asyncio.sleep(4)
            
            # Extract job listings
            jobs = self.driver.find_elements(By.CSS_SELECTOR, 
                ".job_seen_beacon, .result, [data-testid='job-title']")
            
            logger.info(f"Found {len(jobs)} job containers")
            
            for i, job in enumerate(jobs[:8]):
                try:
                    item = {}
                    
                    # Job title
                    title_elem = await self._find_element_in_container(job, [
                        "[data-testid='job-title'] a", "h2 a", ".jobTitle a"
                    ])
                    if title_elem:
                        item["title"] = title_elem.text.strip()
                        item["link"] = urljoin("https://indeed.com", title_elem.get_attribute("href"))
                    
                    # Company
                    company_elem = await self._find_element_in_container(job, [
                        ".companyName", "[data-testid='company-name']"
                    ])
                    if company_elem:
                        item["company"] = company_elem.text.strip()
                    
                    # Location
                    location_elem = await self._find_element_in_container(job, [
                        ".companyLocation", "[data-testid='job-location']"
                    ])
                    if location_elem:
                        item["location"] = location_elem.text.strip()
                    
                    # Salary (if available)
                    salary_elem = await self._find_element_in_container(job, [
                        ".metadata .salary-snippet", "[data-testid='job-salary']"
                    ])
                    if salary_elem:
                        item["salary"] = salary_elem.text.strip()
                    
                    if len(item) >= 2:
                        results.append(item)
                        
                except Exception as e:
                    logger.debug(f"Error extracting job {i}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(results)} Indeed jobs")
            
        except Exception as e:
            logger.error(f"Indeed search failed: {e}")
            
        return results

    async def _search_stackoverflow(self, parsed: Dict) -> List[Dict[str, Any]]:
        """Stack Overflow search"""
        logger.info("Navigating to Stack Overflow...")
        results = []
        
        try:
            self.driver.get("https://stackoverflow.com")
            await asyncio.sleep(2)
            
            # Find search box
            search_box = await self._find_element_universal([
                "input[name='q']",
                ".s-input__search",
                "[placeholder*='Search']"
            ])
            
            if not search_box:
                raise Exception("Stack Overflow search box not found")
            
            logger.info(f"Searching Stack Overflow for: {parsed['query']}")
            search_box.clear()
            search_box.send_keys(parsed['query'])
            search_box.send_keys(Keys.RETURN)
            
            await asyncio.sleep(3)
            
            # Extract questions
            questions = self.driver.find_elements(By.CSS_SELECTOR, 
                ".s-post-summary, .question-summary")
            
            logger.info(f"Found {len(questions)} question containers")
            
            for i, question in enumerate(questions[:10]):
                try:
                    item = {}
                    
                    # Question title
                    title_elem = await self._find_element_in_container(question, [
                        ".s-post-summary--content-title a", ".question-hyperlink"
                    ])
                    if title_elem:
                        item["title"] = title_elem.text.strip()
                        item["link"] = urljoin("https://stackoverflow.com", title_elem.get_attribute("href"))
                    
                    # Vote count
                    votes_elem = await self._find_element_in_container(question, [
                        ".s-post-summary--stats-item-number", ".votes .vote-count-post"
                    ])
                    if votes_elem:
                        item["votes"] = votes_elem.text.strip()
                    
                    # Answer count
                    answers_elem = await self._find_element_in_container(question, [
                        ".s-post-summary--stats-item:nth-child(2) .s-post-summary--stats-item-number"
                    ])
                    if answers_elem:
                        item["answers"] = answers_elem.text.strip()
                    
                    # Tags
                    tags = question.find_elements(By.CSS_SELECTOR, ".s-tag, .post-tag")
                    if tags:
                        item["tags"] = [tag.text for tag in tags[:3]]
                    
                    if len(item) >= 2:
                        results.append(item)
                        
                except Exception as e:
                    logger.debug(f"Error extracting question {i}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(results)} Stack Overflow questions")
            
        except Exception as e:
            logger.error(f"Stack Overflow search failed: {e}")
            
        return results

    async def _search_universal(self, parsed: Dict) -> List[Dict[str, Any]]:
        """Universal search fallback for any website"""
        logger.info(f"Universal search on {parsed['site']}")
        results = []
        
        try:
            # Construct URL
            if not parsed['site'].startswith('http'):
                url = f"https://{parsed['site']}"
            else:
                url = parsed['site']
            
            self.driver.get(url)
            await asyncio.sleep(3)
            
            # Try to find any search input
            search_box = await self._find_element_universal([
                "input[name='q']",
                "input[name='search']",
                "input[type='search']",
                "input[placeholder*='search' i]",
                "input[placeholder*='Search' i]",
                "input[aria-label*='search' i]",
                "#search",
                ".search input",
                "[role='search'] input"
            ])
            
            if search_box:
                logger.info(f"Found search box, searching for: {parsed['query']}")
                search_box.clear()
                search_box.send_keys(parsed['query'])
                search_box.send_keys(Keys.RETURN)
                await asyncio.sleep(4)
                
                # Extract any structured content
                content_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "article, .result, .item, .post, .product, .card, [role='article']")
                
                for i, element in enumerate(content_elements[:10]):
                    try:
                        item = {}
                        
                        # Try to extract title/heading
                        title_elem = await self._find_element_in_container(element, [
                            "h1", "h2", "h3", ".title", ".heading", "a"
                        ])
                        if title_elem:
                            title_text = title_elem.text.strip()
                            if len(title_text) > 5:  # Reasonable title length
                                item["title"] = title_text[:200]
                        
                        # Try to extract description
                        desc_elem = await self._find_element_in_container(element, [
                            "p", ".description", ".summary", ".excerpt"
                        ])
                        if desc_elem:
                            desc_text = desc_elem.text.strip()
                            if len(desc_text) > 10:
                                item["description"] = desc_text[:300]
                        
                        # Try to extract link
                        link_elem = await self._find_element_in_container(element, ["a"])
                        if link_elem:
                            href = link_elem.get_attribute("href")
                            if href and href.startswith('http'):
                                item["link"] = href
                        
                        if len(item) >= 1:
                            results.append(item)
                            
                    except Exception as e:
                        logger.debug(f"Error extracting content {i}: {e}")
                        continue
            
            else:
                # No search box found, just extract visible content
                logger.info("No search box found, extracting visible content")
                
                # Look for any structured content on the page
                content_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "article, .post, .item, .card, h2, h3")
                
                for i, element in enumerate(content_elements[:8]):
                    try:
                        text = element.text.strip()
                        if len(text) > 10 and len(text) < 500:
                            results.append({
                                "title": text[:100],
                                "content": text,
                                "source": parsed['site']
                            })
                    except:
                        continue
            
            logger.info(f"Universal search extracted {len(results)} items")
            
        except Exception as e:
            logger.error(f"Universal search failed: {e}")
            
        return results

    async def _find_element_universal(self, selectors: List[str], timeout=5):
        """Find element using multiple selectors with timeout"""
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                if element:
                    return element
            except:
                continue
        return None

    async def _find_element_in_container(self, container, selectors: List[str]):
        """Find element within a container using multiple selectors"""
        for selector in selectors:
            try:
                element = container.find_element(By.CSS_SELECTOR, selector)
                if element and element.is_displayed():
                    return element
            except:
                continue
        return None

    async def _dismiss_popups(self, selectors: List[str]):
        """Dismiss common popups/modals"""
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                element.click()
                logger.info(f"Dismissed popup: {selector}")
                await asyncio.sleep(1)
            except:
                continue


class WebNavigatorAgent:
    def __init__(self):
        self.navigator = UniversalWebNavigator()

    async def initialize(self, headless=True, verbose_chrome=False):
        """Initialize the navigator"""
        success = await self.navigator.initialize(headless, verbose_chrome)
        if success:
            logger.info("Web Navigator Agent ready with LLM integration")
        return success

    async def cleanup(self):
        """Clean up resources"""
        await self.navigator.cleanup()

    async def execute_task(self, instruction: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a web navigation task"""
        return await self.navigator.execute_task(instruction, options)