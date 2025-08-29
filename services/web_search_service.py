"""
Web Search Service - Special Skill for VoxAura Agent
Provides web search functionality using DuckDuckGo (no API key required)
"""
import os
import logging
import requests
import json
from typing import Dict, Any, Optional
import urllib.parse

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        """Initialize web search service using DuckDuckGo Instant Answer API"""
        self.base_url = "https://api.duckduckgo.com/"
        logger.info("✅ Web search service initialized (DuckDuckGo)")

    def search_web(self, query: str) -> Dict[str, Any]:
        """
        Search the web using DuckDuckGo Instant Answer API

        Args:
            query: Search query string

        Returns:
            Dict containing search results
        """
        try:
            # Use DuckDuckGo Instant Answer API (no API key required)
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }

            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Extract relevant information
                abstract = data.get('Abstract', '')
                definition = data.get('Definition', '')
                answer = data.get('Answer', '')

                # Get related topics
                related_topics = []
                for topic in data.get('RelatedTopics', [])[:3]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        related_topics.append(topic['Text'])

                # Get infobox data
                infobox = data.get('Infobox', {})
                infobox_content = []
                if infobox and 'content' in infobox:
                    for item in infobox['content'][:3]:
                        if 'label' in item and 'value' in item:
                            infobox_content.append(f"{item['label']}: {item['value']}")

                # Determine best answer
                best_answer = answer or abstract or definition
                if not best_answer and related_topics:
                    best_answer = related_topics[0]

                search_info = {
                    'success': True,
                    'query': query,
                    'answer': best_answer,
                    'abstract': abstract,
                    'definition': definition,
                    'instant_answer': answer,
                    'related_topics': related_topics,
                    'infobox': infobox_content,
                    'result_count': len(related_topics) + (1 if best_answer else 0),
                    'source': data.get('AbstractSource', 'DuckDuckGo')
                }

                logger.info(f"Web search successful for: {query}")
                return search_info

            else:
                return self._get_fallback_search(query)

        except requests.RequestException as e:
            logger.error(f"Web search API request failed: {e}")
            return self._get_fallback_search(query)
        except Exception as e:
            logger.error(f"Web search service error: {e}")
            return self._get_fallback_search(query)

    def _get_fallback_search(self, query: str) -> Dict[str, Any]:
        """Generate fallback search response when API fails"""
        return {
            'success': False,
            'query': query,
            'error': 'Search service temporarily unavailable',
            'fallback_response': f"I'm unable to search for '{query}' right now due to connectivity issues."
        }

    def format_search_response(self, search_data: Dict[str, Any], persona: str = 'default') -> str:
        """
        Format search data into a natural language response based on persona

        Args:
            search_data: Search information dictionary
            persona: Agent persona for response style

        Returns:
            Formatted search response string
        """
        if not search_data['success']:
            if persona == 'pirate':
                return f"Arrr! {search_data.get('fallback_response', search_data.get('error', 'Search failed'))} The digital seas be rough today, matey!"
            else:
                return search_data.get('fallback_response', search_data.get('error', 'I encountered an error while searching.'))

        query = search_data['query']
        answer = search_data.get('answer', '')
        abstract = search_data.get('abstract', '')
        definition = search_data.get('definition', '')
        related_topics = search_data.get('related_topics', [])
        infobox = search_data.get('infobox', [])

        if persona == 'pirate':
            response = f"Ahoy! I've sailed the digital seas searchin' for '{query}', and here's what I've found, me hearty:\n\n"

            if answer:
                response += f"⚓ Direct Answer: {answer}\n\n"
            elif definition:
                response += f"⚓ Definition: {definition}\n\n"
            elif abstract:
                response += f"⚓ What I Found: {abstract}\n\n"

            if infobox:
                response += "📜 Key Details:\n"
                for info in infobox:
                    response += f"• {info}\n"
                response += "\n"

            if related_topics:
                response += "🗺️ Related Discoveries:\n"
                for i, topic in enumerate(related_topics[:2], 1):
                    response += f"{i}. {topic}\n"

            if not (answer or definition or abstract):
                response += "I searched the seven seas but couldn't find much treasure about that topic, matey!"

            response += "\nAnything else ye want me to search for, me trusted crew member?"

        else:
            response = f"I searched for '{query}' and here's what I found:\n\n"

            if answer:
                response += f"📝 Answer: {answer}\n\n"
            elif definition:
                response += f"📝 Definition: {definition}\n\n"
            elif abstract:
                response += f"📝 Summary: {abstract}\n\n"

            if infobox:
                response += "ℹ️ Key Information:\n"
                for info in infobox:
                    response += f"• {info}\n"
                response += "\n"

            if related_topics:
                response += "🔗 Related Topics:\n"
                for i, topic in enumerate(related_topics[:2], 1):
                    response += f"{i}. {topic}\n"

            if not (answer or definition or abstract):
                response += "I couldn't find specific information about that topic. Try rephrasing your search query."

            response += "\nWould you like me to search for anything else?"

        return response