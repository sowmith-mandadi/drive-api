"""AI service for handling interactions with Vertex AI and other language models."""

import os
import json
import logging
import traceback
from typing import List, Dict, Any, Optional, Union
from app.services.embedding_service import EmbeddingService

# Configure settings from environment variables
VERTEX_AI_MODEL = os.environ.get("VERTEX_AI_MODEL", "gemini-pro")
VERTEX_AI_LOCATION = os.environ.get("VERTEX_AI_LOCATION", "us-central1")
USE_VERTEX_AI = os.environ.get("USE_VERTEX_AI", "true").lower() == "true"

# Initialize logger
logger = logging.getLogger(__name__)

class AIService:
    """Service for handling interactions with Vertex AI and other language models."""
    
    def __init__(self):
        """Initialize the AI service."""
        self.embedding_service = EmbeddingService()
        self.model = VERTEX_AI_MODEL
        self.initialized = False
        self.dev_mode = not os.path.exists('credentials.json')
        
        if self.dev_mode:
            logger.warning("Credentials file not found. Running AI service in development mode.")
            return
            
        try:
            if USE_VERTEX_AI:
                # Initialize Vertex AI
                self._init_vertex_ai()
            else:
                # Initialize alternative model (e.g., local models or API)
                self._init_alternative_model()
                
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            logger.error(traceback.format_exc())
            logger.warning("Running AI service in development mode with mock responses")
    
    def _init_vertex_ai(self):
        """Initialize Vertex AI."""
        try:
            from google.cloud import aiplatform
            import vertexai
            
            # Initialize Vertex AI with default project and location
            try:
                # Try to get project ID from environment variable
                project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
                if project_id:
                    vertexai.init(project=project_id, location=VERTEX_AI_LOCATION)
                else:
                    # Try with credentials file
                    aiplatform.init(location=VERTEX_AI_LOCATION)
                    
                logger.info(f"Initialized Vertex AI with model: {self.model}")
                self.initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize Vertex AI: {e}")
                logger.warning("Running AI service in development mode with mock responses")
                
        except ImportError:
            logger.warning("google-cloud-aiplatform not installed. Unable to use Vertex AI.")
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate an embedding vector for a given text.
        
        Args:
            text: The text to generate an embedding for
            
        Returns:
            Optional[List[float]]: The embedding vector or None if generation failed
        """
        if self.dev_mode or not self.initialized:
            # Return a mock embedding in development mode
            logger.info("Development mode: Generating mock embedding")
            # Generate a simple mock embedding of 10 values between 0 and 1
            import random
            return [random.random() for _ in range(10)]
            
        return self.embedding_service.generate_embedding(text)
    
    def generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embedding vectors for multiple texts.
        
        Args:
            texts: The texts to generate embeddings for
            
        Returns:
            List[Optional[List[float]]]: The embedding vectors
        """
        if self.dev_mode or not self.initialized:
            # Return mock embeddings in development mode
            logger.info("Development mode: Generating mock embeddings")
            import random
            return [[random.random() for _ in range(10)] for _ in texts]
            
        return self.embedding_service.generate_embeddings(texts)
    
    def generate_direct_response(self, question: str) -> Dict[str, Any]:
        """Generate a direct response to a question without context.
        
        Args:
            question: The question to answer
            
        Returns:
            Dict[str, Any]: Response with answer and metadata
        """
        if self.dev_mode or not self.initialized:
            return self._generate_mock_response(question)
        
        try:
            # Prepare the prompt
            prompt = f"Question: {question}\n\nAnswer: "
            
            # Generate the response
            if USE_VERTEX_AI:
                response_text = self._generate_vertex_ai_response(prompt)
            else:
                response_text = self._generate_alternative_response(prompt)
            
            # Return the response
            return {
                "answer": response_text,
                "model": self.model,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error generating direct response: {e}")
            logger.error(traceback.format_exc())
            
            # Fallback to mock response
            return self._generate_mock_response(question)
    
    def generate_rag_response(self, question: str, passages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a RAG response to a question with context.
        
        Args:
            question: The question to answer
            passages: The retrieved passages to use as context
            
        Returns:
            Dict[str, Any]: Response with answer and metadata
        """
        if self.dev_mode or not self.initialized:
            return self._generate_mock_rag_response(question, passages)
        
        try:
            # Format the passages for the prompt
            formatted_passages = self._format_passages_for_prompt(passages)
            
            # Create the RAG prompt
            prompt = self._create_rag_prompt(question, formatted_passages)
            
            # Generate the response
            if USE_VERTEX_AI:
                response_text = self._generate_vertex_ai_response(prompt)
            else:
                response_text = self._generate_alternative_response(prompt)
            
            # Return the response
            return {
                "answer": response_text,
                "model": self.model,
                "context_used": True,
                "passages_count": len(passages),
                "success": True
            }
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            logger.error(traceback.format_exc())
            
            # Fallback to mock response
            return self._generate_mock_rag_response(question, passages)
    
    def summarize_content(self, content: Dict[str, Any]) -> str:
        """Summarize the content based on available information.
        
        Args:
            content: The content to summarize
            
        Returns:
            str: The summary
        """
        if self.dev_mode or not self.initialized:
            return self._generate_mock_summary(content)
        
        try:
            # Extract metadata
            metadata = content.get("metadata", {})
            title = metadata.get("title", "")
            description = metadata.get("description", "")
            
            # Extract text from document chunks
            document_chunks = content.get("document_chunks", {})
            text_chunks = []
            
            for file_name, chunks in document_chunks.items():
                for chunk in chunks:
                    text_chunks.append(chunk.get("text", ""))
            
            # Combine text chunks (limit to avoid token limits)
            combined_text = "\n\n".join(text_chunks[:10])
            
            # Create the prompt
            prompt = f"""Please summarize the following content:
Title: {title}
Description: {description}

Document text:
{combined_text[:2000]}  # Limiting text to 2000 characters

Summary:"""
            
            # Generate the summary
            if USE_VERTEX_AI:
                summary = self._generate_vertex_ai_response(prompt)
            else:
                summary = self._generate_alternative_response(prompt)
            
            return summary
        except Exception as e:
            logger.error(f"Error with AI summary: {e}")
            logger.error(traceback.format_exc())
            
            # Fallback to mock summary
            return self._generate_mock_summary(content)
    
    def generate_tags(self, content: Dict[str, Any]) -> List[str]:
        """Generate tags for content document.
        
        Args:
            content: The content document to generate tags for
            
        Returns:
            List[str]: Generated tags
        """
        try:
            logger.info(f"Generating tags for content: {content.get('id')}")
            
            if not self.initialized:
                return self._generate_mock_tags(content)
            
            # Build text representation of the content
            title = content.get("metadata", {}).get("title", "")
            description = content.get("metadata", {}).get("description", "")
            
            # Get existing tags if any
            existing_tags = content.get("metadata", {}).get("tags", [])
            existing_tags_str = ", ".join(existing_tags) if existing_tags else "None"
            
            # Get text from chunks if available
            text_chunks = []
            doc_chunks = content.get("document_chunks", {})
            
            for file_name, chunks in doc_chunks.items():
                for chunk in chunks:
                    chunk_text = chunk.get("text", "").strip()
                    if chunk_text:
                        text_chunks.append(chunk_text)
            
            # Combine information for tag generation
            combined_text = f"Title: {title}\n\nDescription: {description}\n\n"
            
            # Add some chunks for context (limit to avoid token limits)
            if text_chunks:
                combined_text += "Content:\n\n"
                for i, chunk in enumerate(text_chunks[:5]):  # Limit to first 5 chunks
                    combined_text += f"{chunk}\n\n"
            
            # Create tag generation prompt
            prompt = f"""Please generate a list of 5-8 relevant tags for the following conference content.
The tags should be concise (1-3 words each) and capture the key topics, technologies, and concepts discussed.
Existing tags: {existing_tags_str}

{combined_text}

Generate tags in a JSON array format. Example: ["artificial intelligence", "machine learning", "data science"]
Tags:"""
            
            # Generate tags
            if USE_VERTEX_AI:
                response = self._generate_vertex_ai_response(prompt)
            else:
                response = self._generate_alternative_response(prompt)
            
            # Extract tags from response (expecting JSON array)
            try:
                # Find JSON array in response
                start_idx = response.find("[")
                end_idx = response.rfind("]") + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    tags = json.loads(json_str)
                    
                    # Clean and validate tags
                    tags = [tag.strip().lower() for tag in tags if tag and isinstance(tag, str)]
                    
                    # Remove duplicates and limit to 10 tags
                    tags = list(set(tags))[:10]
                    
                    return tags
                else:
                    # Fallback: try to extract tags manually
                    words = response.strip().split(",")
                    tags = [word.strip().lower().strip('"\'[]') for word in words if word.strip()]
                    return tags[:10]
                    
            except Exception as e:
                logger.error(f"Error parsing tags from response: {e}")
                logger.error(f"Response was: {response}")
                return self._generate_mock_tags(content)
                
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            logger.error(traceback.format_exc())
            return self._generate_mock_tags(content)
    
    def _generate_vertex_ai_response(self, prompt: str) -> str:
        """Generate response using Vertex AI.
        
        Args:
            prompt: The prompt to generate a response for
            
        Returns:
            str: Generated response
        """
        try:
            from vertexai.generative_models import GenerativeModel
            
            # Initialize the model
            model = GenerativeModel(self.model)
            
            # Generate response
            response = model.generate_content(prompt)
            
            # Extract text from response
            if hasattr(response, "text"):
                return response.text
            elif hasattr(response, "candidates") and response.candidates:
                return response.candidates[0].content.text
            else:
                logger.warning("Unexpected Vertex AI response format")
                return "I'm unable to provide a response at this time."
                
        except Exception as e:
            logger.error(f"Error with Vertex AI response: {e}")
            logger.error(traceback.format_exc())
            return f"I apologize, but I encountered a technical issue while processing your request. Error: {str(e)}"
    
    def _generate_alternative_response(self, prompt: str) -> str:
        """Generate response using alternative model.
        
        Args:
            prompt: The prompt to generate a response for
            
        Returns:
            str: Generated response
        """
        # This is a placeholder for integration with alternative models
        # In a real implementation, this would call OpenAI, HuggingFace, etc.
        
        try:
            # For demo purposes, just return a mock response
            logger.info("Using alternative model for response generation")
            return self._simple_mock_response(prompt)
            
        except Exception as e:
            logger.error(f"Error with alternative model response: {e}")
            logger.error(traceback.format_exc())
            return "I apologize, but I'm currently experiencing technical difficulties."
    
    def _format_passages_for_prompt(self, passages: List[Dict[str, Any]]) -> str:
        """Format passages for inclusion in prompt.
        
        Args:
            passages: The passages to format
            
        Returns:
            str: Formatted passages for prompt
        """
        formatted_passages = []
        
        for i, passage in enumerate(passages, 1):
            passage_text = passage.get("text", "").strip()
            if passage_text:
                formatted_passages.append(f"[{i}] {passage_text}")
        
        return "\n\n".join(formatted_passages)
    
    def _create_rag_prompt(self, question: str, context: str) -> str:
        """Create a RAG prompt for the model.
        
        Args:
            question: The question to answer
            context: The context from retrieved passages
            
        Returns:
            str: RAG prompt
        """
        return f"""You are a helpful assistant for a conference app that answers questions based only on the provided context. 
If the answer cannot be found in the provided context, acknowledge that and provide general information if possible.
Always maintain a professional, friendly, and informative tone appropriate for a conference setting.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
    
    def _generate_mock_response(self, question: str) -> Dict[str, Any]:
        """Generate a mock response for testing.
        
        Args:
            question: The question to answer
            
        Returns:
            Dict: Mock response
        """
        mock_answer = self._simple_mock_response(question)
        
        return {
            "answer": mock_answer,
            "passages": [],
            "metadata": {
                "model": "mock-model",
                "is_grounded": False
            }
        }
    
    def _generate_mock_rag_response(self, question: str, passages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a mock RAG response for testing.
        
        Args:
            question: The question to answer
            passages: The retrieved passages
            
        Returns:
            Dict: Mock RAG response
        """
        # Create a simple response using the passages
        passage_texts = [p.get("text", "").strip() for p in passages if p.get("text")]
        
        if passage_texts:
            # Extract first sentence from first passage as mock answer
            first_passage = passage_texts[0]
            first_sentence = first_passage.split('.')[0] + '.'
            
            mock_answer = f"Based on the provided information: {first_sentence} The documentation also provides additional details on this topic."
        else:
            mock_answer = f"I don't have specific information about that in the conference materials, but generally speaking, this is a common topic in the industry."
        
        return {
            "answer": mock_answer,
            "passages": passages,
            "metadata": {
                "model": "mock-rag-model",
                "is_grounded": True,
                "passage_count": len(passages)
            }
        }
    
    def _generate_mock_summary(self, content: Dict[str, Any]) -> str:
        """Generate a mock summary for testing.
        
        Args:
            content: The content to summarize
            
        Returns:
            str: Mock summary
        """
        title = content.get("metadata", {}).get("title", "Untitled Content")
        
        return f"This presentation titled '{title}' discusses key concepts and technologies relevant to the conference theme. It provides insights into implementation strategies and best practices, while highlighting important considerations for practitioners in the field."
    
    def _generate_mock_tags(self, content: Dict[str, Any]) -> List[str]:
        """Generate mock tags for testing.
        
        Args:
            content: The content to generate tags for
            
        Returns:
            List[str]: Mock tags
        """
        title = content.get("metadata", {}).get("title", "").lower()
        
        # Generate some relevant tags based on title
        base_tags = ["conference", "technology", "presentation"]
        
        if "ai" in title or "machine" in title:
            extra_tags = ["artificial intelligence", "machine learning", "data science"]
        elif "cloud" in title or "service" in title:
            extra_tags = ["cloud computing", "microservices", "devops"]
        elif "mobile" in title or "app" in title:
            extra_tags = ["mobile development", "app design", "user experience"]
        elif "web" in title or "frontend" in title:
            extra_tags = ["web development", "frontend", "javascript"]
        elif "data" in title or "database" in title:
            extra_tags = ["databases", "data analytics", "big data"]
        else:
            extra_tags = ["innovation", "digital transformation", "best practices"]
        
        return base_tags + extra_tags
    
    def _simple_mock_response(self, prompt: str) -> str:
        """Generate a simple mock text response based on prompt.
        
        Args:
            prompt: The prompt to generate a response for
            
        Returns:
            str: Simple mock response
        """
        # Extract question if in a Q&A format
        question_marker = "QUESTION:"
        if question_marker in prompt:
            question_part = prompt.split(question_marker)[1].strip().split("\n")[0]
        else:
            # Otherwise use the last sentence
            sentences = prompt.strip().split(".")
            question_part = sentences[-2] if len(sentences) > 1 else prompt[-100:]
        
        # Generate a generic response
        if "?" in question_part:
            return f"Regarding your question about {question_part.split('?')[0].strip()}, this is a relevant topic that has been discussed in several sessions at the conference. The main considerations include understanding the context, identifying key requirements, and implementing best practices for your specific use case."
        elif "summary" in prompt.lower():
            return "This presentation covers key principles and practices in the field, with a focus on implementation strategies and real-world applications. The content highlights important considerations for practitioners and provides insights into emerging trends. The examples shared demonstrate practical approaches to common challenges."
        elif "tag" in prompt.lower():
            return '["technology", "innovation", "best practices", "implementation", "industry trends", "case study", "research"]'
        else:
            return "The conference materials address this topic in detail, covering both theoretical foundations and practical implementations. Key aspects to consider include how these concepts apply in different contexts and the best practices recommended by industry experts. For more specific details, you might want to check the conference schedule for related sessions." 