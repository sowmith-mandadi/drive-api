"""AI service for generating embeddings and text responses."""

import os
import logging
import traceback
import random
import json
from typing import List, Dict, Any, Optional

# Initialize logger
logger = logging.getLogger(__name__)

class AIService:
    """Service for AI operations."""
    
    def __init__(self):
        """Initialize the AI service."""
        # Check if running in Cloud Shell with GCP environment variables
        if 'GOOGLE_CLOUD_PROJECT' in os.environ:
            logger.info("Using Cloud Shell environment for AI service")
            self.dev_mode = False
            try:
                # Initialize Vertex AI
                self._init_vertex_ai()
            except Exception as e:
                logger.error(f"Failed to initialize AI service in Cloud Shell: {e}")
                logger.error(traceback.format_exc())
                logger.warning("Running AI service in development mode")
                self.dev_mode = True
            return
                
        # If not in Cloud Shell, check for credentials file
        self.dev_mode = not os.path.exists('credentials.json')
        if self.dev_mode:
            logger.warning("Credentials file not found. Running AI service in development mode.")
        else:
            try:
                # Initialize Vertex AI
                self._init_vertex_ai()
            except Exception as e:
                logger.error(f"Error initializing AI service: {e}")
                logger.warning("Running AI service in development mode")
                self.dev_mode = True
    
    def _init_vertex_ai(self):
        """Initialize Vertex AI."""
        try:
            from vertexai.preview.generative_models import GenerativeModel
            from vertexai.language_models import TextEmbeddingModel
            import vertexai
            
            # Initialize Vertex AI
            project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
            location = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
            
            if project_id:
                vertexai.init(project=project_id, location=location)
            else:
                # In Cloud Shell, this should work without explicit project
                vertexai.init(location=location)
            
            # Initialize models - use the correct format for Gemini
            try:
                # Use GenerativeModel with gemini-1.5-pro model
                self.generation_model = GenerativeModel("gemini-1.5-pro")
                logger.info("Successfully initialized Gemini 1.5 Pro model")
            except Exception as e:
                logger.error(f"Error initializing Gemini model: {e}")
                try:
                    # Fall back to gemini-1.0-pro if 1.5 is not available
                    self.generation_model = GenerativeModel("gemini-1.0-pro")
                    logger.info("Successfully initialized Gemini 1.0 Pro model as fallback")
                except Exception as e2:
                    logger.error(f"Error initializing fallback Gemini model: {e2}")
                    self.dev_mode = True
                    return
            
            # Initialize embedding model
            try:
                embedding_model_name = os.environ.get('TEXT_EMBEDDING_MODEL', 'textembedding-gecko@latest')
                self.embedding_model = TextEmbeddingModel.from_pretrained(embedding_model_name)
                logger.info(f"Successfully initialized embedding model: {embedding_model_name}")
            except Exception as e:
                logger.error(f"Error initializing embedding model: {e}")
                self.dev_mode = True
                return
                
            logger.info("Vertex AI initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Required packages not available: {e}")
            self.dev_mode = True
        except Exception as e:
            logger.error(f"Error initializing Vertex AI: {e}")
            logger.error(traceback.format_exc())
            self.dev_mode = True
            
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate an embedding for text using Vertex AI.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Optional[List[float]]: Embedding vector
        """
        if self.dev_mode:
            logger.info(f"[DEV MODE] Generating mock embedding for text: {text[:50]}...")
            return self._generate_mock_embedding(text)
            
        try:
            if not text or not text.strip():
                return self._generate_mock_embedding("")
                
            # Use Vertex AI embedding model
            embedding = self.embedding_model.get_embeddings([text])[0].values
            return list(embedding)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return self._generate_mock_embedding(text)
            
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate a mock embedding vector.
        
        Args:
            text: Text to generate mock embedding for
            
        Returns:
            List[float]: Mock embedding vector
        """
        # Generate a deterministic but random-looking embedding
        random.seed(hash(text) % 10000)
        return [random.uniform(-1, 1) for _ in range(768)]

    def generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embedding vectors for multiple texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List[Optional[List[float]]]: List of embedding vectors
        """
        if self.dev_mode:
            logger.info(f"[DEV MODE] Generating mock embeddings for {len(texts)} texts")
            return [self._generate_mock_embedding(text) for text in texts]
            
        try:
            # Use Vertex AI embedding model
            embeddings = []
            batch_size = 5  # Process in smaller batches to avoid timeouts
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                batch_texts = [t for t in batch_texts if t and t.strip()]
                
                if not batch_texts:
                    continue
                    
                batch_embeddings = self.embedding_model.get_embeddings(batch_texts)
                embeddings.extend([list(e.values) for e in batch_embeddings])
                
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [self._generate_mock_embedding(text) for text in texts]
    
    def generate_rag_response(self, question: str, passages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a RAG response using Vertex AI.
        
        Args:
            question: The question to answer
            passages: List of relevant passages
            
        Returns:
            Dict: RAG response with answer and passages
        """
        if self.dev_mode:
            logger.info(f"[DEV MODE] Generating mock RAG response for question: {question}")
            return {
                "answer": f"This is a mock answer to the question: {question}",
                "passages": passages[:3],
                "source": "mock_data",
                "is_mock": True
            }
            
        try:
            # Construct prompt with passages
            prompt = self._construct_rag_prompt(question, passages)
            
            # Call Vertex AI with updated API
            from vertexai.preview.generative_models import GenerationConfig
            
            response = self.generation_model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=1024
                )
            )
            
            return {
                "answer": response.text,
                "passages": passages[:5],  # Only include top passages
                "source": "vertex_ai"
            }
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return {
                "answer": f"Error generating response: {str(e)}",
                "passages": passages[:3] if passages else [],
                "source": "error",
                "error": str(e)
            }
    
    def _construct_rag_prompt(self, question: str, passages: List[Dict[str, Any]]) -> str:
        """Construct a prompt for RAG.
        
        Args:
            question: The question to answer
            passages: List of relevant passages
            
        Returns:
            str: Constructed prompt
        """
        prompt = f"""You are an AI assistant answering questions about conference content.
Answer the question based only on the provided passages. If the passages don't contain the information needed to answer the question, reply with "I don't have enough information to answer this question."

Question: {question}

Relevant passages:
"""
        
        # Add passages
        for i, passage in enumerate(passages[:5]):  # Use top 5 passages
            passage_text = passage.get("text", "")
            source = passage.get("source", "Unknown")
            prompt += f"\nPassage {i+1} (Source: {source}):\n{passage_text}\n"
            
        prompt += "\nAnswer:"
        
        return prompt
    
    def generate_direct_response(self, question: str) -> Dict[str, Any]:
        """Generate a direct response without grounding.
        
        Args:
            question: The question to answer
            
        Returns:
            Dict: Response
        """
        if self.dev_mode:
            logger.info(f"[DEV MODE] Generating mock direct response for question: {question}")
            return {
                "answer": f"This is a mock direct answer to: {question}",
                "passages": [],
                "source": "mock_data",
                "is_mock": True
            }
            
        try:
            # Construct prompt
            prompt = f"""You are an AI assistant answering questions about conference content.
Please answer the following question to the best of your ability:

Question: {question}

Answer:"""
            
            # Call Vertex AI with updated API
            from vertexai.preview.generative_models import GenerationConfig
            
            response = self.generation_model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=1024
                )
            )
            
            return {
                "answer": response.text,
                "passages": [],
                "source": "vertex_ai_direct"
            }
        except Exception as e:
            logger.error(f"Error generating direct response: {e}")
            return {
                "answer": f"Error generating response: {str(e)}",
                "passages": [],
                "source": "error",
                "error": str(e)
            }
    
    def summarize_content(self, content: Dict[str, Any]) -> str:
        """Generate a summary for content.
        
        Args:
            content: Content to summarize
            
        Returns:
            str: Generated summary
        """
        if self.dev_mode:
            logger.info(f"[DEV MODE] Generating mock summary for content: {content.get('id', 'unknown')}")
            return f"This is a mock summary of the content with ID: {content.get('id', 'unknown')}"
            
        try:
            # Extract metadata and chunks
            metadata = content.get("metadata", {})
            title = metadata.get("title", "Untitled")
            description = metadata.get("description", "")
            
            # Get document chunks if available
            document_chunks = content.get("document_chunks", {})
            chunks_text = ""
            
            # Add text from chunks
            for file_name, chunks in document_chunks.items():
                chunks_text += f"\nContent from {file_name}:\n"
                # Only use a few chunks to avoid token limits
                for chunk in chunks[:5]:
                    chunks_text += f"{chunk.get('text', '')}\n"
            
            # Construct prompt
            prompt = f"""You are an AI assistant tasked with summarizing conference content.
Please provide a comprehensive summary of the following content:

Title: {title}
Description: {description}
{chunks_text}

Summary:"""
            
            # Call Vertex AI with updated API
            from vertexai.preview.generative_models import GenerationConfig
            
            response = self.generation_model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=512
                )
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def generate_tags(self, content: Dict[str, Any]) -> List[str]:
        """Generate tags for content.
        
        Args:
            content: Content to generate tags for
            
        Returns:
            List[str]: Generated tags
        """
        if self.dev_mode:
            logger.info(f"[DEV MODE] Generating mock tags for content: {content.get('id', 'unknown')}")
            return ["ai", "cloud", "conference", "mock-tag"]
            
        try:
            # Extract metadata and chunks
            metadata = content.get("metadata", {})
            title = metadata.get("title", "Untitled")
            description = metadata.get("description", "")
            
            # Get document chunks if available
            document_chunks = content.get("document_chunks", {})
            chunks_text = ""
            
            # Add text from chunks (limited)
            for file_name, chunks in document_chunks.items():
                chunks_text += f"\nContent from {file_name}:\n"
                # Only use a few chunks to avoid token limits
                for chunk in chunks[:3]:
                    chunks_text += f"{chunk.get('text', '')}\n"
            
            # Construct prompt
            prompt = f"""You are an AI assistant tasked with generating relevant tags for conference content.
Please generate up to 10 relevant, specific tags for the following content. Return the tags as a JSON array of strings.

Title: {title}
Description: {description}
{chunks_text}

Tags:"""
            
            # Call Vertex AI with updated API
            from vertexai.preview.generative_models import GenerationConfig
            
            response = self.generation_model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=256
                )
            )
            
            # Parse the response for tags
            text = response.text.strip()
            
            # Try to extract JSON array
            try:
                # Try to find JSON array in the response
                if "[" in text and "]" in text:
                    start = text.find("[")
                    end = text.rfind("]") + 1
                    json_str = text[start:end]
                    tags = json.loads(json_str)
                    return tags
                else:
                    # Fallback: Split by commas or newlines
                    tags = [t.strip() for t in text.replace('"', '').replace("'", "").split(",")]
                    return [t for t in tags if t]
            except Exception as e:
                logger.error(f"Error parsing tags from response: {e}")
                # Fallback parsing
                tags = [t.strip() for t in text.split("\n") if t.strip()]
                return tags[:10]  # Take at most 10 tags
                
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return ["error", "generation-failed"]
    
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