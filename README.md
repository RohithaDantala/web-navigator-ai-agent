# Web Navigator AI Agent

## 🎯 Problem Statement (HACXPB002)

Building an autonomous browser agent that can understand natural language instructions, plan execution steps, control web browsers autonomously, and extract structured results. The challenge involves creating a system that bridges human intent with automated web navigation through conversational AI.

**Example Task**: *"Search for laptops under 50k and list top 5 with specifications"* → Agent automatically performs Google search, extracts relevant data, filters by price, and returns structured results.

## 📋 Detailed Proposal & Prototype Plan

### Architecture Overview

Our Web Navigator AI Agent follows a modular pipeline architecture:

```
User Input → NL Understanding → Task Planning → Browser Automation → Data Extraction → Structured Output
```

### Core Components

#### 1. Natural Language Understanding Module
- **Technology**: Local LLM (LLaMA 3 via Ollama)
- **Function**: Parses natural language instructions into structured task plans
- **Input**: "Search for laptops under 50k and list top 5"
- **Output**: Step-by-step execution plan with browser actions

#### 2. Task Orchestration Engine
- **Technology**: Custom Python orchestrator with LangChain integration
- **Function**: Converts parsed intent into executable browser commands
- **Features**: 
  - Dynamic step sequencing
  - Error recovery mechanisms
  - State management across browser sessions

#### 3. Browser Automation Layer
- **Technology**: Selenium WebDriver
- **Function**: Executes actual browser interactions
- **Capabilities**:
  - Multi-browser support (Chrome, Firefox, Edge)
  - Headless and visible modes
  - Element detection and interaction
  - Screenshot capture for debugging

#### 4. Data Extraction & Structuring
- **Technology**: BeautifulSoup + Selenium selectors
- **Function**: Intelligent content scraping and data structuring
- **Output Formats**: JSON, CSV, structured dictionaries


## ✨ Features to be Implemented

### Core Features ✅
- [x] Natural language instruction parsing
- [x] Dynamic task plan generation
- [x] Multi-browser automation support
- [x] Intelligent element detection
- [x] Structured data extraction
- [x] JSON/CSV output formatting

### Advanced Features 🚧
- [ ] **Context Memory**: Remember previous searches and user preferences
- [ ] **Multi-page Navigation**: Handle complex workflows across multiple websites
- [ ] **Price Comparison**: Automated comparison across e-commerce platforms
- [ ] **Form Automation**: Auto-fill forms and handle user authentication
- [ ] **Screenshot Generation**: Visual confirmation of completed tasks
- [ ] **Voice Interface**: Speech-to-text input integration
- [ ] **Scheduling**: Periodic automated searches with notifications

### AI Enhancement Features 🔮
- [ ] **RAG Integration**: Retrieval-augmented generation for better context understanding
- [ ] **Learning Module**: Improve performance based on user feedback
- [ ] **Website Adaptation**: Dynamic adaptation to website layout changes
- [ ] **Query Optimization**: Suggest better search terms for improved results

## 🛠 Tech Stack

### Backend Framework
- **Python 3.8+**: Core application development
- **Selenium WebDriver**: Browser automation and control
- **BeautifulSoup4**: HTML parsing and data extraction
- **Pandas**: Data manipulation and analysis

### AI/ML Components
- **Ollama**: Local LLM deployment and management
- **LLaMA 3**: Language model for instruction understanding
- **LangChain**: LLM application framework and orchestration
- **Transformers**: Additional NLP capabilities

### Web Automation
- **ChromeDriver**: Chrome browser automation
- **GeckoDriver**: Firefox browser automation
- **Requests**: HTTP client for API interactions
- **Urllib**: URL handling and parsing

### Data Processing
- **JSON**: Structured data formatting
- **CSV**: Tabular data export
- **SQLite**: Local data storage (optional)
- **Regular Expressions**: Text pattern matching

### Development Tools
- **Poetry**: Dependency management
- **Pytest**: Unit testing framework
- **Black**: Code formatting
- **Flake8**: Code linting
- **Pre-commit**: Git hooks for code quality


## 🚀 Getting Started

### Prerequisites
```bash
# Python 3.8 or higher
python --version

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull LLaMA 3 model
ollama pull llama3
```

### Installation
```bash
# Clone repository
git clone https://github.com/your-username/web-navigator-ai-agent.git
cd web-navigator-ai-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install browser drivers
python -m selenium.webdriver.chrome.service
python -m selenium.webdriver.firefox.service
```

### Quick Start
```python
from src.core.agent import WebNavigatorAgent

# Initialize agent
agent = WebNavigatorAgent()

# Execute natural language command
result = agent.execute("Search for laptops under 50k and list top 5")

# Print structured results
print(result)
```

## 👥 Team Contributions

### Rasvini (231FA04F22) - LLM Integration & Intelligence Layer
**Focus:** AI/LLM Specialist - "Brain of the System"

**Files Owned:**
- `llm_service.py` - Core LLM communication service
- `intent_parser.py` - Natural language understanding
- `task_planner.py` - AI-powered task planning
- `settings.yaml` - Configuration management

**Responsibilities:**
- Set up and optimize Ollama/Llama3 integration
- Implement natural language instruction parsing
- Design intelligent task planning algorithms
- Fine-tune prompts for better accuracy
- Handle LLM error cases and fallbacks

**Key Contributions:**
- Ollama integration with LLaMA 3 model
- Custom prompt engineering for 95% instruction parsing accuracy
- Context management and conversation memory systems
- Intelligent task decomposition algorithms
- Error handling and fallback mechanisms for LLM responses

### Bhavana (231FA04203) - Browser Automation & Web Control
**Focus:** Web Automation Engineer - "Hands of the System"

