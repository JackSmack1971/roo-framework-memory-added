# MCP Server Configuration for Autonomous AI Development

## Overview
Model Context Protocol (MCP) servers enhance autonomous AI capabilities by providing access to external data, services, and specialized tools. This guide covers configuration of MCP servers specifically for the Autonomous AI Development Framework.

## Required MCP Servers

### Research and Validation Servers (Highly Recommended)

#### Exa AI - Advanced Web Search and Analysis
- **Purpose**: Comprehensive web search and content analysis for data-researcher mode
- **Capabilities**: Real-time web search, content extraction, competitive analysis
- **Configuration**: Configure in Roo Code Settings → MCP Servers
- **Environment Variable**: `EXA_API_KEY`
- **Used By**: `data-researcher`, `sparc-autonomous-adversary`

```json
{
  "server": "exa",
  "apiKey": "${EXA_API_KEY}",
  "capabilities": ["web_search", "content_analysis", "competitive_intelligence"]
}
```

#### Perplexity (Sonar) - Research Synthesis and Fact-Checking  
- **Purpose**: Research synthesis and fact-checking for rapid-fact-checker mode
- **Capabilities**: Multi-source synthesis, claim verification, trend analysis
- **Environment Variable**: `SONAR_API_KEY` (Perplexity API key)
- **Used By**: `rapid-fact-checker`, `data-researcher`

```json
{
  "server": "perplexity",
  "apiKey": "${SONAR_API_KEY}",
  "model": "sonar-pro",
  "capabilities": ["fact_checking", "research_synthesis", "claim_validation"]
}
```

#### Context7 - Technical Documentation Access
- **Purpose**: Access to up-to-date technical documentation and API references
- **Capabilities**: Library documentation, API specifications, code examples
- **Environment Variable**: `CONTEXT7_API_KEY`
- **Used By**: `sparc-architect`, `sparc-code-implementer`, `sparc-autonomous-adversary`

```json
{
  "server": "context7",
  "apiKey": "${CONTEXT7_API_KEY}",
  "capabilities": ["documentation_access", "api_reference", "code_examples"]
}
```

#### Ref Tools - URL Content Extraction
- **Purpose**: Extract and analyze content from specific URLs
- **Capabilities**: URL content extraction, document analysis, reference validation
- **Environment Variable**: `REF_API_KEY`
- **Used By**: `data-researcher`, `rapid-fact-checker`

```json
{
  "server": "ref-tools",
  "apiKey": "${REF_API_KEY}",
  "capabilities": ["url_extraction", "document_analysis", "reference_validation"]
}
```

### Development and Testing Servers (Optional)

#### Playwright - Automated Browser Testing
- **Purpose**: Automated browser testing and web application validation
- **Capabilities**: E2E testing, browser automation, accessibility testing
- **Requirements**: Node.js 18+ and browser environment
- **Used By**: `sparc-autonomous-adversary`, `sparc-qa-analyst`
- **Configuration**: Allowlist in `project/<id>/control/playwright-origins.json`

```json
{
  "server": "playwright",
  "config": {
    "allowedOrigins": ["https://example.com", "https://your-app.com"],
    "blockedPatterns": ["*://*/*login*", "*://*/*admin*"],
    "timeout": 30000,
    "headless": true
  }
}
```

## Configuration Steps

### 1. Environment Variables Setup

Create a `.env` file or set system environment variables:

```bash
# Research and validation servers
EXA_API_KEY=your-exa-api-key-here
SONAR_API_KEY=your-perplexity-api-key-here  
CONTEXT7_API_KEY=your-context7-api-key-here
REF_API_KEY=your-ref-tools-api-key-here

# Optional development servers
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000
```

### 2. Roo Code MCP Configuration

1. **Open Roo Code Settings**
   - Command Palette → "Roo Code: Settings"
   - Navigate to MCP Servers section

2. **Configure Each Server**
   - Add server configurations using environment variable references
   - Test connections to verify API keys are working
   - Enable/disable servers based on your needs

3. **Validate Configuration**
   - Use built-in Roo Code MCP testing tools
   - Verify each server responds correctly
   - Check logs for connection errors

### 3. Project-Specific Configuration

#### Playwright Origins Allowlist
Create `project/<id>/control/playwright-origins.json`:

