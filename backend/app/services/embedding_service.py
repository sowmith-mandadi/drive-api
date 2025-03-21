"""Embedding service for generating text embeddings."""

import os
import logging
import traceback
from typing import List, Dict, Any, Optional, Union
import numpy as np

# Default to using Google's text-embedding-gecko if Vertex AI is configured
# Otherwise, fallback to using sentence-transformers locally if available
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-gecko")
USE_VERTEX_AI = os.environ.get("USE_VERTEX_AI", "true").lower() == "true"

# Initialize logger
logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """Initialize the embedding service."""
        self.initialized = False
        self.embedding_model = None
        self.embedding_dim = 768  # Default dimension
        self.dev_mode = not os.path.exists('credentials.json')
        
        if self.dev_mode:
            logger.warning("Credentials file not found. Running embedding service in development mode.")
            return
            
        try:
            if USE_VERTEX_AI:
                # Initialize Vertex AI embedding model if configured
                self._init_vertex_ai()
            else:
                # Initialize local sentence-transformers model as fallback
                self._init_local_model()
                
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            logger.error(traceback.format_exc())
            logger.warning("Running embedding service in development mode with mock embeddings")
    
    def _init_vertex_ai(self):
        """Initialize the Vertex AI embedding model."""
        try:
            from google.cloud import aiplatform
            
            # Check for project ID
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
            if not project_id:
                logger.warning("No GOOGLE_CLOUD_PROJECT environment variable found. Embedding service may not initialize properly.")
            
            # Initialize Vertex AI with project if available
            if project_id:
                aiplatform.init(project=project_id)
            else:
                aiplatform.init()
            
            # For Vertex text-embedding models
            if EMBEDDING_MODEL == "text-embedding-gecko":
                self.embedding_dim = 768
            elif EMBEDDING_MODEL == "text-embedding-gecko-multilingual":
                self.embedding_dim = 768
            
            logger.info(f"Initialized Vertex AI embedding model: {EMBEDDING_MODEL}")
            self.initialized = True
            
        except ImportError:
            logger.warning("google-cloud-aiplatform not installed. Unable to use Vertex AI embeddings.")
        except Exception as e:
            logger.error(f"Error initializing Vertex AI embedding model: {e}")
            logger.error(traceback.format_exc())
    
    def _init_local_model(self):
        """Initialize local sentence-transformers model as fallback."""
        try:
            # Using all-MiniLM-L6-v2 by default as it's small and performs well
            from sentence_transformers import SentenceTransformer
            
            local_model_name = os.environ.get("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            
            # Load the model
            self.embedding_model = SentenceTransformer(local_model_name)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            
            logger.info(f"Initialized local embedding service with model: {local_model_name}")
            self.initialized = True
            
        except ImportError:
            logger.warning("sentence-transformers not installed. Using mock embeddings.")
        except Exception as e:
            logger.error(f"Error initializing local embedding service: {e}")
            logger.error(traceback.format_exc())
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate an embedding vector for a given text.
        
        Args:
            text: The text to generate an embedding for
            
        Returns:
            Optional[List[float]]: The embedding vector or None if generation failed
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding generation")
            return self._generate_mock_embedding("")
            
        if self.dev_mode or not self.initialized:
            # Return a mock embedding in development mode
            logger.info("Development mode: Generating mock embedding")
            return self._generate_mock_embedding(text)
            
        try:
            # Use appropriate method based on initialization
            if USE_VERTEX_AI and self.initialized:
                return self._generate_vertex_ai_embedding(text)
            elif self.embedding_model and not USE_VERTEX_AI:
                return self._generate_local_embedding(text)
            else:
                logger.warning("No embedding model available, using mock embedding")
                return self._generate_mock_embedding(text)
                
        except Exception as e:
            logger.error(f"Error with Vertex AI embedding: {e}")
            logger.error(traceback.format_exc())
            return self._generate_mock_embedding(text)
    
    def generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embedding vectors for multiple texts.
        
        Args:
            texts: The texts to generate embeddings for
            
        Returns:
            List[Optional[List[float]]]: The embedding vectors
        """
        if not texts:
            logger.warning("Empty text list provided for embedding generation")
            return []
            
        if self.dev_mode or not self.initialized:
            # Return mock embeddings in development mode
            logger.info("Development mode: Generating mock embeddings")
            return [self._generate_mock_embedding(text) for text in texts]
            
        try:
            # Use appropriate method based on initialization
            if USE_VERTEX_AI and self.initialized:
                return self._generate_vertex_ai_embeddings_batch(texts)
            elif self.embedding_model and not USE_VERTEX_AI:
                return self._generate_local_embeddings_batch(texts)
            else:
                logger.warning("No embedding model available, using mock embeddings")
                return [self._generate_mock_embedding(text) for text in texts]
                
        except Exception as e:
            logger.error(f"Error generating embeddings batch: {e}")
            logger.error(traceback.format_exc())
            return [self._generate_mock_embedding(text) for text in texts]
    
    def _generate_vertex_ai_embedding(self, text: str) -> List[float]:
        """Generate embedding using Vertex AI.
        
        Args:
            text: The text to generate embedding for
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            from google.cloud import aiplatform
            
            # Using Vertex AI Prediction for embeddings
            endpoint = aiplatform.Endpoint(
                endpoint_name=f"projects/{os.environ.get('GOOGLE_CLOUD_PROJECT')}/locations/us-central1/publishers/google/models/{EMBEDDING_MODEL}"
            )
            
            response = endpoint.predict(instances=[{"content": text}])
            
            # Extract embeddings from response
            embeddings = response.predictions[0]["embeddings"]["values"]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error with Vertex AI embedding: {e}")
            return self._generate_mock_embedding(text)
    
    def _generate_vertex_ai_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts using Vertex AI.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        try:
            from google.cloud import aiplatform
            
            # Using Vertex AI Prediction for embeddings
            endpoint = aiplatform.Endpoint(
                endpoint_name=f"projects/{os.environ.get('GOOGLE_CLOUD_PROJECT')}/locations/us-central1/publishers/google/models/{EMBEDDING_MODEL}"
            )
            
            instances = [{"content": text} for text in texts]
            response = endpoint.predict(instances=instances)
            
            # Extract embeddings from response
            batch_embeddings = []
            for prediction in response.predictions:
                embedding = prediction["embeddings"]["values"]
                batch_embeddings.append(embedding)
            
            return batch_embeddings
            
        except Exception as e:
            logger.error(f"Error with Vertex AI batch embedding: {e}")
            return [self._generate_mock_embedding(text) for text in texts]
    
    def _generate_local_embedding(self, text: str) -> List[float]:
        """Generate embedding using local model.
        
        Args:
            text: The text to generate embedding for
            
        Returns:
            List[float]: Embedding vector
        """
        if not self.embedding_model:
            return self._generate_mock_embedding(text)
            
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(text)
            
            # Convert to Python list of floats
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error with local embedding: {e}")
            return self._generate_mock_embedding(text)
    
    def _generate_local_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts using local model.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not self.embedding_model:
            return [self._generate_mock_embedding(text) for text in texts]
            
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts)
            
            # Convert to Python list of lists of floats
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Error with local batch embedding: {e}")
            return [self._generate_mock_embedding(text) for text in texts]
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate a reproducible mock embedding for testing purposes.
        
        Args:
            text: The text to generate mock embedding for
            
        Returns:
            List[float]: Mock embedding vector
        """
        # Use text hash as seed for reproducible embeddings
        seed = hash(text) % 10000
        np.random.seed(seed)
        
        # Generate random vector
        mock_embedding = np.random.randn(self.embedding_dim).astype(np.float32)
        
        # Normalize to unit length
        mock_embedding = mock_embedding / np.linalg.norm(mock_embedding)
        
        return mock_embedding.tolist()
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for embedding generation.
        
        Args:
            text: The text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        # Basic preprocessing
        text = text.strip()
        
        # Truncate if too long (most models have token limits)
        max_chars = 8000  # Approximate limit to avoid most token limit issues
        if len(text) > max_chars:
            logger.warning(f"Text too long ({len(text)} chars), truncating to {max_chars} chars")
            text = text[:max_chars]
        
        return text
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            float: Cosine similarity score (-1 to 1)
        """
        try:
            if not embedding1 or not embedding2:
                return 0.0
                
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return np.dot(vec1, vec2) / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def find_most_similar(self, query_embedding: List[float], 
                         candidate_embeddings: List[Union[List[float], Dict[str, Any]]], 
                         top_k: int = 5) -> List[Dict[str, Any]]:
        """Find most similar embeddings to a query embedding.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embeddings or dicts with 'embedding' key
            top_k: Number of results to return
            
        Returns:
            List[Dict]: Top k results with similarity scores
        """
        try:
            results = []
            
            for i, candidate in enumerate(candidate_embeddings):
                # Extract embedding from candidate if it's a dict
                if isinstance(candidate, dict):
                    embedding = candidate.get("embedding")
                    metadata = {k: v for k, v in candidate.items() if k != "embedding"}
                else:
                    embedding = candidate
                    metadata = {"index": i}
                
                if not embedding:
                    continue
                
                # Calculate similarity
                similarity = self.cosine_similarity(query_embedding, embedding)
                
                # Add to results
                results.append({
                    "similarity": similarity,
                    "metadata": metadata
                })
            
            # Sort by similarity (descending)
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Return top k results
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding most similar embeddings: {e}")
            return [] 