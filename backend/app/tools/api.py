import requests


def api_get(url: str) -> dict:
    """
    Send an HTTP GET request to a REST API.
    """

    try:
        response = requests.get(
            url,
            timeout=10,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise RuntimeError(
            f"API request failed: {exc}"
        ) from exc

    try:
        return response.json()

    except ValueError as exc:
        raise RuntimeError(
            "API returned a non-JSON response."
        ) from exc