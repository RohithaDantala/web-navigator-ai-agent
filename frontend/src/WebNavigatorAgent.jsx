import React, { useState, useEffect } from 'react';

const WebNavigatorApp = () => {
  const [instruction, setInstruction] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [executionTime, setExecutionTime] = useState(0);
  const [sessionId, setSessionId] = useState('');
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [contentType, setContentType] = useState('general');

  // Generate session ID on component mount
  useEffect(() => {
    const newSessionId = 'session_' + Math.random().toString(36).substr(2, 9);
    setSessionId(newSessionId);
  }, []);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!instruction.trim()) return;

    setIsLoading(true);
    setMessage('AI is analyzing your request...');
    setResults([]);

    try {
      const response = await fetch('http://localhost:8000/navigate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          instruction: instruction,
          session_id: sessionId,
          options: {
            headless: true,
            timeout: 30000
          }
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setResults(data.data || []);
        setMessage(data.message);
        setExecutionTime(data.execution_time);
        setContentType(data.content_type || 'general');
        
        // Add to history
        const historyItem = {
          instruction,
          results: data.data || [],
          timestamp: new Date().toLocaleString(),
          executionTime: data.execution_time,
          contentType: data.content_type || 'general'
        };
        setHistory(prev => [historyItem, ...prev.slice(0, 9)]); // Keep last 10
        
        // Clear input after successful submission
        setInstruction('');
      } else {
        setMessage(data.message || 'Navigation failed');
        setResults([]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessage('Error connecting to the server. Make sure the backend is running.');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const startNewChat = () => {
    setResults([]);
    setMessage('');
    setExecutionTime(0);
    setInstruction('');
    setContentType('general');
    const newSessionId = 'session_' + Math.random().toString(36).substr(2, 9);
    setSessionId(newSessionId);
  };

  const loadExample = (exampleInstruction) => {
    setInstruction(exampleInstruction);
  };

  const loadFromHistory = (historyItem) => {
    setInstruction(historyItem.instruction);
    setResults(historyItem.results);
    setMessage(`Loaded from history: ${historyItem.results.length} results`);
    setExecutionTime(historyItem.executionTime);
    setContentType(historyItem.contentType);
  };

  // Get appropriate action text based on content type and result
  const getActionText = (item) => {
    // Check if item has custom action text
    if (item.action_text) {
      return item.action_text;
    }
    
    // Fallback based on content type
    switch (contentType) {
      case 'products':
        return 'View Product';
      case 'jobs':
        return 'View Job';
      case 'repositories':
        return 'View Repository';
      case 'videos':
        return 'Watch Video';
      case 'questions':
        return 'View Question';
      default:
        return 'View Details';
    }
  };

  // Get content type icon
  const getContentTypeIcon = (type) => {
    switch (type) {
      case 'products': return '🛍️';
      case 'jobs': return '💼';
      case 'repositories': return '📁';
      case 'videos': return '📺';
      case 'questions': return '❓';
      default: return '📄';
    }
  };

  const exampleQueries = [
    "Search for gaming laptops under $1500 on Amazon",
    "Find Python jobs on LinkedIn", 
    "Search for React tutorials on YouTube",
    "Look for JavaScript questions on Stack Overflow",
    "Find React repositories on GitHub"
  ];

  return (
    <div style={styles.app}>
      <div style={styles.sidebar}>
        <div style={styles.sidebarHeader}>
          <div style={styles.logo}>
            <div style={styles.logoIcon}>⚡</div>
            <span style={styles.logoText}>AI Navigator</span>
          </div>
          <button onClick={startNewChat} style={styles.newChatButton}>
            + New Chat
          </button>
        </div>

        <div style={styles.navSection}>
          <div style={styles.navItem}>
            <span style={styles.navIcon}>💬</span>
            <span>Current Session</span>
          </div>
          <div 
            style={styles.navItem} 
            onClick={() => setShowHistory(!showHistory)}
          >
            <span style={styles.navIcon}>📚</span>
            <span>History ({history.length})</span>
          </div>
        </div>

        {showHistory && (
          <div style={styles.historySection}>
            <div style={styles.historyTitle}>Recent Searches</div>
            {history.length > 0 ? (
              <div style={styles.historyList}>
                {history.map((item, index) => (
                  <div 
                    key={index} 
                    style={styles.historyItem}
                    onClick={() => loadFromHistory(item)}
                  >
                    <div style={styles.historyText}>
                      {getContentTypeIcon(item.contentType)} {item.instruction.slice(0, 40)}...
                    </div>
                    <div style={styles.historyMeta}>
                      {item.results.length} results • {item.executionTime.toFixed(1)}s
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={styles.emptyHistory}>No searches yet</div>
            )}
          </div>
        )}

        <div style={styles.sidebarFooter}>
          <div style={styles.sessionInfo}>
            <div style={styles.sessionLabel}>Session ID</div>
            <div style={styles.sessionValue}>{sessionId.slice(-8)}</div>
          </div>
        </div>
      </div>

      <div style={styles.main}>
        <div style={styles.header}>
          <h1 style={styles.title}>AI Web Navigator</h1>
          <p style={styles.subtitle}>Intelligent web automation powered by Llama3 LLM and Selenium</p>
        </div>

        <div style={styles.content}>
          {!results.length && !message && (
            <div style={styles.welcome}>
              <div style={styles.welcomeContent}>
                <h2 style={styles.welcomeTitle}>Welcome to AI Web Navigator</h2>
                <p style={styles.welcomeDescription}>
                  Describe what you want to find on the web in natural language. 
                  Our AI will understand your request and navigate websites to gather the information you need.
                </p>
                
                <div style={styles.features}>
                  <div style={styles.feature}>
                    <div style={styles.featureIcon}>🧠</div>
                    <div style={styles.featureText}>
                      <div style={styles.featureTitle}>Smart Understanding</div>
                      <div style={styles.featureDesc}>AI interprets natural language queries</div>
                    </div>
                  </div>
                  <div style={styles.feature}>
                    <div style={styles.featureIcon}>🤖</div>
                    <div style={styles.featureText}>
                      <div style={styles.featureTitle}>Automated Navigation</div>
                      <div style={styles.featureDesc}>Selenium-powered web automation</div>
                    </div>
                  </div>
                  <div style={styles.feature}>
                    <div style={styles.featureIcon}>📊</div>
                    <div style={styles.featureText}>
                      <div style={styles.featureTitle}>Structured Results</div>
                      <div style={styles.featureDesc}>Clean, organized data extraction</div>
                    </div>
                  </div>
                  <div style={styles.feature}>
                    <div style={styles.featureIcon}>⚡</div>
                    <div style={styles.featureText}>
                      <div style={styles.featureTitle}>Fast Processing</div>
                      <div style={styles.featureDesc}>Optimized LLM-driven execution</div>
                    </div>
                  </div>
                </div>

                <div style={styles.examples}>
                  <div style={styles.examplesTitle}>Try these examples:</div>
                  <div style={styles.examplesList}>
                    {exampleQueries.map((query, index) => (
                      <button
                        key={index}
                        onClick={() => loadExample(query)}
                        style={styles.exampleButton}
                        disabled={isLoading}
                      >
                        {query}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {message && (
            <div style={styles.messageContainer}>
              <div style={styles.statusMessage}>
                <div style={styles.statusIcon}>
                  {isLoading ? (
                    <div style={styles.spinner}></div>
                  ) : '✅'}
                </div>
                <div style={styles.statusContent}>
                  <div style={styles.statusText}>{message}</div>
                  {executionTime > 0 && (
                    <div style={styles.statusTime}>
                      Completed in {executionTime.toFixed(2)} seconds
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {results.length > 0 && (
            <div style={styles.resultsContainer}>
              <div style={styles.resultsHeader}>
                <div style={styles.resultsTitle}>
                  {getContentTypeIcon(contentType)} {results.length} {contentType.charAt(0).toUpperCase() + contentType.slice(1)} Found
                </div>
                <button onClick={startNewChat} style={styles.clearButton}>
                  Clear Results
                </button>
              </div>

              <div style={styles.resultsGrid}>
                {results.map((item, index) => (
                  <div key={index} style={styles.resultCard}>
                    <div style={styles.resultBadge}>{index + 1}</div>
                    
                    {item.title && (
                      <h3 style={styles.resultTitle}>{item.title}</h3>
                    )}
                    
                    <div style={styles.resultDetails}>
                      {item.price && (
                        <div style={styles.resultPrice}>
                          <span style={styles.priceLabel}>Price:</span>
                          <span style={styles.priceValue}>{item.price}</span>
                        </div>
                      )}
                      {item.rating && (
                        <div style={styles.resultRating}>
                          <span style={styles.ratingLabel}>Rating:</span>
                          <span style={styles.ratingValue}>{item.rating}</span>
                        </div>
                      )}
                      {item.company && (
                        <div style={styles.resultCompany}>
                          <span style={styles.companyLabel}>Company:</span>
                          <span style={styles.companyValue}>{item.company}</span>
                        </div>
                      )}
                      {item.location && (
                        <div style={styles.resultLocation}>
                          <span style={styles.locationLabel}>Location:</span>
                          <span style={styles.locationValue}>{item.location}</span>
                        </div>
                      )}
                      {item.channel && (
                        <div style={styles.resultChannel}>
                          <span style={styles.channelLabel}>Channel:</span>
                          <span style={styles.channelValue}>{item.channel}</span>
                        </div>
                      )}
                      {item.views && (
                        <div style={styles.resultViews}>
                          <span style={styles.viewsLabel}>Views:</span>
                          <span style={styles.viewsValue}>{item.views}</span>
                        </div>
                      )}
                      {item.language && (
                        <div style={styles.resultLanguage}>
                          <span style={styles.languageLabel}>Language:</span>
                          <span style={styles.languageValue}>{item.language}</span>
                        </div>
                      )}
                      {item.stars && (
                        <div style={styles.resultStars}>
                          <span style={styles.starsLabel}>Stars:</span>
                          <span style={styles.starsValue}>{item.stars}</span>
                        </div>
                      )}
                    </div>
                    
                    {item.description && (
                      <p style={styles.resultDescription}>{item.description}</p>
                    )}
                    
                    {item.link && (
                      <a 
                        href={item.link} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={styles.resultLink}
                      >
                        {getActionText(item)} →
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div style={styles.inputArea}>
          <div style={styles.inputContainer}>
            <textarea
              value={instruction}
              onChange={(e) => setInstruction(e.target.value)}
              placeholder="Describe what you want to find on the web..."
              style={styles.input}
              disabled={isLoading}
              rows={1}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <button 
              onClick={handleSubmit}
              style={{
                ...styles.sendButton,
                ...(isLoading || !instruction.trim() ? styles.sendButtonDisabled : {})
              }}
              disabled={isLoading || !instruction.trim()}
            >
              {isLoading ? (
                <div style={styles.buttonSpinner}></div>
              ) : (
                '↑'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const styles = {
  app: {
    display: 'flex',
    height: '100vh',
    width: '100vw',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    backgroundColor: '#f8fafc',
    color: '#1e293b',
    overflow: 'hidden',
  },

  sidebar: {
    width: '320px',
    backgroundColor: '#ffffff',
    borderRight: '1px solid #e2e8f0',
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
  },

  sidebarHeader: {
    padding: '24px',
    borderBottom: '1px solid #e2e8f0',
  },

  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '16px',
  },

  logoIcon: {
    fontSize: '24px',
    color: '#3b82f6',
  },

  logoText: {
    fontSize: '20px',
    fontWeight: '700',
    color: '#1e293b',
  },

  newChatButton: {
    width: '100%',
    padding: '12px 16px',
    backgroundColor: '#3b82f6',
    color: '#ffffff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },

  navSection: {
    padding: '16px 0',
    borderBottom: '1px solid #e2e8f0',
  },

  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 24px',
    cursor: 'pointer',
    fontSize: '14px',
    color: '#64748b',
    transition: 'all 0.2s ease',
  },

  navIcon: {
    fontSize: '16px',
  },

  historySection: {
    flex: 1,
    padding: '16px 24px',
    overflowY: 'auto',
  },

  historyTitle: {
    fontSize: '12px',
    fontWeight: '600',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    marginBottom: '12px',
  },

  historyList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },

  historyItem: {
    padding: '12px',
    backgroundColor: '#f8fafc',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },

  historyText: {
    fontSize: '13px',
    color: '#334155',
    lineHeight: '1.4',
    marginBottom: '4px',
  },

  historyMeta: {
    fontSize: '11px',
    color: '#94a3b8',
  },

  emptyHistory: {
    fontSize: '13px',
    color: '#94a3b8',
    textAlign: 'center',
    padding: '20px',
  },

  sidebarFooter: {
    padding: '24px',
    borderTop: '1px solid #e2e8f0',
    backgroundColor: '#f8fafc',
  },

  sessionInfo: {
    textAlign: 'center',
  },

  sessionLabel: {
    fontSize: '11px',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    marginBottom: '4px',
  },

  sessionValue: {
    fontSize: '12px',
    color: '#64748b',
    fontFamily: 'monospace',
  },

  main: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    overflow: 'hidden',
  },

  header: {
    padding: '32px 48px 24px',
    backgroundColor: '#ffffff',
    borderBottom: '1px solid #e2e8f0',
  },

  title: {
    fontSize: '32px',
    fontWeight: '800',
    color: '#0f172a',
    margin: '0 0 8px 0',
  },

  subtitle: {
    fontSize: '16px',
    color: '#64748b',
    margin: 0,
    fontWeight: '400',
  },

  content: {
    flex: 1,
    overflow: 'auto',
    padding: '0 48px',
  },

  welcome: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    minHeight: '500px',
  },

  welcomeContent: {
    maxWidth: '800px',
    textAlign: 'center',
  },

  welcomeTitle: {
    fontSize: '28px',
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: '16px',
  },

  welcomeDescription: {
    fontSize: '16px',
    color: '#64748b',
    lineHeight: '1.6',
    marginBottom: '48px',
  },

  features: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '24px',
    marginBottom: '48px',
  },

  feature: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '20px',
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    border: '1px solid #e2e8f0',
    textAlign: 'left',
  },

  featureIcon: {
    fontSize: '32px',
    flexShrink: 0,
  },

  featureText: {
    flex: 1,
  },

  featureTitle: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#0f172a',
    marginBottom: '4px',
  },

  featureDesc: {
    fontSize: '14px',
    color: '#64748b',
    lineHeight: '1.4',
  },

  examples: {
    textAlign: 'left',
  },

  examplesTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#0f172a',
    marginBottom: '16px',
  },

  examplesList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },

  exampleButton: {
    padding: '12px 16px',
    backgroundColor: '#ffffff',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    fontSize: '14px',
    color: '#334155',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    textAlign: 'left',
  },

  messageContainer: {
    padding: '24px 0',
  },

  statusMessage: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '16px 20px',
    backgroundColor: '#eff6ff',
    border: '1px solid #bfdbfe',
    borderRadius: '12px',
  },

  statusIcon: {
    fontSize: '20px',
    color: '#3b82f6',
  },

  statusContent: {
    flex: 1,
  },

  statusText: {
    fontSize: '15px',
    color: '#1e40af',
    fontWeight: '500',
  },

  statusTime: {
    fontSize: '13px',
    color: '#3b82f6',
    marginTop: '4px',
  },

  spinner: {
    width: '18px',
    height: '18px',
    border: '2px solid #bfdbfe',
    borderTop: '2px solid #3b82f6',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },

  resultsContainer: {
    padding: '24px 0',
  },

  resultsHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },

  resultsTitle: {
    fontSize: '20px',
    fontWeight: '700',
    color: '#0f172a',
  },

  clearButton: {
    padding: '8px 16px',
    backgroundColor: '#ffffff',
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    fontSize: '14px',
    color: '#64748b',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },

  resultsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
    gap: '20px',
  },

  resultCard: {
    padding: '24px',
    backgroundColor: '#ffffff',
    border: '1px solid #e2e8f0',
    borderRadius: '12px',
    position: 'relative',
    transition: 'all 0.3s ease',
  },

  resultBadge: {
    position: 'absolute',
    top: '16px',
    right: '16px',
    width: '28px',
    height: '28px',
    backgroundColor: '#f1f5f9',
    color: '#64748b',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '12px',
    fontWeight: '600',
  },

  resultTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#0f172a',
    marginBottom: '16px',
    lineHeight: '1.4',
    paddingRight: '40px',
  },

  resultDetails: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '16px',
    marginBottom: '16px',
  },

  resultPrice: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },

  priceLabel: {
    fontSize: '12px',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },

  priceValue: {
    fontSize: '16px',
    fontWeight: '700',
    color: '#059669',
  },

  resultRating: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },

  ratingLabel: {
    fontSize: '12px',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },

  ratingValue: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#f59e0b',
  },

  resultCompany: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },

  companyLabel: {
    fontSize: '12px',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },

  companyValue: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#1e40af',
  },

  resultLocation: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },

  locationLabel: {
    fontSize: '12px',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },

  locationValue: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#7c3aed',
  },

  resultChannel: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },

  channelLabel: {
    fontSize: '12px',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },

  channelValue: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#dc2626',
  },

  resultViews: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },

  viewsLabel: {
    fontSize: '12px',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },

  viewsValue: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#059669',
  },

  resultLanguage: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },

  languageLabel: {
    fontSize: '12px',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },

  languageValue: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#ea580c',
  },

  resultStars: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },

  starsLabel: {
    fontSize: '12px',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },

  starsValue: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#f59e0b',
  },

  resultDescription: {
    fontSize: '14px',
    color: '#64748b',
    lineHeight: '1.5',
    marginBottom: '16px',
  },

  resultLink: {
    display: 'inline-flex',
    alignItems: 'center',
    fontSize: '14px',
    color: '#3b82f6',
    textDecoration: 'none',
    fontWeight: '600',
    transition: 'color 0.2s ease',
  },

  inputArea: {
    padding: '24px 48px',
    backgroundColor: '#ffffff',
    borderTop: '1px solid #e2e8f0',
  },

  inputContainer: {
    display: 'flex',
    gap: '12px',
    alignItems: 'flex-end',
    maxWidth: '1000px',
    margin: '0 auto',
  },

  input: {
    flex: 1,
    padding: '16px 20px',
    border: '1px solid #d1d5db',
    borderRadius: '12px',
    fontSize: '16px',
    fontFamily: 'inherit',
    resize: 'none',
    minHeight: '56px',
    maxHeight: '120px',
    outline: 'none',
    transition: 'all 0.2s ease',
    backgroundColor: '#ffffff',
    color: '#0f172a',
  },

  sendButton: {
    width: '56px',
    height: '56px',
    backgroundColor: '#0f172a',
    border: 'none',
    borderRadius: '12px',
    color: '#ffffff',
    fontSize: '20px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },

  sendButtonDisabled: {
    backgroundColor: '#94a3b8',
    cursor: 'not-allowed',
  },

  buttonSpinner: {
    width: '16px',
    height: '16px',
    border: '2px solid rgba(255, 255, 255, 0.3)',
    borderTop: '2px solid #ffffff',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
};

// Add CSS animations and hover effects
const styleSheet = document.createElement("style");
styleSheet.type = "text/css";
styleSheet.innerText = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .new-chat-button:hover {
    background-color: #2563eb !important;
    transform: translateY(-1px);
  }

  .nav-item:hover {
    background-color: #f1f5f9 !important;
    color: #1e293b !important;
  }

  .history-item:hover {
    background-color: #f1f5f9 !important;
  }

  .example-button:hover:not(:disabled) {
    background-color: #f8fafc !important;
    border-color: #cbd5e0 !important;
  }

  .result-card:hover {
    border-color: #cbd5e0 !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06) !important;
    transform: translateY(-2px);
  }

  .clear-button:hover {
    background-color: #f8fafc !important;
    border-color: #cbd5e0 !important;
  }

  .send-button:hover:not(:disabled) {
    background-color: #020617 !important;
    transform: scale(1.05);
  }

  .result-link:hover {
    color: #2563eb !important;
  }

  .input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
  }
`;
document.head.appendChild(styleSheet);

export default WebNavigatorApp;