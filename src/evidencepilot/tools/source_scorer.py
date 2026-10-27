"""Evidence hygiene, deduplication, and source quality scoring."""

from __future__ import annotations

import logging
from typing import List, Tuple
from urllib.parse import urlparse

from evidencepilot.schemas.research import SourceItem
from evidencepilot.tools.url_policy import canonicalize_url

logger = logging.getLogger(__name__)

# Transparent domain credibility heuristics
AUTHORITATIVE_TLDS = (".gov", ".edu", ".mil")
REPUTABLE_DOMAINS = {
    "wikipedia.org",
    "arxiv.org",
    "github.com",
    "reuters.com",
    "bloomberg.com",
    "nature.com",
    "ieee.org",
    "acm.org",
    "cisa.gov",
    "nist.gov",
}


def compute_source_quality_score(source: SourceItem) -> float:
    """Compute an explainable, bounded credibility score [0.0, 1.0] for a source."""
    base_score = 0.50

    domain = source.domain.lower() if source.domain else urlparse(source.url).netloc.lower()
    # TLD authority heuristic
    if any(domain.endswith(tld) for tld in AUTHORITATIVE_TLDS):
        base_score += 0.25
    elif any(rep in domain for rep in REPUTABLE_DOMAINS):
        base_score += 0.20

    # Content richness
    snippet_len = len(source.snippet.strip())
    content_len = len(source.full_content.strip()) if source.full_content else 0

    if content_len > 1000:
        base_score += 0.15
    elif content_len > 50:
        base_score += 0.10
    elif snippet_len > 50:
        base_score += 0.05

    # Penalize if almost no text is present
    if content_len == 0 and snippet_len < 30:
        base_score -= 0.30

    return max(0.05, min(0.98, round(base_score, 2)))


class SourceQualityFilter:
    """Cleans, deduplicates, scores, and filters evidence sources."""

    def __init__(self, min_text_length: int = 25, max_sources: int = 8):
        self.min_text_length = min_text_length
        self.max_sources = max_sources

    def process(self, sources: List[SourceItem]) -> Tuple[List[SourceItem], List[SourceItem]]:
        """Deduplicate, score, and filter a list of sources.
        
        Returns:
            Tuple of (kept_sources, filtered_out_sources).
        """
        seen_urls = set()
        kept: List[SourceItem] = []
        filtered: List[SourceItem] = []

        for item in sources:
            canon = canonicalize_url(item.url)
            item.url = canon
            if not item.domain:
                item.domain = urlparse(canon).netloc.lower()
            
            # Check 1: Duplicate canonical URL
            if canon in seen_urls:
                item.is_filtered_out = True
                item.filter_reason = "Duplicate URL"
                filtered.append(item)
                continue
            seen_urls.add(canon)

            # Check 2: Minimum text availability
            total_text_len = len(item.snippet.strip()) + (len(item.full_content.strip()) if item.full_content else 0)
            if total_text_len < self.min_text_length:
                item.is_filtered_out = True
                item.filter_reason = f"Insufficient content length ({total_text_len} chars < {self.min_text_length})"
                filtered.append(item)
                continue

            # Check 3: Calculate updated quality score
            item.quality_score = compute_source_quality_score(item)
            item.is_filtered_out = False
            kept.append(item)

        # Sort kept sources by quality score descending
        kept.sort(key=lambda s: s.quality_score, reverse=True)

        # Cap at max_sources if needed, moving surplus to filtered
        if len(kept) > self.max_sources:
            surplus = kept[self.max_sources:]
            for s in surplus:
                s.is_filtered_out = True
                s.filter_reason = f"Exceeded maximum source budget ({self.max_sources})"
                filtered.append(s)
            kept = kept[:self.max_sources]

        # Re-index kept sources cleanly: S1, S2, ...
        for idx, s in enumerate(kept, start=1):
            s.id = f"S{idx}"

        return kept, filtered