```json
{
  "allow": [
    "https://your-staging-site.com",
    "https://api.your-service.com",
    "https://docs.your-company.com"
  ],
  "block": [
    "*://*/*login*",
    "*://*/*admin*", 
    "*://*/*password*",
    "*://localhost:*/*"
  ],
  "timeout": 30000,
  "retries": 3
}
```

#### MCP Usage Logging
Configure logging in `project/<id>/control/mcp-usage.log.jsonl`:

```jsonl
{"timestamp": "2025-08-25T10:30:00Z", "mode": "data-researcher", "server": "exa", "operation": "web_search", "topic": "payment_gateway_integration", "confidence": 0.89, "cost": 0.02}
{"timestamp": "2025-08-25T10:45:00Z", "mode": "rapid-fact-checker", "server": "perplexity", "operation": "fact_check", "topic": "pci_compliance_requirements", "confidence": 0.94, "cost": 0.05}
```

## MCP Server Usage by Mode

### Data Researcher Mode
- **Primary**: Exa (web search), Perplexity (synthesis)
- **Secondary**: Context7 (technical validation), Ref Tools (URL extraction)
- **Usage Pattern**: Broad research → focused fact-checking → technical validation

### Rapid Fact-Checker Mode  
- **Primary**: Perplexity (claim verification), Ref Tools (source validation)
- **Secondary**: Context7 (technical fact-checking)
- **Usage Pattern**: Multi-source verification → confidence assessment → evidence documentation

### Autonomous Adversary Mode
- **Primary**: Playwright (automated testing), Exa (attack vector research)
- **Secondary**: Context7 (vulnerability databases), Perplexity (threat intelligence)
- **Usage Pattern**: Automated vulnerability testing → threat research → attack simulation

### Architecture and Implementation Modes
- **Primary**: Context7 (technical documentation), Ref Tools (API specifications)
- **Secondary**: Exa (best practices research)
- **Usage Pattern**: Technical reference lookup → implementation guidance → validation

## Cost Management

### API Usage Monitoring
- Track API calls per mode and per day
- Set budgets and alerts for high-usage periods
- Optimize queries to minimize API costs

### Cost-Effective Usage Patterns
- **Batch Operations**: Group similar requests together
- **Caching**: Store frequently accessed information locally
- **Selective Usage**: Only use expensive APIs for critical decisions
- **Fallback Strategies**: Have offline alternatives for when APIs are unavailable

### Budget Allocation Example
```yaml
monthly_mcp_budget: $200
allocation:
  exa: $80          # High-value research capabilities
  perplexity: $60   # Critical fact-checking
  context7: $40     # Technical documentation access
  ref_tools: $20    # URL extraction and validation
```

## Troubleshooting

### Common Issues

**Issue**: MCP server not responding
**Solution**: 
- Check API key validity and format
- Verify network connectivity
- Review server rate limits and quotas

**Issue**: High API costs
**Solution**:
- Implement request caching
- Optimize query patterns
- Set usage alerts and budgets

**Issue**: Playwright browser failures
**Solution**:
- Ensure Node.js 18+ is installed
- Check browser environment setup
- Review allowlist configuration

### Debug Mode

Enable verbose MCP logging:
```json
{
  "mcp_debug": {
    "enabled": true,
    "log_level": "verbose",
    "trace_requests": true,
    "cost_tracking": true
  }
}
```

### Health Checks

Regular MCP server health validation:
```bash
# Test all configured servers
curl -X POST https://api.exa.ai/health -H "Authorization: Bearer $EXA_API_KEY"
curl -X POST https://api.perplexity.ai/health -H "Authorization: Bearer $SONAR_API_KEY"
```

## Security Considerations

### API Key Management
- Never commit API keys to version control
- Use environment variables or secure key management
- Rotate keys regularly
- Monitor for unauthorized usage

### Access Control
- Configure server allowlists appropriately  
- Block sensitive or dangerous operations
- Monitor API usage for anomalous patterns
- Implement rate limiting and quotas

### Data Privacy
- Ensure MCP servers comply with data privacy regulations
- Review terms of service for each provider
- Implement data retention and deletion policies
- Monitor for sensitive data exposure

This MCP configuration enables the autonomous AI development framework to access external knowledge and capabilities while maintaining security, cost control, and performance optimization.