#!/usr/bin/env python3
"""
AI Newsletter Curation Agent using Strands SDK and Ollama
Curates tech/AI newsletter content and generates markdown output
"""

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

from tools.tools import fetch_rss_feeds, scrape_article_content, filter_relevant_articles, generate_newsletter_markdown

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsletterConfig:
    """Configuration for the newsletter curation agent"""

    def __init__(self):
        self.sources = [
            "https://feeds.feedburner.com/oreilly/radar",
            "https://news.ycombinator.com/rss",
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/index.xml",
            "https://venturebeat.com/feed/",
            "https://www.wired.com/feed/rss"
        ]
        self.max_articles = 20
        self.lookback_days = 7
        self.ai_keywords = [
            "artificial intelligence", "machine learning", "AI", "ML", "LLM",
            "large language model", "generative AI", "deep learning", "neural network",
            "transformer", "GPT", "Claude", "ChatGPT", "automation", "robotics"
        ]
        self.tech_keywords = [
            "technology", "software", "programming", "startup", "tech company",
            "cloud computing", "cybersecurity", "blockchain", "cryptocurrency",
            "web development", "mobile app", "API", "database", "DevOps"
        ]



class NewsletterCurationAgent:
    """Main agent class for newsletter curation"""

    def __init__(self, ollama_host: str = "http://localhost:11434", model_id: str = "qwen2.5:3b"):
        self.config = NewsletterConfig()

        # Initialize Ollama model
        self.ollama_model = OllamaModel(
            host=ollama_host,
            model_id=model_id,
            temperature=0.3,  # Lower temperature for more consistent output
            keep_alive="10m"
        )

        # Create agent with tools
        self.agent = Agent(
            model=self.ollama_model,
            tools=[
                fetch_rss_feeds,
                scrape_article_content,
                filter_relevant_articles,
                generate_newsletter_markdown,
                file_write
            ]
        )

    def _generate_newsletter_markdown_direct(self, articles: List[Dict],
                                             newsletter_title: str = "AI & Tech Weekly") -> str:
        """Generate newsletter markdown directly (not as a tool)"""
        date_str = datetime.now().strftime("%B %d, %Y")

        markdown = f"""# {newsletter_title}
    *{date_str}*

    Welcome to this week's curated selection of AI and technology news. Here are the most important stories and developments:

    ## 🔥 Top Stories

    """

        for i, article in enumerate(articles[:5], 1):
            source_domain = urlparse(article['link']).netloc
            markdown += f"""### {i}. {article['title']}

    **Source:** {source_domain}  
    **Link:** [{article['title']}]({article['link']})

    {article.get('description', 'No description available.')}

    ---

    """

        if len(articles) > 5:
            markdown += "\n## 📖 Additional Reading\n\n"
            for article in articles[5:]:
                source_domain = urlparse(article['link']).netloc
                markdown += f"- [{article['title']}]({article['link']}) - *{source_domain}*\n"

        markdown += f"""

    ## 🤖 About This Newsletter

    This newsletter was curated by an AI agent using the latest developments in artificial intelligence and technology. 
    Articles were automatically selected based on relevance, novelty, and potential impact.

    *Generated on {date_str}*
    """

        return markdown

    def _save_newsletter_direct(self, content: str, filename: str) -> str:
        """Save newsletter directly (not as a tool)"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Newsletter saved to {filename}")
            return f"Newsletter successfully saved to {filename}"
        except Exception as e:
            error_msg = f"Error saving newsletter: {e}"
            logger.error(error_msg)
            return error_msg

    def _fetch_rss_feeds_direct(self, sources: List[str], max_articles: int = 50) -> List[Dict[str, Any]]:
        """Direct RSS fetching (copy the logic from fetch_rss_feeds)"""
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

    def curate_newsletter(self, output_filename: str = "newsletter.md") -> str:
        """
        Main method to curate and generate newsletter

        Args:
            output_filename: Filename for the generated newsletter

        Returns:
            Path to the generated newsletter file
        """
        logger.info("Starting newsletter curation process...")

        try:
            # Step 1: Fetch articles from RSS feeds
            logger.info("Fetching articles from RSS feeds...")
            articles = fetch_rss_feeds(self.config.sources, self.config.max_articles)
            logger.info(f"Fetched {len(articles)} articles")

            # Step 2: Filter for AI/tech relevance
            logger.info("Filtering articles for relevance...")
            all_keywords = self.config.ai_keywords + self.config.tech_keywords
            relevant_articles = filter_relevant_articles(articles, all_keywords, 15)
            logger.info(f"Found {len(relevant_articles)} relevant articles")

            # Step 3: Enhance top articles with full content
            logger.info("Enhancing top articles with full content...")
            for article in relevant_articles[:5]:
                content = scrape_article_content(article['link'])
                article['content'] = content

            # Step 4: Use AI agent to analyze and rank articles
            analysis_prompt = f"""
            Analyze these {len(relevant_articles)} articles and help me create a newsletter. 
            Consider factors like:
            - Novelty and impact of the story
            - Relevance to AI and technology trends
            - Quality of the source
            - Potential interest to tech professionals

            Articles data: {json.dumps(relevant_articles[:10], indent=2)}

            Please suggest the top 5 articles for the newsletter and provide brief explanations for why each is significant.
            """

            logger.info("Getting AI analysis of articles...")
            analysis = self.agent(analysis_prompt)
            logger.info("AI analysis completed")

            # Step 5: Generate newsletter markdown
            logger.info("Generating newsletter markdown...")
            print(
                f"DEBUG: type of self._generate_newsletter_markdown_direct: {type(self._generate_newsletter_markdown_direct)}")
            print(
                f"DEBUG: relevant_articles type: {type(relevant_articles)}, length: {len(relevant_articles) if relevant_articles else 'None'}")

            try:
                newsletter_content = self._generate_newsletter_markdown_direct(relevant_articles)
                print(f"DEBUG: newsletter_content generated successfully, type: {type(newsletter_content)}")
            except Exception as e:
                print(f"DEBUG: Error in _generate_newsletter_markdown_direct: {e}")
                import traceback
                traceback.print_exc()

            # from newsletter_tools import generate_newsletter_markdown as gen_newsletter
            # newsletter_content = self._generate_newsletter_markdown_direct(relevant_articles)

            # Step 6: Save newsletter to file
            save_result = self._save_newsletter_direct(newsletter_content, output_filename)
            logger.info(save_result)

            # file_write(output_filename, newsletter_content)
            logger.info(f"Newsletter saved to {output_filename}")

            return output_filename

        except Exception as e:
            logger.error(f"Error in newsletter curation: {e}")
            raise


def main():
    """Main execution function"""
    try:
        # Initialize the newsletter agent
        agent = NewsletterCurationAgent()

        # Generate newsletter
        print("🤖 Starting AI Newsletter Curation Agent...")
        print("📡 Fetching latest AI and tech news...")

        output_file = agent.curate_newsletter("ai_tech_newsletter.md")

        print(f"✅ Newsletter generated successfully: {output_file}")
        print("📄 Check the markdown file for your curated newsletter!")

    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Main execution error: {e}")


if __name__ == "__main__":
    main()