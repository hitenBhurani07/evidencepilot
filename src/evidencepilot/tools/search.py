"""Web search tool providing normalized SourceItem evidence."""

from __future__ import annotations

import logging
from typing import List, Optional
from urllib.parse import urlparse

from evidencepilot.providers.base import ProviderError, SearchProvider, SearchResult
from evidencepilot.schemas.research import SourceItem
from evidencepilot.tools.url_policy import canonicalize_url

logger = logging.getLogger(__name__)


class SearchTool:
    """Tool for querying web search and returning normalized source items."""
    
    def __init__(self, provider: SearchProvider, default_max_results: int = 5):
        self.provider = provider
        self.default_max_results = default_max_results

    def execute(
        self,
        query: str,
        max_results: Optional[int] = None,
        id_prefix: str = "S",
        start_index: int = 1,
    ) -> List[SourceItem]:
        """Execute a search query and map raw results to normalized SourceItems."""
        limit = max_results or self.default_max_results
        cleaned_query = query.strip()
        if not cleaned_query:
            return []

        try:
            raw_results: List[SearchResult] = self.provider.search(cleaned_query, max_results=limit)
        except ProviderError as p_err:
            logger.error("Search provider error on query '%s': %s", cleaned_query, p_err)
            raise

        sources: List[SourceItem] = []
        for idx, item in enumerate(raw_results, start=start_index):
            canon_url = canonicalize_url(item.url)
            parsed_host = urlparse(canon_url).netloc.lower()

            # Default initial quality score based on provider score if available
            initial_score = item.score if item.score is not None else 0.7

            source = SourceItem(
                id=f"{id_prefix}{idx}",
                url=canon_url,
                title=item.title or parsed_host or "Untitled Document",
                snippet=item.snippet,
                full_content=item.raw_content,
                domain=parsed_host,
                quality_score=min(1.0, max(0.0, initial_score)),
                is_filtered_out=False,
            )
            sources.append(source)

        return sources