**Files Owned:**
- `enhanced_web_navigator.py` - Main navigation engine
- `browser_controller.py` - Browser control logic
- `web_navigator_selenium.py` - Selenium implementation

**Responsibilities:**
- Implement robust browser automation with Selenium WebDriver
- Handle different website structures (Amazon, GitHub, LinkedIn, etc.)
- Develop anti-detection mechanisms
- Optimize browser performance and reliability
- Create fallback strategies for failed navigation

**Key Contributions:**
- Multi-browser automation framework (Chrome, Firefox, Edge)
- Anti-detection mechanisms to avoid bot blocking
- Cross-platform browser compatibility testing
- Intelligent element detection and interaction systems
- Performance optimization for web scraping operations

### Varshini (231FA04E93) - Data Extraction & Processing
**Focus:** Data Engineer - "Eyes of the System"

**Files Owned:**
- `data_extractor.py` - Data extraction and cleaning
- `helpers.py` - Utility functions for data processing
- `task_models.py` - Data structure definitions

**Responsibilities:**
- Build intelligent data extraction algorithms
- Implement data cleaning and validation
- Create structured output formatting
- Handle different data types (prices, ratings, descriptions)
- Develop data quality scoring systems

**Key Contributions:**
- BeautifulSoup integration for intelligent content extraction
- Data validation and cleaning pipelines
- Structured output formatting (JSON/CSV)
- Multi-format data type handling and processing
- Quality scoring algorithms for extracted data

### Rohitha (231FA04F09) - API & Backend Infrastructure
**Focus:** Backend/DevOps Engineer - "Backbone of the System"

**Files Owned:**
- `main.py` - FastAPI server implementation
- `request_models.py` - API request/response models
- `memory_service.py` - Data persistence layer
- `requirements.txt` - Dependency management

**Responsibilities:**
- Design and implement REST API endpoints
- Create request/response handling systems
- Implement session management and history
- Set up database for storing results
- Handle concurrent requests and scaling
- Deploy and monitor the backend service

**Key Contributions:**
- FastAPI server architecture and RESTful endpoints
- Session management and user history tracking
- Database integration for result persistence
- Concurrent request handling and load balancing
- Deployment pipeline and system monitoring

### Pavani (231FA04F18) - Frontend & User Experience
**Focus:** Frontend Developer - "Face of the System"

**Files Owned:**
- `WebNavigatorAgent.jsx` - Complete React frontend
- Frontend styling and component architecture
- User interaction flows and UX design

**Responsibilities:**
- Build intuitive React-based user interface
- Implement real-time status updates and loading states
- Create example queries and user guidance systems
- Design responsive and accessible UI components
- Handle error states and user feedback mechanisms
- Implement session history and result visualization

**Key Contributions:**
- React-based responsive user interface
- Real-time status updates and progress tracking
- Intuitive UX flow from query input to results display
- Error handling and user feedback systems
- Session history visualization and management

## 📊 Demo Examples

### Example 1: Product Search
```python
# Input
"Find the top 5 gaming laptops under ₹80,000 with their specifications"

# Output
[
  {
    "title": "ASUS ROG Strix G15",
    "price": "₹75,999",
    "specifications": "AMD Ryzen 7, 16GB RAM, RTX 3050",
    "link": "https://...",
    "rating": "4.3/5"
  },
  // ... 4 more results
]
```

### Example 2: Price Comparison
```python
# Input
"Compare iPhone 14 prices across Amazon, Flipkart, and official Apple store"

# Output
{
  "product": "iPhone 14",
  "comparison": [
    {"store": "Amazon", "price": "₹69,999", "availability": "In Stock"},
    {"store": "Flipkart", "price": "₹71,999", "availability": "In Stock"},
    {"store": "Apple Store", "price": "₹72,900", "availability": "In Stock"}
  ],
  "recommendation": "Best price found on Amazon"
}
```

## 📈 Performance Metrics

- **Instruction Understanding Accuracy**: 95%+
- **Browser Automation Success Rate**: 92%+
- **Data Extraction Quality Score**: 88%+
- **Average Response Time**: <30 seconds
- **Supported Website Types**: 8+ (E-commerce, Search, Social, etc.)

## 🔄 Integration Points

### Daily Development Focus:
- **Rasvini**: LLM accuracy and parsing improvements
- **Bhavan**: Browser compatibility and automation reliability  
- **Varshini**: Data extraction quality and new site support
- **Rohitha**: API performance and deployment status
- **Pavani**: User experience and frontend polish

### Key Integration Workflows:
1. **LLM ↔ Browser**: Intent parsing to navigation commands
2. **Browser ↔ Data**: Navigation results to structured extraction
3. **Data ↔ API**: Processed data to HTTP responses
4. **API ↔ Frontend**: Backend responses to UI updates

## 📝 Testing Strategy

### Unit Testing
- Individual module testing for each component
- Mock testing for external dependencies
- Coverage target: 85%+

### Integration Testing
- End-to-end workflow validation
- Cross-browser compatibility testing
- Performance benchmarking

### User Acceptance Testing
- Natural language instruction variety
- Edge case handling
- User experience validation

## 🚀 Deployment & Scaling

### Development Environment
- Local development with hot-reload
- Docker containerization for consistency
- Environment-specific configurations

### Production Deployment
- Cloud deployment (AWS/GCP/Azure)
- Load balancing for concurrent users
- Monitoring and logging systems
- Automated backup and recovery

## 📚 Documentation

- **API Reference**: Complete endpoint documentation
- **User Guide**: Step-by-step usage instructions
- **Developer Guide**: Architecture and contribution guidelines
- **Deployment Guide**: Setup and configuration instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper testing
4. Submit a pull request with detailed description
5. Ensure all tests pass and code follows style guidelines

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation for common solutions
