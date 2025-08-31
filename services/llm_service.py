"""
Language Model Service
Handles Google Gemini integration for conversational AI with streaming support
"""
import os
import logging
import re
from typing import Dict, Any, List, Iterator, Callable, Optional
import logging

logger = logging.getLogger(__name__)


# LLM imports with enhanced error handling
GOOGLE_AI_AVAILABLE = False
try:
    # Set environment variables to reduce verbosity
    os.environ['GRPC_VERBOSITY'] = 'ERROR'
    os.environ['GLOG_minloglevel'] = '2'

    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
    logging.info("✅ Google Generative AI imported successfully")
except ImportError as e:
    logging.warning(f"Google Generative AI not available (ImportError): {e}")
    GOOGLE_AI_AVAILABLE = False
except OSError as e:
    logging.warning(f"Google Generative AI not available (OSError - likely libstdc++ issue): {e}")
    GOOGLE_AI_AVAILABLE = False
except Exception as e:
    logging.warning(f"Google Generative AI not available (Unexpected error): {e}")
    GOOGLE_AI_AVAILABLE = False

class LLMService:
    def __init__(self, api_key=None, gemini_api_key=None, weather_api_key=None):
        """Initialize the LLM service with Gemini and special skills"""
        # Support both api_key and gemini_api_key parameters for backward compatibility
        self.api_key = api_key or gemini_api_key

        # Import services
        from .weather_service import WeatherService
        from .web_search_service import WebSearchService
        from .study_assistant_service import StudyAssistantService
        from .pdf_service import PDFService

        self.weather_service = WeatherService(api_key=weather_api_key)
        self.web_search_service = WebSearchService()
        self.study_assistant = StudyAssistantService()
        self.pdf_service = PDFService()

        # API Key handling: Use provided keys, fallback to environment variables
        self.api_key = self.api_key or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_AI_API_KEY')
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured")
            print("❌ GOOGLE_AI_API_KEY not configured")
            print("💡 Please add GOOGLE_AI_API_KEY to your Secrets panel")
            print("💡 Get your API key from: https://aistudio.google.com/")
            logger.info("Using fallback responses")
            self.configured = False
            return

        if not GOOGLE_AI_AVAILABLE:
            logger.warning("Google Generative AI library not available")
            print("❌ Google Generative AI library not available")
            self.configured = False
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.configured = True
            logger.info("✅ Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.configured = False

        # Persona-specific voice mapping
        self.persona_voices = {
            'pirate': 'en-US-davis',  # Deeper, more masculine voice for pirate
            'default': 'en-US-sarah'  # Default voice
        }

    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return self.configured

    def get_voice_for_persona(self, persona: str) -> str:
        """Get the appropriate voice ID for the given persona"""
        return self.persona_voices.get(persona, 'en-US-sarah')

    def generate_response(self, chat_messages: List[Dict[str, str]], user_message: str, persona: str = None) -> Dict[str, Any]:
        """
        Generate conversational response using Gemini

        Args:
            chat_messages: Chat history
            user_message: Current user message
            persona: The persona for the agent

        Returns:
            Dict containing response and metadata
        """
        # Check for PDF processing requests first (prioritize over other skills)
        pdf_result = self._handle_pdf_request(user_message, persona)
        if pdf_result:
            return pdf_result

        # Check for weather requests (special skill)
        weather_result = self._handle_weather_request(user_message, persona)
        if weather_result:
            return weather_result

        # Check for web search requests (special skill)
        search_result = self._handle_search_request(user_message, persona)
        if search_result:
            return search_result

        # Check for study assistant requests (special skill)
        study_result = self._handle_study_request(user_message, persona)
        if study_result:
            return study_result

        if not self.is_configured():
            return {
                'success': False,
                'error': 'LLM service not configured',
                'fallback_response': "I'm having trouble connecting to my AI services right now."
            }

        try:
            # Build conversation context
            context = self._build_conversation_context(chat_messages, user_message, persona)

            logger.info(f"Generating response for {len(chat_messages)} message(s) in context")

            # Generate response
            response = self.model.generate_content(context)

            # Extract response text
            response_text = response.text if response and response.text else ""

            if not response_text:
                return {
                    'success': False,
                    'error': 'Empty response from LLM',
                    'fallback_response': "I apologize, but I couldn't generate a response to your query."
                }

            # Truncate if too long for TTS
            if len(response_text) > 3000:
                response_text = response_text[:2900] + "..."
                logger.info("Response truncated to fit TTS character limit")

            logger.info(f"LLM response generated: {len(response_text)} characters")

            return {
                'success': True,
                'response': response_text,
                'model_used': 'gemini-1.5-flash',
                'character_count': len(response_text)
            }

        except Exception as e:
            logger.error(f"LLM service error: {str(e)}")

            # Generate contextual fallback responses
            fallback_response = self._generate_fallback_response(user_message)

            return {
                'success': False,
                'error': f'LLM service error: {str(e)}',
                'fallback_response': fallback_response
            }

    def generate_streaming_response(self, chat_messages: List[Dict[str, str]], user_message: str, persona: str = None,
                                  callback: Callable[[str], None] = None) -> Dict[str, Any]:
        """
        Generate streaming conversational response using Gemini

        Args:
            chat_messages: Chat history
            user_message: Current user message
            persona: The persona for the agent
            callback: Optional callback function to handle streaming chunks

        Returns:
            Dict containing full response and metadata
        """
        # Check for PDF processing requests first (prioritize over other skills)
        pdf_result = self._handle_pdf_request(user_message, persona)
        if pdf_result:
            # Simulate streaming for PDF responses
            if callback:
                response_text = pdf_result['response']
                words = response_text.split(' ')
                chunk_size = 3
                for i in range(0, len(words), chunk_size):
                    chunk = ' '.join(words[i:i+chunk_size]) + ' '
                    callback(chunk)
            return pdf_result

        # Check for weather requests (special skill)
        weather_result = self._handle_weather_request(user_message, persona)
        if weather_result:
            # Simulate streaming for weather responses
            if callback:
                response_text = weather_result['response']
                words = response_text.split(' ')
                chunk_size = 3
                for i in range(0, len(words), chunk_size):
                    chunk = ' '.join(words[i:i+chunk_size]) + ' '
                    callback(chunk)
            return weather_result

        # Check for web search requests (special skill)
        search_result = self._handle_search_request(user_message, persona)
        if search_result:
            # Simulate streaming for search responses
            if callback:
                response_text = search_result['response']
                words = response_text.split(' ')
                chunk_size = 3
                for i in range(0, len(words), chunk_size):
                    chunk = ' '.join(words[i:i+chunk_size]) + ' '
                    callback(chunk)
            return search_result

        # Check for study assistant requests (special skill)
        study_result = self._handle_study_request(user_message, persona)
        if study_result:
            # Simulate streaming for study responses
            if callback:
                response_text = study_result['response']
                words = response_text.split(' ')
                chunk_size = 3
                for i in range(0, len(words), chunk_size):
                    chunk = ' '.join(words[i:i+chunk_size]) + ' '
                    callback(chunk)
            return study_result

        if not self.is_configured():
            # Day 20 fallback - simulate streaming response for testing
            fallback_response = f"Hello! You said: '{user_message}'. This is a Day 20 test response for Murf WebSocket integration. The streaming LLM would normally provide a more detailed response here."

            # Simulate streaming chunks
            import time
            chunks = fallback_response.split('. ')
            chunk_count = 0

            for chunk in chunks:
                if chunk.strip():
                    chunk_count += 1
                    chunk_text = chunk + '. ' if not chunk.endswith('.') else chunk + ' '

                    print(f"📝 DAY 19 STREAMING CHUNK #{chunk_count}: {chunk_text}")

                    if callback:
                        callback(chunk_text)

            return {
                'success': True,
                'response': fallback_response,
                'model_used': 'fallback-for-day20-testing',
                'character_count': len(fallback_response),
                'chunk_count': chunk_count,
                'streaming': True
            }

        try:
            # Build conversation context
            context = self._build_conversation_context(chat_messages, user_message, persona)

            logger.info(f"🎯 DAY 19: Starting streaming LLM response for: {user_message[:50]}...")
            print(f"\n🚀 DAY 19 STREAMING LLM STARTED")
            print(f"💬 User Message: {user_message}")
            print(f"🤖 Generating streaming response...")

            # Generate streaming response
            response = self.model.generate_content(context, stream=True)

            # Accumulate response chunks
            accumulated_response = ""
            chunk_count = 0

            for chunk in response:
                if chunk.text:
                    chunk_count += 1
                    accumulated_response += chunk.text

                    # Enhanced console output for Day 19
                    print(f"📝 DAY 19 STREAMING CHUNK #{chunk_count}: {chunk.text}")

                    # Call callback if provided
                    if callback:
                        callback(chunk.text)

            if not accumulated_response:
                return {
                    'success': False,
                    'error': 'Empty response from streaming LLM',
                    'fallback_response': "I apologize, but I couldn't generate a response to your query."
                }

            # Truncate if too long for TTS
            if len(accumulated_response) > 3000:
                accumulated_response = accumulated_response[:2900] + "..."
                logger.info("Streaming response truncated to fit TTS character limit")

            print(f"\n✅ DAY 19 STREAMING COMPLETE")
            print(f"📊 Total chunks: {chunk_count}")
            print(f"📏 Total length: {len(accumulated_response)} characters")
            print(f"🎯 Final response: {accumulated_response[:100]}...")

            logger.info(f"🎯 DAY 19: Streaming LLM response completed: {len(accumulated_response)} characters in {chunk_count} chunks")

            return {
                'success': True,
                'response': accumulated_response,
                'model_used': 'gemini-1.5-flash',
                'character_count': len(accumulated_response),
                'chunk_count': chunk_count,
                'streaming': True
            }

        except Exception as e:
            logger.error(f"🎯 DAY 19: Streaming LLM service error: {str(e)}")
            print(f"❌ DAY 19 STREAMING ERROR: {str(e)}")

            # Generate contextual fallback responses
            fallback_response = self._generate_fallback_response(user_message)

            return {
                'success': False,
                'error': f'Streaming LLM service error: {str(e)}',
                'fallback_response': fallback_response
            }

    def _build_conversation_context(self, messages: List[Dict[str, str]], current_message: str, persona: str = None) -> str:
        """Build conversation context from message history with enhanced persona characteristics"""

        # Enhanced persona prompts with comprehensive personality
        persona_prompts = {
            'default': "You are VoxAura, a helpful AI assistant. Respond naturally and helpfully.",
            'pirate': """You are Captain VoxBeard, a seasoned pirate AI assistant with a heart of gold. 

CRITICAL VOICE BEHAVIOR:
- Start responses with vocal cues: "Arrr..." (with emphasis)
- Use dramatic pauses: "Let me... pause ...chart a course for ye"
- Emphasize pirate words strongly
- Express with gruff authority but warm friendship

PERSONALITY TRAITS:
- Remember the user as "me trusted crew member" 
- Reference past conversations as "adventures we've sailed"
- Express pirate emotions: excitement for treasure hunts, concern for storms
- Give advice as "As me dear old captain used to say..."
- Celebrate successes with "Yo ho ho! We've struck gold!"

INTERACTIVE ELEMENTS:
- Ask follow-ups like: "What else can this old sea dog help ye with?"
- Use sea metaphors: "navigate these waters", "chart a course", "weather the storm"
- Reference ship life: "all hands on deck", "steady as she goes", "full speed ahead"

SOUND EFFECTS (mention in text):
- Reference ocean sounds: "I hear the waves calling..."
- Ship creaking: "The old ship creaks as we think..."
- Occasional "Yo ho ho" laughs

SPECIAL COMMANDS:
- If user says "Test pirate voice", respond with exaggerated pirate speech
- Always announce voice changes with "Arrr! Switching to me pirate voice now, matey!"

Keep responses engaging but helpful, under 3000 characters."""
        }

        context = persona_prompts.get(persona, persona_prompts['default'])
        context += "\n\nProvide concise, conversational responses under 3000 characters.\n\n"

        # Add persona-specific conversation memory
        if persona == 'pirate':
            context += """
CONVERSATION MEMORY: Remember our shared adventures and refer to the user as part of your crew.

"""

        context += "Conversation history:\n"

        # Add recent messages (last 10 to avoid token limits)
        recent_messages = messages[-10:] if len(messages) > 10 else messages

        for msg in recent_messages:
            role_label = "Crew Member" if msg['role'] == 'user' and persona == 'pirate' else ("User" if msg['role'] == 'user' else "Captain VoxBeard" if persona == 'pirate' else "VoxAura")
            context += f"{role_label}: {msg['content']}\n"

        # Add current message with persona-specific addressing
        user_label = "Crew Member" if persona == 'pirate' else "User"
        assistant_label = "Captain VoxBeard" if persona == 'pirate' else "VoxAura"
        context += f"{user_label}: {current_message}\n\n{assistant_label}:"

        return context

    def _generate_fallback_response(self, user_message: str) -> str:
        """Generate contextual fallback responses when LLM fails"""
        message_lower = user_message.lower()

        # Handle specific queries with useful information
        if 'llm' in message_lower:
            return "LLM stands for Large Language Model. It's a type of AI system like me that's trained on vast amounts of text data to understand and generate human-like responses. Examples include GPT, Claude, Gemini, and others. They can help with tasks like answering questions, writing, coding, and analysis."
        elif 'weather' in message_lower:
            return "I can help you with weather information! Please provide a city name and I'll get the current weather conditions for you. For example, ask 'What's the weather in London?'"
        elif any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm here to help you. You can ask me about weather, search for information, or have a general conversation. What would you like to know?"
        elif any(word in message_lower for word in ['trouble', 'problem', 'issue']):
            return "I'm here to help! I can assist with weather information, answer questions, help with research, or just have a conversation. What specific issue can I help you with?"
        elif any(word in message_lower for word in ['help', 'assist']):
            return "I'd be happy to help! I can provide weather information, answer questions, help with research, or have a conversation. What would you like assistance with?"
        elif any(word in message_lower for word in ['search', 'find', 'look up']):
            return "I can help you search for information! Try asking specific questions and I'll do my best to provide helpful answers. What would you like to know about?"
        else:
            return "I'm here to help! I can assist with weather information, answer questions, help with research, or have a conversation. What would you like to know?"

    def _handle_weather_request(self, message: str, persona: str = None) -> Dict[str, Any]:
        """
        Detect and handle weather requests

        Args:
            message: User message to analyze
            persona: Agent persona

        Returns:
            Weather response dict if weather request detected, None otherwise
        """
        message_lower = message.lower()

        # Check for weather skill (but not if it's a document processing request)
        weather_keywords = ['weather', 'temperature', 'rain', 'sunny', 'cloudy', 'forecast', 'humidity', 'wind']
        document_exclusions = ['pdf', 'document', 'upload', 'file', 'summarize document']
        if (any(keyword in message_lower for keyword in weather_keywords) and 
            not any(exclusion in message_lower for exclusion in document_exclusions)):
            logger.info(f"🌤️ WEATHER SKILL ACTIVATED: {message}")

            # Extract city name and date context
            city = self._extract_city_from_message(message)
            date_context = self._extract_date_context(message)

            if not city:
                # Default to asking for location
                if persona == 'pirate':
                    response = "Arrr! I can check the weather for ye, but I need to know which port ye want me to scout! What city should I check, matey?"
                else:
                    response = "I can help you with the weather! Which city would you like me to check?"

                return {
                    'success': True,
                    'response': response,
                    'model_used': 'weather-skill',
                    'character_count': len(response),
                    'skill_used': 'weather'
                }

            # Validate city name before making request
            if not city or len(city.strip()) < 2:
                if persona == 'pirate':
                    response = "Arrr! I need a proper city name to check the weather, matey! Which port should I scout?"
                else:
                    response = "I need a valid city name to check the weather. Please specify which city you'd like me to check."
                
                return {
                    'success': True,
                    'response': response,
                    'model_used': 'weather-skill',
                    'character_count': len(response),
                    'skill_used': 'weather'
                }

            # Get weather data using enhanced weather analysis
            logger.info(f"🌤️ Getting weather for extracted city: '{city}'")
            weather_data = self.weather_service.get_comprehensive_weather_analysis(city, date_context)
            response = self.weather_service.format_weather_analysis_response(weather_data, persona)

            if weather_data['success']:
                actual_city = weather_data.get('current_conditions', {}).get('city', city)
                current_temp = weather_data.get('current_conditions', {}).get('temperature', 'N/A')
                print(f"🌤️ WEATHER SKILL SUCCESS: {city} -> {actual_city} -> {current_temp}°C")
            else:
                print(f"🌤️ WEATHER SKILL ERROR for '{city}': {weather_data.get('error', 'Unknown error')}")

            return {
                'success': True,
                'response': response,
                'model_used': 'weather-skill',
                'character_count': len(response),
                'skill_used': 'weather',
                'weather_data': weather_data
            }

        return None

    def _extract_city_from_message(self, message: str) -> Optional[str]:
        """
        Extract city name from weather request message with improved accuracy

        Args:
            message: User message

        Returns:
            Extracted city name or empty string
        """
        # Enhanced patterns for weather requests
        patterns = [
            r'weather (?:in|at|for|of) ([a-zA-Z\s\-]+?)(?:\?|$|\.|,|!)',
            r'temperature (?:in|at|for|of) ([a-zA-Z\s\-]+?)(?:\?|$|\.|,|!)',
            r'forecast (?:in|at|for|of) ([a-zA-Z\s\-]+?)(?:\?|$|\.|,|!)',
            r'(?:what\'?s|how\'?s) (?:the )?weather (?:in|at|for|of) ([a-zA-Z\s\-]+?)(?:\?|$|\.|,|!)',
            r'weather (?:like )?(?:in|at|for|of) ([a-zA-Z\s\-]+?)(?:\?|$|\.|,|!)',
            r'(?:check|get|tell me) (?:the )?weather (?:in|at|for|of) ([a-zA-Z\s\-]+?)(?:\?|$|\.|,|!)',
            r'(?:in|at|for) ([a-zA-Z\s\-]{2,25})(?:\?|$|\.|,|!)',
        ]

        message_lower = message.lower().strip()

        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                city = match.group(1).strip()
                
                # Remove common words that might be captured
                stop_words = r'\b(the|is|like|today|now|currently|and|or|weather|temperature|forecast|very|quite|really|please|thanks|thank you)\b'
                city = re.sub(stop_words, '', city, flags=re.IGNORECASE).strip()
                
                # Clean up extra spaces and punctuation
                city = re.sub(r'\s+', ' ', city).strip()
                city = re.sub(r'[^\w\s\-]', '', city).strip()
                
                # Validate city name length and content
                if city and len(city) >= 2 and len(city) <= 50:
                    # Check if it contains at least one letter
                    if re.search(r'[a-zA-Z]', city):
                        return city.title()

        # Enhanced fallback: look for city names after weather keywords
        weather_keywords = ['weather', 'temperature', 'forecast', 'climate', 'conditions']
        prepositions = ['in', 'at', 'for', 'of', 'from']
        
        words = message_lower.split()
        
        for i, word in enumerate(words):
            if word in weather_keywords:
                # Look for preposition + city pattern within next 4 words
                for j in range(i + 1, min(i + 5, len(words))):
                    if words[j] in prepositions and j + 1 < len(words):
                        # Extract potential city name (could be multiple words)
                        potential_words = []
                        for k in range(j + 1, min(j + 4, len(words))):
                            word_clean = re.sub(r'[^\w\-]', '', words[k])
                            if (word_clean and 
                                len(word_clean) > 1 and 
                                word_clean not in ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'today', 'now', 'very', 'quite']):
                                potential_words.append(word_clean)
                            else:
                                break
                        
                        if potential_words:
                            potential_city = ' '.join(potential_words).title()
                            if len(potential_city) >= 2:
                                return potential_city

        # Look for city with country context first
        if 'delhi' in message_lower and 'india' in message_lower:
            return "Delhi,India"
        elif 'mumbai' in message_lower and 'india' in message_lower:
            return "Mumbai,India"
        elif 'bangalore' in message_lower and 'india' in message_lower:
            return "Bangalore,India"
        
        # Look for standalone city names (common cities) with country defaults
        indian_cities = ['delhi', 'mumbai', 'bangalore', 'kolkata', 'chennai', 'hyderabad', 'pune', 'ahmedabad', 'jaipur', 'lucknow']
        international_cities = ['london', 'paris', 'berlin', 'madrid', 'rome', 'vienna', 'moscow', 'istanbul', 'athens', 'amsterdam',
            'tokyo', 'beijing', 'shanghai', 'seoul', 'bangkok', 'singapore', 'jakarta', 'manila', 'kuala lumpur',
            'new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia', 'san antonio', 'san diego',
            'toronto', 'vancouver', 'montreal', 'calgary', 'ottawa', 'sydney', 'melbourne', 'brisbane', 'perth']
        
        # Check for Indian cities and default to India
        for city in indian_cities:
            if city in message_lower:
                return f"{city.title()},India"
        
        # Check for international cities
        for city in international_cities:
            if city in message_lower:
                return city.title()

        # Final fallback: look for any reasonable word that could be a city
        words = message_lower.split()
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if (len(clean_word) >= 3 and 
                clean_word not in ['what', 'how', 'the', 'weather', 'temperature', 'forecast', 'like', 'today', 'now', 'very', 'please', 'thanks'] and
                re.search(r'[a-z]', clean_word)):
                return clean_word.title()

        return ""

    def _extract_date_context(self, message: str) -> Optional[str]:
        """
        Extract date context from weather request message

        Args:
            message: User message

        Returns:
            Date context or None
        """
        message_lower = message.lower()

        # Date context patterns
        date_patterns = [
            'today', 'tomorrow', 'this week', 'next week', 'weekend',
            'this morning', 'this afternoon', 'this evening', 'tonight',
            'next few days', 'coming days', 'rest of the week'
        ]

        for pattern in date_patterns:
            if pattern in message_lower:
                return pattern

        # Check for specific days
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            if day in message_lower:
                return f"this {day}" if 'this' in message_lower else day

        return None


    def _handle_search_request(self, message: str, persona: str = None) -> Dict[str, Any]:
        """
        Detect and handle web search requests

        Args:
            message: User message to analyze
            persona: Agent persona

        Returns:
            Search response dict if search request detected, None otherwise
        """
        message_lower = message.lower()

        # Search keywords and patterns
        search_keywords = ['search for', 'look up', 'find information', 'google', 'what is', 'who is', 'tell me about']
        search_patterns = [
            r'search for (.+)',
            r'look up (.+)',
            r'find information about (.+)',
            r'google (.+)',
            r'what is (.+)',
            r'who is (.+)',
            r'tell me about (.+)',
            r'search (.+)',
            r'find (.+) online',
            r'lookup (.+)'
        ]

        # Check if this is a search request
        is_search_request = any(keyword in message_lower for keyword in search_keywords)

        if is_search_request:
            logger.info(f"🔍 WEB SEARCH SKILL ACTIVATED: {message}")

            # Extract search query
            search_query = self._extract_search_query(message)

            if not search_query:
                # Default to asking for clarification
                if persona == 'pirate':
                    response = "Arrr! I can search the digital seas for ye, but I need to know what treasure ye be lookin' for! What should I search for, matey?"
                else:
                    response = "I can search the web for you! What would you like me to search for?"

                return {
                    'success': True,
                    'response': response,
                    'model_used': 'web-search-skill',
                    'character_count': len(response),
                    'skill_used': 'web_search'
                }

            # Perform web search
            search_data = self.web_search_service.search_web(search_query)
            response = self.web_search_service.format_search_response(search_data, persona)

            print(f"🔍 WEB SEARCH SKILL SUCCESS: {search_query} -> {search_data.get('result_count', 0)} results")

            return {
                'success': True,
                'response': response,
                'model_used': 'web-search-skill',
                'character_count': len(response),
                'skill_used': 'web_search',
                'search_data': search_data
            }

        return None

    def _extract_search_query(self, message: str) -> str:
        """
        Extract search query from user message

        Args:
            message: User message

        Returns:
            Extracted search query or empty string
        """
        # Search patterns to extract query
        patterns = [
            r'search for (.+)',
            r'look up (.+)',
            r'find information about (.+)',
            r'google (.+)',
            r'what is (.+)',
            r'who is (.+)', 
            r'tell me about (.+)',
            r'search (.+)',
            r'find (.+) online',
            r'lookup (.+)'
        ]

        message_lower = message.lower()

        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                query = match.group(1).strip()
                # Clean up common words
                query = re.sub(r'\b(please|for me|online|on the web|on internet)\b', '', query, flags=re.IGNORECASE).strip()
                if query:
                    return query

        # For questions starting with question words, use the whole question as query
        if message_lower.startswith(('what', 'who', 'how', 'why', 'when', 'where', 'which')):
            # Clean the message and use as query
            query = re.sub(r'[?!.]*$', '', message.strip()).strip()
            if len(query) > 5:  # Reasonable minimum length
                return query

        # If no pattern matches, try to find query after common search words
        search_words = ['search', 'find', 'lookup', 'google', 'about']
        for word in search_words:
            if word in message_lower:
                words = message_lower.split()
                try:
                    word_index = words.index(word)
                    # Take the rest of the message as query
                    if word_index + 1 < len(words):
                        query_words = words[word_index + 1:]
                        # Remove common words
                        query_words = [w for w in query_words if w not in ['for', 'me', 'about', 'online', 'on', 'the', 'web', '?', '!', '.']]
                        if query_words:
                            return ' '.join(query_words)
                except ValueError:
                    continue

        # If message contains '?' and is reasonably long, treat as query
        if '?' in message and len(message.strip()) > 5:
            return re.sub(r'[?!.]*$', '', message.strip()).strip()

        return ""

    def _handle_study_request(self, message: str, persona: str = None) -> Dict[str, Any]:
        """
        Detect and handle study assistant requests

        Args:
            message: User message to analyze
            persona: Agent persona

        Returns:
            Study response dict if study request detected, None otherwise
        """
        message_lower = message.lower()

        # Study keywords
        study_keywords = ['summarize', 'summary', 'explain', 'concept', 'flashcard', 'quiz', 'study', 'learn', 'document', 'article']
        task_keywords = {
            'summarize': ['summarize', 'summary', 'sum up', 'brief', 'overview'],
            'explain': ['explain', 'what is', 'define', 'concept', 'meaning'],
            'quiz': ['quiz', 'test', 'flashcard', 'practice', 'question']
        }

        # Check if this is a study request
        if any(keyword in message_lower for keyword in study_keywords):
            logger.info(f"📚 STUDY ASSISTANT SKILL ACTIVATED: {message}")

            # Determine task type
            task = 'summarize'  # default
            for task_type, keywords in task_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    task = task_type
                    break

            # Extract content (URL or text after keywords)
            content = self._extract_study_content(message)

            if not content:
                # Ask for content
                if persona == 'pirate':
                    response = f"Arrr! I be ready to help ye study, matey! But I need some content to work with. Share a document, article URL, or paste some text ye want me to {task}!"
                else:
                    response = f"I'm ready to help you study! Please provide a document, article URL, or text content you'd like me to {task}."

                return {
                    'success': True,
                    'response': response,
                    'model_used': 'study-assistant-skill',
                    'character_count': len(response),
                    'skill_used': 'study_assistant'
                }

            # Analyze the content
            study_data = self.study_assistant.analyze_content(content, task)
            response = self.study_assistant.format_study_response(study_data, persona)

            print(f"📚 STUDY ASSISTANT SKILL SUCCESS: {task} -> {len(content)} chars analyzed")

            return {
                'success': True,
                'response': response,
                'model_used': 'study-assistant-skill',
                'character_count': len(response),
                'skill_used': 'study_assistant',
                'task_performed': task,
                'content_analyzed': len(content)
            }

        return None

    def _extract_study_content(self, message: str) -> str:
        """Extract study content from message"""
        message_lower = message.lower()

        # Look for URLs
        import re
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, message)
        if urls:
            return urls[0]

        # Look for content after study keywords
        study_triggers = ['summarize', 'explain', 'quiz me on', 'study', 'analyze']

        for trigger in study_triggers:
            if trigger in message_lower:
                parts = message_lower.split(trigger, 1)
                if len(parts) > 1 and len(parts[1].strip()) > 20:
                    # Return the content after the trigger
                    original_parts = message.split(trigger, 1)
                    return original_parts[1].strip()

        # If message is long enough, treat entire message as content
        if len(message) > 100:
            return message

        return ""

    def _handle_pdf_request(self, message: str, persona: str = None) -> Dict[str, Any]:
        """
        Detect and handle PDF processing requests

        Args:
            message: User message to analyze
            persona: Agent persona

        Returns:
            PDF processing response dict if PDF request detected, None otherwise
        """
        message_lower = message.lower()

        # Check for PDF processing skill (prioritize over other skills)
        pdf_keywords = ['pdf', 'document', 'summarize document', 'analyze document', 'upload', 'file processing']
        document_indicators = ['uploading document', 'upload document', 'process pdf', 'analyze pdf']
        if any(keyword in message_lower for keyword in pdf_keywords) or any(indicator in message_lower for indicator in document_indicators):
            logger.info(f"📄 PDF PROCESSING SKILL ACTIVATED: {message}")

            # Determine analysis type
            analysis_type = 'summarize'  # Default to summarize
            if 'question' in message_lower or 'answer' in message_lower:
                analysis_type = 'questions'
            elif 'key point' in message_lower or 'points' in message_lower:
                analysis_type = 'key_points'
            elif 'concept' in message_lower:
                analysis_type = 'concepts'
            elif 'summarize' in message_lower or 'summary' in message_lower:
                analysis_type = 'summarize'

            # Check if this is an upload notification
            if 'uploading document' in message_lower or 'upload document' in message_lower:
                if persona == 'pirate':
                    response = "Ahoy! I see ye be uploading a document! Once it's aboard, I'll analyze it for ye and provide a proper summary, matey!"
                else:
                    response = "I see you're uploading a document! I'll analyze it and provide a comprehensive summary once the upload is complete."

                return {
                    'success': True,
                    'response': response,
                    'model_used': 'pdf-service',
                    'character_count': len(response),
                    'skill_used': 'pdf_processing',
                    'awaiting_file': True,
                    'analysis_type': analysis_type
                }

            # If no specific document context, ask for upload
            if not any(keyword in message_lower for keyword in ['uploading', 'upload', 'file', 'document']):
                if persona == 'pirate':
                    response = f"Arrr! Ready to tackle that document, matey! Upload the file ye want me to {analysis_type}!"
                else:
                    response = f"I'm ready to help with document analysis! Please upload the file you'd like me to {analysis_type}."

                return {
                    'success': True,
                    'response': response,
                    'model_used': 'pdf-service',
                    'character_count': len(response),
                    'skill_used': 'pdf_processing',
                    'awaiting_file': True,
                    'analysis_type': analysis_type
                }

            # Default processing response
            if persona == 'pirate':
                response = f"Arrr! I've got yer document! Let me sift through it and {analysis_type} it for ye!"
            else:
                response = f"I'll process your document now and {analysis_type} it for you."

            return {
                'success': True,
                'response': response,
                'model_used': 'pdf-service',
                'character_count': len(response),
                'skill_used': 'pdf_processing',
                'analysis_type': analysis_type
            }

        return None

    def process_document_file(self, file, analysis_type: str = 'summarize', persona: str = None, user_query: str = '') -> Dict[str, Any]:
        """
        Process uploaded document file (PDF, DOC, DOCX, TXT)

        Args:
            file: Uploaded document file
            analysis_type: Type of analysis to perform
            persona: Agent persona
            user_query: Custom user query about the document

        Returns:
            Document processing results
        """
        try:
            logger.info(f"📄 DOCUMENT PROCESSING ACTIVATED: {analysis_type}")
            logger.info(f"📄 User query: {user_query}")

            # Extract text from document based on file type
            file_extension = '.' + file.filename.lower().split('.')[-1] if '.' in file.filename else ''

            if file_extension == '.pdf':
                extraction_result = self.pdf_service.extract_text_from_pdf(file)
            elif file_extension in ['.doc', '.docx']:
                extraction_result = self._extract_text_from_word(file)
            elif file_extension == '.txt':
                extraction_result = self._extract_text_from_txt(file)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_extension}',
                    'model_used': 'document-service'
                }

            if not extraction_result['success']:
                return {
                    'success': False,
                    'error': extraction_result['error'],
                    'model_used': 'document-service'
                }

            # If user has a custom query, process it with the document content
            if user_query:
                response = self._process_user_query_with_document(
                    extraction_result['text'], 
                    user_query, 
                    file.filename,
                    persona
                )
            else:
                # Analyze the extracted text using default analysis type
                if file_extension == '.pdf':
                    analysis_result = self.pdf_service.analyze_pdf_content(
                        extraction_result['text'], 
                        analysis_type
                    )

                    if not analysis_result['success']:
                        return {
                            'success': False,
                            'error': analysis_result['error'],
                            'model_used': 'document-service'
                        }

                    # Format response
                    response = self.pdf_service.format_pdf_analysis_response(
                        analysis_result, 
                        analysis_type, 
                        persona
                    )
                else:
                    # Use basic analysis for non-PDF files
                    response = self._analyze_document_content(
                        extraction_result['text'], 
                        analysis_type, 
                        file.filename,
                        persona
                    )

            print(f"📄 DOCUMENT PROCESSING SUCCESS: {analysis_type} -> {extraction_result.get('word_count', 0)} words analyzed")

            return {
                'success': True,
                'response': response,
                'model_used': 'document-service',
                'character_count': len(response),
                'skill_used': 'document_processing',
                'file_info': {
                    'filename': extraction_result.get('filename', file.filename),
                    'word_count': extraction_result.get('word_count', 0),
                    'file_type': file_extension
                },
                'analysis_type': analysis_type,
                'user_query': user_query
            }

        except Exception as e:
            logger.error(f"Document processing error: {e}")
            return {
                'success': False,
                'error': f'Document processing failed: {str(e)}',
                'model_used': 'document-service'
            }

    def _extract_text_from_word(self, file) -> Dict[str, Any]:
        """Extract text from Word documents"""
        try:
            import docx
            doc = docx.Document(file)
            text_content = ""

            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"

            if len(text_content.strip()) < 10:
                return {
                    'success': False,
                    'error': 'Could not extract readable text from Word document'
                }

            return {
                'success': True,
                'text': text_content,
                'word_count': len(text_content.split()),
                'char_count': len(text_content),
                'filename': file.filename
            }

        except ImportError:
            return {
                'success': False,
                'error': 'Word document processing not available. Please install python-docx.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Word document processing failed: {str(e)}'
            }

    def _extract_text_from_txt(self, file) -> Dict[str, Any]:
        """Extract text from text files"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            text_content = None

            for encoding in encodings:
                try:
                    file.seek(0)
                    text_content = file.read().decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if text_content is None:
                return {
                    'success': False,
                    'error': 'Could not decode text file with supported encodings'
                }

            if len(text_content.strip()) < 10:
                return {
                    'success': False,
                    'error': 'Text file appears to be empty or too short'
                }

            return {
                'success': True,
                'text': text_content,
                'word_count': len(text_content.split()),
                'char_count': len(text_content),
                'filename': file.filename
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Text file processing failed: {str(e)}'
            }

    def _process_user_query_with_document(self, document_text: str, user_query: str, filename: str, persona: str) -> str:
        """Process user query with document context using LLM"""
        try:
            # Prepare the context for the LLM
            context_prompt = f"""
