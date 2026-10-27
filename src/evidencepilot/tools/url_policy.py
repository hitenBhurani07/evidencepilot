"""URL validation and SSRF protection policy."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class UnsafeURLError(ValueError):
    """Raised when a URL violates safety policies (SSRF, local IP, unsafe scheme)."""
    pass


ALLOWED_SCHEMES = {"http", "https"}

DISALLOWED_HOSTS = {
    "localhost",
    "metadata.google.internal",
    "169.254.169.254",  # Cloud instance metadata
    "instance-data",
}


def is_ip_private_or_local(ip_str: str) -> bool:
    """Check if an IP address string is private, loopback, reserved, or link-local."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        )
    except ValueError:
        return False


def validate_target_url(url: str, resolve_dns: bool = True) -> str:
    """Validate that a URL is safe to fetch over HTTP(S).
    
    Guards against:
    - Non-HTTP(S) schemes (file://, gopher://, data:, etc.)
    - Localhost and known cloud metadata domains
    - Private, loopback, and link-local IP addresses (SSRF prevention)
    
    Returns the cleaned URL if safe, or raises UnsafeURLError.
    """
    cleaned = url.strip()
    if not cleaned:
        raise UnsafeURLError("URL cannot be empty")

    parsed = urlparse(cleaned)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise UnsafeURLError(
            f"Scheme '{parsed.scheme}' is not allowed. Only HTTP and HTTPS are permitted."
        )

    hostname = parsed.hostname
    if not hostname:
        raise UnsafeURLError(f"Invalid URL missing hostname: '{url}'")

    host_lower = hostname.lower()
    if host_lower in DISALLOWED_HOSTS or host_lower.endswith(".local") or host_lower.endswith(".internal"):
        raise UnsafeURLError(f"Access to blocked internal/metadata host '{hostname}' is forbidden.")

    # Check direct IP addresses
    if is_ip_private_or_local(hostname):
        raise UnsafeURLError(f"Access to private/local IP '{hostname}' is forbidden.")

    # DNS resolution check for domain names if resolve_dns is True
    if resolve_dns:
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for family, socktype, proto, canonname, sockaddr in addr_info:
                ip_resolved = sockaddr[0]
                if is_ip_private_or_local(ip_resolved):
                    raise UnsafeURLError(
                        f"Host '{hostname}' resolved to private/local IP '{ip_resolved}'. Access is forbidden."
                    )
        except socket.gaierror:
            # If DNS fails to resolve here, we let the network client handle the DNS error cleanly,
            # or we could flag it. Raising UnsafeURLError on unresolvable DNS during validation:
            pass

    return cleaned


def canonicalize_url(url: str) -> str:
    """Normalize a URL for deduplication.
    
    Strips tracking query params, fragments, port 80/443 defaults, and trailing slashes.
    """
    from urllib.parse import parse_qsl, urlencode, urlunparse

    parsed = urlparse(url.strip())
    # Lowercase scheme and netloc
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Strip default ports
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    elif netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    # Filter out common marketing/tracking query parameters
    tracking_prefixes = ("utm_", "fbclid", "gclid", "ref", "mc_eid", "yclid")
    filtered_query = [
        (k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
        if not any(k.lower().startswith(prefix) for prefix in tracking_prefixes)
    ]
    query_str = urlencode(filtered_query)

    path = parsed.path
    if path.endswith("/") and len(path) > 1:
        path = path[:-1]

    # Reconstruct without fragment
    return urlunparse((scheme, netloc, path, parsed.params, query_str, ""))
