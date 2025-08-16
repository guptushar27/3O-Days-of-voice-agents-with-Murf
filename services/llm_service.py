
"""
Language Model Service
Handles Google Gemini integration for conversational AI
"""
import os
import logging
from typing import Dict, Any, List
from google import genai

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("Gemini API key not configured")
    
    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return bool(self.client)
    
    def generate_response(self, messages: List[Dict[str, str]], current_message: str) -> Dict[str, Any]:
        """
        Generate conversational response using Gemini
        
        Args:
            messages: Chat history
            current_message: Current user message
            
        Returns:
            Dict containing response and metadata
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'LLM service not configured',
                'fallback_response': "I'm having trouble connecting to my AI services right now."
            }
        
        try:
            # Build conversation context
            context = self._build_conversation_context(messages, current_message)
            
            logger.info(f"Generating response for {len(messages)} message(s) in context")
            
            # Generate response
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=context
            )
            
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
                'model_used': 'gemini-2.5-flash',
                'character_count': len(response_text)
            }
            
        except Exception as e:
            logger.error(f"LLM service error: {str(e)}")
            
            # Generate contextual fallback responses
            fallback_response = self._generate_fallback_response(current_message)
            
            return {
                'success': False,
                'error': f'LLM service error: {str(e)}',
                'fallback_response': fallback_response
            }
    
    def _build_conversation_context(self, messages: List[Dict[str, str]], current_message: str) -> str:
        """Build conversation context from message history"""
        context = "You are VoxAura, a helpful AI voice assistant. Provide concise, conversational responses under 3000 characters.\n\nConversation history:\n"
        
        # Add recent messages (last 10 to avoid token limits)
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        
        for msg in recent_messages:
            role_label = "User" if msg['role'] == 'user' else "VoxAura"
            context += f"{role_label}: {msg['content']}\n"
        
        # Add current message
        context += f"User: {current_message}\n\nVoxAura:"
        
        return context
    
    def _generate_fallback_response(self, user_message: str) -> str:
        """Generate contextual fallback responses when LLM fails"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm having some technical difficulties with my AI services right now, but I'm still here to chat with you."
        elif any(word in message_lower for word in ['trouble', 'problem', 'issue']):
            return "I understand you're having some trouble. I'm also experiencing some technical difficulties right now, but I'm here to help as best I can."
        elif any(word in message_lower for word in ['help', 'assist']):
            return "I'd love to help you, but I'm experiencing some connectivity issues with my AI services. Please try again in a moment."
        else:
            return "I'm having trouble connecting to my AI services right now. Please try again in a moment, and I'll do my best to assist you."