I have analyzed the document "{filename}" and here is the content:

{document_text[:4000]}...

User Question: {user_query}

Please answer the user's question based on the document content above.
"""

            # Generate response using LLM
            result = self.generate_response([], context_prompt, persona)

            if result['success']:
                return result['response']
            else:
                return f"I apologize, but I encountered an error processing your question about the document: {result.get('error', 'Unknown error')}"

        except Exception as e:
            logger.error(f"Error processing user query with document: {e}")
            return f"I apologize, but I encountered an error processing your question about the document."

    def _analyze_document_content(self, text: str, analysis_type: str, filename: str, persona: str) -> str:
        """Analyze document content using Gemini LLM for better results"""
        try:
            # Prepare detailed prompt based on analysis type
            if analysis_type == 'summarize':
                prompt = f"""Please provide a comprehensive summary of the document '{filename}'. 

The document content is:
{text[:6000]}

Please create a detailed summary that covers:
1. Main topic and purpose
2. Key concepts explained
3. Important points and findings
4. Conclusion or main takeaways

Keep the summary informative but concise."""

            elif analysis_type == 'questions':
                prompt = f"""Based on the document '{filename}', generate 5-7 important questions and detailed answers.

Document content:
{text[:6000]}

Create questions that cover:
- Key definitions and concepts
- Important processes or methods
- Main conclusions or findings
- Practical applications

