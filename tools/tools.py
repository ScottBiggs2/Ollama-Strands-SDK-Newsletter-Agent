import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urlparse, urljoin
import re

# Strands SDK imports
from strands import Agent, tool
from strands.models.ollama import OllamaModel
from strands_tools import file_write

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def fetch_rss_feeds(sources: List[str], max_articles: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch articles from RSS feeds

    Args:
        sources: List of RSS feed URLs
        max_articles: Maximum number of articles to fetch per source

    Returns:
        List of article dictionaries with title, link, description, date
    """
    articles = []

    for source in sources:
        try:
            logger.info(f"Fetching RSS feed: {source}")
            feed = feedparser.parse(source)

            for entry in feed.entries[:max_articles]:
                article = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "description": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "source": source,
                    "content": ""
                }
                articles.append(article)

        except Exception as e:
            logger.error(f"Error fetching RSS feed {source}: {e}")
            continue

    return articles


@tool
def scrape_article_content(url: str) -> str:
    """
    Scrape the main content from an article URL

    Args:
        url: Article URL to scrape

    Returns:
        Extracted article text content
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Try to find main content areas
        content_selectors = [
            'article', '[role="main"]', '.article-content',
            '.post-content', '.entry-content', '.content'
        ]

        content = ""
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(strip=True, separator='\n')
                break

        if not content:
            # Fallback to body content
            content = soup.get_text(strip=True, separator='\n')

        # Clean up content
        content = re.sub(r'\n\s*\n', '\n\n', content)
        return content[:3000]  # Limit content length

    except Exception as e:
        logger.error(f"Error scraping article {url}: {e}")
        return ""


@tool
def filter_relevant_articles(articles: List[Dict], keywords: List[str], max_results: int = 10) -> List[Dict]:
    """
    Filter articles based on relevance to AI/tech keywords

    Args:
        articles: List of article dictionaries
        keywords: Keywords to filter by
        max_results: Maximum number of articles to return

    Returns:
        Filtered and scored list of articles
    """
    scored_articles = []

    for article in articles:
        score = 0
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()

        # Score based on keyword matches
        for keyword in keywords:
            if keyword.lower() in text:
                score += 1

        if score > 0:
            article['relevance_score'] = score
            scored_articles.append(article)

    # Sort by relevance score
    scored_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
    return scored_articles[:max_results]


@tool
def generate_newsletter_markdown(articles: List[Dict], newsletter_title: str = "AI & Tech Weekly") -> str:
    """
    Generate a markdown newsletter from curated articles

    Args:
        articles: List of curated article dictionaries
        newsletter_title: Title for the newsletter

    Returns:
        Formatted markdown newsletter content
    """
    date_str = datetime.now().strftime("%B %d, %Y")

    markdown = f"""# {newsletter_title}
*{date_str}*

Welcome to this week's curated selection of AI and technology news. Here are the most important stories and developments:

## 🔥 Top Stories
"""

    for i, article in enumerate(articles[:5], 1):
        markdown += f"""### {i}. {article['title']}

**Source:** {urlparse(article['link']).netloc}  
**Link:** [{article['title']}]({article['link']})

{article.get('description', 'No description available.')}

---

"""

    if len(articles) > 5:
        markdown += "\n## 📖 Additional Reading\n\n"
        for article in articles[5:]:
            markdown += f"- [{article['title']}]({article['link']}) - *{urlparse(article['link']).netloc}*\n"

    markdown += f"""

## 🤖 About This Newsletter

This newsletter was curated by an AI agent using the latest developments in artificial intelligence and technology. 
Articles were automatically selected based on relevance, novelty, and potential impact.

*Generated on {date_str}*
"""

    return markdown

