
"""
Study/Work Assistant Service - Special Skill for VoxAura Agent
Provides document summarization, concept explanation, and quiz generation
"""
import os
import logging
import requests
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import html2text

logger = logging.getLogger(__name__)

class StudyAssistantService:
    def __init__(self):
        """Initialize study assistant service"""
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
        logger.info("✅ Study Assistant service initialized")

    def analyze_content(self, content: str, task: str = 'summarize') -> Dict[str, Any]:
        """
        Analyze provided content (text or URL)
        
        Args:
            content: Text content or URL to analyze
            task: Type of analysis ('summarize', 'explain', 'quiz')
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Check if content is a URL
            if self._is_url(content):
                text_content = self._extract_webpage_content(content)
                source_type = 'webpage'
            else:
                text_content = content
                source_type = 'document'

            if not text_content or len(text_content.strip()) < 50:
                return {
                    'success': False,
                    'error': 'Content too short or could not be extracted'
                }

            # Perform the requested task
            if task == 'summarize':
                result = self._summarize_content(text_content)
            elif task == 'explain':
                result = self._explain_concepts(text_content)
            elif task == 'quiz':
                result = self._generate_quiz(text_content)
            else:
                return {
                    'success': False,
                    'error': f'Unknown task: {task}'
                }

            return {
                'success': True,
                'task': task,
                'source_type': source_type,
                'content_length': len(text_content),
                'result': result
            }

        except Exception as e:
            logger.error(f"Study assistant analysis error: {e}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }

    def _is_url(self, content: str) -> bool:
        """Check if content is a URL"""
        try:
            result = urlparse(content.strip())
            return all([result.scheme, result.netloc])
        except:
            return False

    def _extract_webpage_content(self, url: str) -> str:
        """Extract text content from webpage"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                # Convert HTML to text
                text_content = self.html_converter.handle(response.text)
                
                # Clean up the text
                text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
                text_content = text_content.strip()
                
                # Limit content length for processing
                if len(text_content) > 5000:
                    text_content = text_content[:5000] + "..."
                
                return text_content
            else:
                raise Exception(f"Failed to fetch webpage: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Webpage extraction error: {e}")
            raise

    def _summarize_content(self, content: str) -> Dict[str, Any]:
        """Summarize the provided content"""
        # Simple extractive summarization
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Select key sentences (first, middle, important keywords)
        key_sentences = []
        
        # Always include first sentence if meaningful
        if sentences and len(sentences[0]) > 30:
            key_sentences.append(sentences[0])
        
        # Find sentences with important keywords
        important_keywords = ['important', 'key', 'main', 'significant', 'crucial', 'essential', 'therefore', 'conclusion', 'summary']
        
        for sentence in sentences[1:]:
            if any(keyword in sentence.lower() for keyword in important_keywords):
                key_sentences.append(sentence)
                if len(key_sentences) >= 5:
                    break
        
        # Fill remaining slots with middle sentences
        if len(key_sentences) < 3 and len(sentences) > 2:
            middle_start = len(sentences) // 3
            middle_end = 2 * len(sentences) // 3
            key_sentences.extend(sentences[middle_start:middle_end][:3-len(key_sentences)])
        
        # Generate key points
        key_points = self._extract_key_points(content)
        
        summary = '. '.join(key_sentences[:5]) + '.'
        
        return {
            'summary': summary,
            'key_points': key_points[:5],
            'word_count': len(content.split()),
            'summary_ratio': f"{len(summary.split())}/{len(content.split())} words"
        }

    def _explain_concepts(self, content: str) -> Dict[str, Any]:
        """Extract and explain key concepts"""
        # Find potential concepts (capitalized terms, technical terms)
        concepts = []
        
        # Look for capitalized terms that might be concepts
        capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        
        # Look for terms in quotes or parentheses
        quoted_terms = re.findall(r'"([^"]*)"', content)
        parenthetical_terms = re.findall(r'\(([^)]*)\)', content)
        
        all_terms = capitalized_terms + quoted_terms + parenthetical_terms
        
        # Filter and deduplicate
        for term in all_terms:
            if len(term) > 2 and len(term) < 50 and term not in concepts:
                concepts.append(term)
        
        # Generate simple explanations based on context
        explanations = []
        for concept in concepts[:5]:
            context = self._find_context(content, concept)
            explanation = self._generate_simple_explanation(concept, context)
            explanations.append({
                'concept': concept,
                'explanation': explanation,
                'context': context[:200] + '...' if len(context) > 200 else context
            })
        
        return {
            'concepts_found': len(concepts),
            'explanations': explanations,
            'simple_summary': self._generate_simple_summary(content)
        }

    def _generate_quiz(self, content: str) -> Dict[str, Any]:
        """Generate flashcards and quiz questions"""
        # Extract key facts and statements
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        flashcards = []
        quiz_questions = []
        
        # Generate flashcards from key statements
        for sentence in sentences[:10]:
            if any(word in sentence.lower() for word in ['is', 'are', 'was', 'were', 'defined', 'means']):
                parts = re.split(r'\s+(?:is|are|was|were|means|defined as)\s+', sentence, 1)
                if len(parts) == 2:
                    question = f"What is {parts[0].strip()}?"
                    answer = parts[1].strip()
                    flashcards.append({
                        'question': question,
                        'answer': answer
                    })
        
        # Generate multiple choice questions
        important_sentences = [s for s in sentences if len(s) > 50 and any(
            keyword in s.lower() for keyword in ['important', 'key', 'main', 'because', 'therefore', 'result']
        )]
        
        for sentence in important_sentences[:5]:
            # Create fill-in-the-blank style questions
            words = sentence.split()
            if len(words) > 8:
                # Replace a key noun or adjective
                key_word_idx = self._find_key_word_index(words)
                if key_word_idx != -1:
                    correct_answer = words[key_word_idx]
                    question_words = words.copy()
                    question_words[key_word_idx] = "______"
                    
                    quiz_questions.append({
                        'question': ' '.join(question_words),
                        'correct_answer': correct_answer,
                        'type': 'fill_in_blank'
                    })
        
        return {
            'flashcards': flashcards[:8],
            'quiz_questions': quiz_questions[:5],
            'total_cards': len(flashcards),
            'total_questions': len(quiz_questions),
            'study_tips': self._generate_study_tips(content)
        }

    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content"""
        sentences = re.split(r'[.!?]+', content)
        key_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and any(indicator in sentence.lower() for indicator in [
                'first', 'second', 'third', 'finally', 'important', 'key', 'main', 'significant'
            ]):
                key_points.append(sentence)
        
        return key_points

    def _find_context(self, content: str, term: str) -> str:
        """Find context around a term"""
        sentences = content.split('.')
        for sentence in sentences:
            if term.lower() in sentence.lower():
                return sentence.strip()
        return ""

    def _generate_simple_explanation(self, concept: str, context: str) -> str:
        """Generate simple explanation for a concept"""
        if context:
            return f"{concept} refers to the idea mentioned in: '{context[:100]}...'"
        else:
            return f"{concept} is an important concept in this document."

    def _generate_simple_summary(self, content: str) -> str:
        """Generate a very simple summary"""
        sentences = re.split(r'[.!?]+', content)
        if sentences:
            first_sentence = sentences[0].strip()
            return f"This content is about: {first_sentence[:150]}..."
        return "This document contains important information."

    def _find_key_word_index(self, words: List[str]) -> int:
        """Find index of a key word to replace in quiz"""
        # Look for nouns, adjectives, or important terms
        for i, word in enumerate(words):
            if (len(word) > 4 and 
                word.lower() not in ['the', 'and', 'but', 'with', 'have', 'that', 'this', 'they', 'from'] and
                not word.lower() in ['a', 'an', 'in', 'on', 'at', 'to', 'for']):
                return i
        return -1

    def _generate_study_tips(self, content: str) -> List[str]:
        """Generate study tips based on content"""
        tips = [
            "Review the key concepts multiple times",
            "Create your own examples for each concept",
            "Test yourself without looking at the answers",
            "Explain concepts in your own words",
            "Connect new information to what you already know"
        ]
        return tips

    def format_study_response(self, study_data: Dict[str, Any], persona: str = 'default') -> str:
        """
        Format study assistant results into natural language response
        
        Args:
            study_data: Study analysis results
            persona: Agent persona for response style
            
        Returns:
            Formatted study response string
        """
        if not study_data['success']:
            if persona == 'pirate':
                return f"Arrr! {study_data['error']} The scholarly seas be rough today, matey!"
            else:
                return f"I'm sorry, {study_data['error']}"

        task = study_data['task']
        result = study_data['result']
        source_type = study_data['source_type']

        if persona == 'pirate':
            if task == 'summarize':
                response = f"Ahoy! I've sailed through yer {source_type} and here be the treasure I found:\n\n"
                response += f"📜 Summary: {result['summary']}\n\n"
                response += "🗝️ Key Points:\n"
                for i, point in enumerate(result['key_points'], 1):
                    response += f"{i}. {point}\n"
                response += f"\n⚓ This be {result['summary_ratio']} - much easier to digest, me hearty!"
                
            elif task == 'explain':
                response = f"Arrr! Let me explain these concepts from yer {source_type}, matey:\n\n"
                for explanation in result['explanations']:
                    response += f"🏴‍☠️ **{explanation['concept']}**: {explanation['explanation']}\n\n"
                response += f"📚 Simple Summary: {result['simple_summary']}\n"
                response += "Now ye can understand this like a true sea scholar!"
                
            elif task == 'quiz':
                response = f"Shiver me timbers! I've created some study treasures for ye:\n\n"
                response += "🃏 Flashcards:\n"
                for i, card in enumerate(result['flashcards'][:3], 1):
                    response += f"{i}. Q: {card['question']}\n   A: {card['answer']}\n\n"
                response += "🎯 Quiz Questions:\n"
                for i, q in enumerate(result['quiz_questions'][:2], 1):
                    response += f"{i}. {q['question']}\n   Answer: {q['correct_answer']}\n\n"
                response += f"Study like a pirate with {result['total_cards']} flashcards and {result['total_questions']} questions!"
        else:
            if task == 'summarize':
                response = f"I've analyzed your {source_type} and here's what I found:\n\n"
                response += f"📋 Summary: {result['summary']}\n\n"
                response += "📌 Key Points:\n"
                for i, point in enumerate(result['key_points'], 1):
                    response += f"{i}. {point}\n"
                response += f"\n📊 Condensed from {result['summary_ratio']} for easier studying!"
                
            elif task == 'explain':
                response = f"Here are the key concepts I found in your {source_type}:\n\n"
                for explanation in result['explanations']:
                    response += f"💡 **{explanation['concept']}**: {explanation['explanation']}\n\n"
                response += f"📖 In simple terms: {result['simple_summary']}\n"
                response += "These explanations should help clarify the main ideas!"
                
            elif task == 'quiz':
                response = f"I've created study materials from your {source_type}:\n\n"
                response += "📚 Flashcards:\n"
                for i, card in enumerate(result['flashcards'][:3], 1):
                    response += f"{i}. Q: {card['question']}\n   A: {card['answer']}\n\n"
                response += "❓ Practice Questions:\n"
                for i, q in enumerate(result['quiz_questions'][:2], 1):
                    response += f"{i}. {q['question']}\n   Answer: {q['correct_answer']}\n\n"
                response += f"Generated {result['total_cards']} flashcards and {result['total_questions']} questions for your study session!"

        response += "\n\nWould you like me to analyze more content or help with a different study task?"
        return response
