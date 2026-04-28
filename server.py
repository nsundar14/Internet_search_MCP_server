"""
Internet Search MCP Server using DuckDuckGo
FastMCP-based server for web search queries
"""

from fastmcp import FastMCP
from duckduckgo_search import DDGS
from typing import List, Dict, Any
import os
import httpx

# Initialize FastMCP server
mcp = FastMCP("Internet Search MCP")

# Proxy configuration (if needed in corporate environment)
PROXIES = None
if os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY"):
    PROXIES = {
        "http://": os.getenv("HTTP_PROXY"),
        "https://": os.getenv("HTTPS_PROXY")
    }

@mcp.tool()
def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo and return relevant results.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5, max: 20)
    
    Returns:
        List of search results with title, link, and snippet
    """
    try:
        if max_results > 20:
            max_results = 20
        
        if max_results < 1:
            max_results = 1
        
        results = []
        
        # Create DDGS instance with proxy support
        ddgs = DDGS(proxies=PROXIES, timeout=20)
        search_results = list(ddgs.text(query, max_results=max_results))
        
        for result in search_results:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })
        
        if not results:
            return [{"message": "No results found"}]
        
        return results
    except Exception as e:
        error_msg = str(e)
        if "ConnectError" in error_msg or "ProxyError" in error_msg:
            return [{"error": "Network connection failed. Please check your internet connection or proxy settings."}]
        return [{"error": f"Search failed: {error_msg}"}]


@mcp.tool()
def search_news(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search for news articles using DuckDuckGo News.
    
    Args:
        query: The news search query string
        max_results: Maximum number of results to return (default: 5, max: 20)
    
    Returns:
        List of news articles with title, link, date, and snippet
    """
    try:
        if max_results > 20:
            max_results = 20
        
        if max_results < 1:
            max_results = 1
        
        results = []
        
        # Create DDGS instance with proxy support
        ddgs = DDGS(proxies=PROXIES, timeout=20)
        news_results = list(ddgs.news(query, max_results=max_results))
        
        for result in news_results:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "date": result.get("date", ""),
                "snippet": result.get("body", ""),
                "source": result.get("source", "")
            })
        
        if not results:
            return [{"message": "No news results found"}]
        
        return results
    except Exception as e:
        error_msg = str(e)
        if "ConnectError" in error_msg or "ProxyError" in error_msg:
            return [{"error": "Network connection failed. Please check your internet connection or proxy settings."}]
        return [{"error": f"News search failed: {error_msg}"}]


if __name__ == "__main__":
    # Run the MCP server with SSE transport
    # Bind to 0.0.0.0 to allow external access in Docker/Kubernetes
    mcp.run(transport="sse", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
