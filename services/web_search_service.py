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
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        """Initialize web search service using DuckDuckGo Instant Answer API"""
        self.base_url = "https://api.duckduckgo.com/"
        logger.info("✅ Web search service initialized (DuckDuckGo)")

    def search_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search the web using DuckDuckGo with improved error handling and rate limit management"""
        try:
            logger.info(f"🔍 Searching web for: {query}")

            # Use DuckDuckGo search with better rate limiting handling
            results = []
            search_attempts = 0
            max_attempts = 2  # Reduce attempts to avoid rate limiting

            while search_attempts < max_attempts and len(results) == 0:
                try:
                    search_attempts += 1
                    logger.info(f"🔍 Search attempt {search_attempts}/{max_attempts}")

                    # Add longer delay between attempts to avoid rate limiting
                    if search_attempts > 1:
                        import time
                        time.sleep(3)  # Longer wait time

                    with DDGS() as ddgs:
                        # Use different parameters to avoid rate limiting
                        search_results = ddgs.text(
                            query, 
                            max_results=min(max_results, 3),  # Limit results to reduce load
                            safesearch='moderate',
                            region='wt-wt',  # Use worldwide region
                            timelimit=None
                        )

                        for result in search_results:
                            if len(results) >= max_results:
                                break
                            results.append({
                                'title': result.get('title', ''),
                                'snippet': result.get('body', ''),
                                'url': result.get('href', ''),
                                'source': 'DuckDuckGo'
                            })

                    if len(results) > 0:
                        break

                except Exception as search_error:
                    error_msg = str(search_error).lower()
                    logger.warning(f"🔍 Search attempt {search_attempts} failed: {str(search_error)}")
                    
                    # Check if it's a rate limit error
                    if 'ratelimit' in error_msg or 'rate limit' in error_msg:
                        logger.warning("🔍 Rate limit detected, using fallback knowledge")
                        break  # Don't retry on rate limit
                    
                    if search_attempts < max_attempts:
                        import time
                        time.sleep(2)  # Wait before retry

            logger.info(f"🔍 Found {len(results)} search results after {search_attempts} attempts")

            # If no results due to rate limiting or errors, provide knowledge-based fallback
            if len(results) == 0:
                fallback_response = self._get_knowledge_based_response(query)
                return {
                    'success': True,  # Mark as success to use fallback
                    'results': [],
                    'query': query,
                    'result_count': 0,
                    'search_engine': 'Knowledge Base (Fallback)',
                    'fallback_needed': True,
                    'fallback_response': fallback_response,
                    'error': 'Search temporarily unavailable - using built-in knowledge'
                }

            return {
                'success': True,
                'results': results,
                'query': query,
                'result_count': len(results),
                'search_engine': 'DuckDuckGo'
            }

        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            fallback_response = self._get_knowledge_based_response(query)
            return {
                'success': True,  # Mark as success to trigger fallback response
                'error': f'Web search temporarily unavailable: {str(e)}',
                'results': [],
                'query': query,
                'result_count': 0,
                'fallback_needed': True,
                'fallback_response': fallback_response
            }

    def _get_fallback_search(self, query: str) -> Dict[str, Any]:
        """Generate fallback search response when API fails"""
        return {
            'success': False,
            'query': query,
            'error': 'Search service temporarily unavailable',
            'fallback_response': f"I'm unable to search for '{query}' right now due to connectivity issues."
        }

    def _get_knowledge_based_response(self, query: str) -> str:
        """Provide knowledge-based responses for common queries when search fails"""
        query_lower = query.lower().strip()
        
        # AI and Technology related queries
        if any(term in query_lower for term in ['ai', 'artificial intelligence', 'machine learning', 'ml']):
            return "AI (Artificial Intelligence) refers to computer systems that can perform tasks typically requiring human intelligence. This includes machine learning, natural language processing, computer vision, and robotics. Modern AI like ChatGPT, Google's Gemini, and other LLMs use deep learning neural networks trained on vast datasets."
        
        elif any(term in query_lower for term in ['llm', 'large language model', 'language model']):
            return "LLM stands for Large Language Model. These are AI systems trained on massive amounts of text data to understand and generate human-like responses. Examples include GPT (OpenAI), Claude (Anthropic), Gemini (Google), and LLaMA (Meta). They can help with writing, coding, analysis, and conversation."
        
        elif any(term in query_lower for term in ['chatgpt', 'gpt', 'openai']):
            return "ChatGPT is an AI chatbot developed by OpenAI, based on their GPT (Generative Pre-trained Transformer) language models. It can engage in conversations, answer questions, help with writing, coding, and various other tasks using natural language processing."
        
        elif any(term in query_lower for term in ['programming', 'coding', 'development', 'software']):
            return "Programming is the process of creating computer software using programming languages like Python, JavaScript, Java, C++, and others. It involves writing instructions that computers can execute to solve problems and create applications."
        
        elif any(term in query_lower for term in ['python', 'javascript', 'java', 'c++', 'html', 'css']):
            return f"You're asking about {query}! This appears to be related to programming or web development. These are popular technologies used to build software applications and websites. Would you like more specific information about any particular aspect?"
        
        # Science and general knowledge
        elif any(term in query_lower for term in ['science', 'physics', 'chemistry', 'biology']):
            return f"You're asking about {query} in science! This is a broad field with many fascinating aspects. Science helps us understand the natural world through observation, experimentation, and analysis. What specific area interests you most?"
        
        elif any(term in query_lower for term in ['history', 'historical', 'past']):
            return f"You're asking about {query} in history! History helps us understand past events, cultures, and civilizations. It provides valuable lessons and context for understanding our present world. What particular period or aspect interests you?"
        
        elif any(term in query_lower for term in ['weather', 'climate', 'temperature']):
            return "I can help with weather information! Try asking about the weather in a specific city, like 'What's the weather in New York?' I can provide current conditions, forecasts, and more detailed weather analysis."
        
        # Default response for unknown queries
        else:
            return f"I'd be happy to help you learn about '{query}'! While I can't search the web right now, I can provide general information. Could you ask a more specific question about what aspect of '{query}' interests you most?"

    def format_search_response(self, search_data: Dict[str, Any], persona: str = None) -> str:
        """Format search results into natural language response"""
        query = search_data.get('query', 'your search')

        # Handle fallback cases with knowledge-based responses
        if search_data.get('fallback_needed') or not search_data.get('success', False):
            fallback_response = search_data.get('fallback_response')
            if fallback_response:
                if persona == 'pirate':
                    return f"Arrr! The search winds be blowin' against us, matey! But fear not - {fallback_response}"
                else:
                    return fallback_response
            else:
                if persona == 'pirate':
                    return f"Arrr! The search winds be blowin' against us, matey! I can't search the digital seas for '{query}' right now, but I can still help ye with other questions about it!"
                else:
                    return f"I'm unable to search for '{query}' right now due to connectivity issues, but I can still provide general information about it. What specifically would you like to know?"

        results = search_data.get('results', [])

        if not results:
            # Use knowledge-based fallback when no results
            fallback_response = self._get_knowledge_based_response(query)
            if persona == 'pirate':
                return f"Arrr! I sailed the digital seas lookin' for '{query}' but found no treasure, matey! However, {fallback_response}"
            else:
                return fallback_response

        # Format results
        if persona == 'pirate':
            response = f"Ahoy! I found some treasure while searchin' for '{query}':\n\n"
            for i, result in enumerate(results[:3], 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   {result['snippet'][:150]}...\n"
                response += f"   Source: {result['url']}\n\n"
            response += "These be the finest results from me search, matey! ⚓"
        else:
            response = f"Here's what I found about '{query}':\n\n"
            for i, result in enumerate(results[:3], 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   {result['snippet'][:150]}...\n"
                response += f"   Source: {result['url']}\n\n"
            response += f"Found {search_data['result_count']} results using {search_data['search_engine']}."

        return response
