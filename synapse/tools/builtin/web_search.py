from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo.
    
    Args:
        query: The search query.
        max_results: Maximum number of results to return.
        
    Returns:
        Formatted string containing the search results.
    """
    results = DDGS().text(query, max_results=max_results)
    
    if not results:
        return f"No results found for '{query}'."
        
    formatted_results = []
    for r in results:
        title = r.get('title', 'No title')
        url = r.get('href', r.get('url', 'No URL'))
        body = r.get('body', 'No body text')
        formatted_results.append(f"Title: {title}\nURL: {url}\nBody: {body}\n---")
        
    return "\n".join(formatted_results)
