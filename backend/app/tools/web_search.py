import os

from tavily import TavilyClient


def web_search(query: str) -> list[dict]:
    """
    Search the web and return only the useful information
    required by the agent.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY is not configured."
        )

    client = TavilyClient(
        api_key=api_key
    )

    response = client.search(
        query=query,
        max_results=5,
    )

    results = []

    for item in response.get("results", []):

        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
            }
        )

    return results