from urllib.parse import urlparse


def get_url_domain(url: str) -> str:
    """Get the domain from a url."""
    return urlparse(url).netloc


def get_url_path(url: str) -> str:
    """Get the path from a url."""
    return urlparse(url).path