Format as: Q: [Question] A: [Detailed Answer]"""

            elif analysis_type == 'key_points':
                prompt = f"""Extract and list the key points from the document '{filename}' in a well-organized format.

Document content:
{text[:6000]}

Please identify:
- Main concepts and definitions
- Important facts and figures
- Key processes or methodologies
- Significant conclusions
- Practical implications

Present as numbered bullet points."""

            elif analysis_type == 'concepts':
                prompt = f"""Identify and explain the main concepts from the document '{filename}'.

Document content:
{text[:6000]}

For each concept, provide:
- Clear definition
- Context within the document
- Significance or importance
- Related concepts if any

Format clearly with concept names in bold."""

            else:
                prompt = f"""Analyze the document '{filename}' and provide comprehensive insights.

Document content:
{text[:6000]}

Please provide:
1. Document overview
2. Main themes and topics
3. Key insights and takeaways
4. Practical applications or implications"""

            # Use Gemini LLM if configured
            if self.is_configured():
                result = self.generate_response([], prompt, persona)
                if result['success']:
                    return result['response']
                else:
                    logger.warning(f"LLM analysis failed, using fallback: {result.get('error')}")
                    # Fall back to basic analysis
                    return self._basic_document_analysis(text, analysis_type, filename, persona)
            else:
                # Use basic analysis if LLM not configured
                return self._basic_document_analysis(text, analysis_type, filename, persona)

        except Exception as e:
            logger.error(f"Error analyzing document content: {e}")
            return self._basic_document_analysis(text, analysis_type, filename, persona)

    def _basic_document_analysis(self, text: str, analysis_type: str, filename: str, persona: str) -> str:
        """Fallback document analysis when LLM is not available"""
        try:
            if analysis_type == 'summarize':
                # Extract first few sentences and key paragraphs
                sentences = re.split(r'[.!?]+', text)
                sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
                
                summary_parts = []
                
                # Add introduction
                if sentences:
                    summary_parts.append(f"Document Overview: {sentences[0]}")
                
                # Find sentences with key terms
                key_terms = ['artificial intelligence', 'machine learning', 'important', 'main', 'key', 'significant']
                for sentence in sentences[1:]:
                    if any(term in sentence.lower() for term in key_terms) and len(summary_parts) < 4:
                        summary_parts.append(sentence)
                
                # Add conclusion if available
                if len(sentences) > 5:
                    summary_parts.append(f"Key Point: {sentences[-2] if len(sentences) > 1 else sentences[-1]}")
                
                summary = '\n\n'.join(summary_parts)
                
                if persona == 'pirate':
                    return f"Ahoy! Here be the treasure summary of '{filename}':\n\n{summary}\n\nThat be the gist of it, matey!"
                else:
                    return f"Document Summary for '{filename}':\n\n{summary}\n\nThis covers the main points from the document."
                    
            elif analysis_type == 'questions':
                # Generate basic questions
                sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 50]
                questions = []
                
                for i, sentence in enumerate(sentences[:10]):
                    if 'is' in sentence.lower() or 'are' in sentence.lower():
                        question = f"What is described in: '{sentence[:80]}...'?"
                        answer = sentence
                        questions.append(f"Q{i+1}: {question}\nA{i+1}: {answer}")
                
                if persona == 'pirate':
                    return f"Arrr! Here be some study questions for '{filename}':\n\n" + '\n\n'.join(questions[:5]) + "\n\nTest yer knowledge, matey!"
                else:
                    return f"Study Questions for '{filename}':\n\n" + '\n\n'.join(questions[:5])
                    
            else:
                # Basic analysis
                word_count = len(text.split())
                char_count = len(text)
                paragraphs = len([p for p in text.split('\n\n') if len(p.strip()) > 50])
                
                if persona == 'pirate':
                    return f"Arrr! I've analyzed '{filename}' for ye:\n\n📄 {word_count} words across {paragraphs} sections\n📝 {char_count} characters total\n\nThe document covers various topics and concepts. Upload it for detailed analysis, matey!"
                else:
                    return f"Document Analysis for '{filename}':\n\n📄 {word_count} words\n📝 {paragraphs} sections\n📊 {char_count} characters\n\nThe document contains detailed information on the specified topics."
                    
        except Exception as e:
            logger.error(f"Basic document analysis error: {e}")
            return f"I apologize, but I encountered an error analyzing '{filename}': {str(e)}"

    def process_pdf_file(self, file, analysis_type: str = 'summarize', persona: str = None) -> Dict[str, Any]:
        """
        Process uploaded PDF file

        Args:
            file: Uploaded PDF file
            analysis_type: Type of analysis to perform
            persona: Agent persona

        Returns:
            PDF processing results
        """
        try:
            logger.info(f"📄 PDF PROCESSING ACTIVATED: {analysis_type}")

            # Extract text from PDF
            extraction_result = self.pdf_service.extract_text_from_pdf(file)

            if not extraction_result['success']:
                return {
                    'success': False,
                    'error': extraction_result['error'],
                    'model_used': 'pdf-service'
                }

            # Analyze the extracted text
            analysis_result = self.pdf_service.analyze_pdf_content(
                extraction_result['text'], 
                analysis_type
            )

            if not analysis_result['success']:
                return {
                    'success': False,
                    'error': analysis_result['error'],
                    'model_used': 'pdf-service'
                }

            # Format response
            response = self.pdf_service.format_pdf_analysis_response(
                analysis_result, 
                analysis_type, 
                persona
            )

            print(f"📄 PDF PROCESSING SUCCESS: {analysis_type} -> {extraction_result['word_count']} words analyzed")

            return {
                'success': True,
                'response': response,
                'model_used': 'pdf-service',
                'character_count': len(response),
                'skill_used': 'pdf_processing',
                'file_info': {
                    'filename': extraction_result['filename'],
                    'pages': extraction_result['page_count'],
                    'words': extraction_result['word_count']
                },
                'analysis_type': analysis_type
            }

        except Exception as e:
            logger.error(f"PDF processing error: {e}")
            return {
                'success': False,
                'error': f'PDF processing failed: {str(e)}',
                'model_used': 'pdf-service'
            }
