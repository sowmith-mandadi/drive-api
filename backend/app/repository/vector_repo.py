"""Vector repository for storing and searching vector embeddings."""

import os
import logging
import traceback
import uuid
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np

# Configure settings from environment variables
USE_VERTEX_AI = os.environ.get("USE_VERTEX_AI", "true").lower() == "true"
USE_CHROMA = os.environ.get("USE_CHROMA", "false").lower() == "true"

# Initialize logger
logger = logging.getLogger(__name__)

class VectorRepository:
    """Repository for storing and searching vector embeddings."""
    
    def __init__(self):
        """Initialize the vector repository."""
        self.initialized = False
        self.vector_collection = None
        
        # Check if running in Cloud Shell with GCP environment variables
        if 'GOOGLE_CLOUD_PROJECT' in os.environ and 'VECTOR_INDEX_ID' in os.environ:
            logger.info("Using Cloud Shell environment for vector search")
            
            try:
                if USE_VERTEX_AI:
                    # Initialize Vertex AI Vector Search client in Cloud Shell
                    self._init_vertex_ai_vector_search()
                    return
            except Exception as e:
                logger.error(f"Failed to initialize Vector Search in Cloud Shell: {e}")
                logger.warning("Falling back to in-memory store in Cloud Shell")
                
        # If not in Cloud Shell or initialization failed, try other options
        try:
            if USE_VERTEX_AI and os.path.exists('credentials.json'):
                # Initialize Vertex AI Vector Search client if configured
                self._init_vertex_ai_vector_search()
            elif USE_CHROMA:
                # Initialize ChromaDB as a local vector database
                self._init_chroma_db()
            else:
                # Initialize in-memory vector store as fallback
                self._init_in_memory_store()
                
        except Exception as e:
            logger.error(f"Failed to initialize vector repository: {e}")
            logger.error(traceback.format_exc())
            # Initialize in-memory as fallback
            self._init_in_memory_store()
    
    def _init_vertex_ai_vector_search(self):
        """Initialize Vertex AI Vector Search client."""
        try:
            from google.cloud import aiplatform
            
            # Initialize Vertex AI
            project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
            location = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
            
            if not project_id:
                logger.warning("No Google Cloud project ID provided, falling back to in-memory store")
                self._init_in_memory_store()
                return
                
            # Initialize AI Platform
            aiplatform.init(project=project_id, location=location)
            
            # Get Vector Search index information
            index_name = os.environ.get('VECTOR_INDEX_NAME')
            
            if not index_name:
                logger.warning("No Vector Search index name provided, falling back to in-memory store")
                self._init_in_memory_store()
                return
                
            # Initialize Vector Search client
            logger.info(f"Initialized Vertex AI Vector Search with index: {index_name}")
            self.initialized = True
            self.vector_store_type = "vertex_ai"
            self.index_name = index_name
            
        except ImportError:
            logger.warning("google-cloud-aiplatform not installed. Falling back to in-memory store.")
            self._init_in_memory_store()
        except Exception as e:
            logger.error(f"Error initializing Vector Search: {e}")
            logger.error(traceback.format_exc())
            self._init_in_memory_store()
    
    def _init_chroma_db(self):
        """Initialize ChromaDB as local vector database."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Get persistence path from environment
            persistence_path = os.environ.get("CHROMA_PERSISTENCE_PATH", "./data/chroma")
            
            # Create client with persistence
            client = chromadb.Client(Settings(
                persist_directory=persistence_path,
                anonymized_telemetry=False
            ))
            
            # Create or get collection
            collection_name = os.environ.get("CHROMA_COLLECTION", "conference_content")
            
            # Create or get the collection
            self.vector_collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Conference content embeddings"}
            )
            
            logger.info(f"Initialized ChromaDB vector store with collection: {collection_name}")
            self.initialized = True
            self.vector_store_type = "chroma"
            
        except ImportError:
            logger.warning("chromadb not installed. Falling back to in-memory vector store.")
            self._init_in_memory_store()
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            logger.error(traceback.format_exc())
            self._init_in_memory_store()
    
    def _init_in_memory_store(self):
        """Initialize in-memory vector store as fallback."""
        try:
            # Simple in-memory vector store using dictionaries
            self.vectors = {}  # Will store vector_id -> (embedding, metadata)
            self.content_chunks = {}  # Will store content_id -> {chunk_id: vector_id}
            
            logger.info("Initialized in-memory vector store as fallback")
            self.initialized = True
            self.vector_store_type = "in_memory"
            
        except Exception as e:
            logger.error(f"Error initializing in-memory vector store: {e}")
            logger.error(traceback.format_exc())
            self.initialized = False
    
    def add_vector(self, embedding: List[float], metadata: Dict[str, Any]) -> Optional[str]:
        """Add a vector embedding to the repository.
        
        Args:
            embedding: The vector embedding
            metadata: Metadata associated with the embedding
            
        Returns:
            str: ID of the added vector, or None if failed
        """
        if not self.initialized:
            logger.warning("Vector repository not initialized")
            return None
            
        try:
            # Generate a unique ID
            vector_id = str(uuid.uuid4())
            
            if self.vector_store_type == "vertex_ai":
                # Implementation for Vertex AI Vector Search
                return self._add_vector_vertex_ai(vector_id, embedding, metadata)
            elif self.vector_store_type == "chroma":
                # Implementation for ChromaDB
                return self._add_vector_chroma(vector_id, embedding, metadata)
            else:
                # Implementation for in-memory store
                return self._add_vector_in_memory(vector_id, embedding, metadata)
                
        except Exception as e:
            logger.error(f"Error adding vector: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def _add_vector_vertex_ai(self, vector_id: str, embedding: List[float], metadata: Dict[str, Any]) -> Optional[str]:
        """Add a vector to Vertex AI Vector Search.
        
        Args:
            vector_id: The vector ID
            embedding: The vector embedding
            metadata: Metadata associated with the embedding
            
        Returns:
            str: ID of the added vector, or None if failed
        """
        try:
            from google.cloud import aiplatform
            
            # TODO: Implement actual Vertex AI Vector Search indexing
            # This requires more infrastructure setup and is beyond the scope
            # of this example implementation
            
            logger.info(f"Mock adding vector to Vertex AI Vector Search: {vector_id}")
            return vector_id
            
        except Exception as e:
            logger.error(f"Error adding vector to Vertex AI: {e}")
            return None
    
    def _add_vector_chroma(self, vector_id: str, embedding: List[float], metadata: Dict[str, Any]) -> Optional[str]:
        """Add a vector to ChromaDB.
        
        Args:
            vector_id: The vector ID
            embedding: The vector embedding
            metadata: Metadata associated with the embedding
            
        Returns:
            str: ID of the added vector, or None if failed
        """
        try:
            # Convert metadata to string values for ChromaDB
            chroma_metadata = {}
            for k, v in metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    chroma_metadata[k] = v
                elif v is None:
                    continue
                else:
                    # Convert complex types to string
                    chroma_metadata[k] = str(v)
            
            # Add vector to collection
            self.vector_collection.add(
                ids=[vector_id],
                embeddings=[embedding],
                metadatas=[chroma_metadata]
            )
            
            logger.info(f"Added vector to ChromaDB: {vector_id}")
            return vector_id
            
        except Exception as e:
            logger.error(f"Error adding vector to ChromaDB: {e}")
            return None
    
    def _add_vector_in_memory(self, vector_id: str, embedding: List[float], metadata: Dict[str, Any]) -> Optional[str]:
        """Add a vector to in-memory store.
        
        Args:
            vector_id: The vector ID
            embedding: The vector embedding
            metadata: Metadata associated with the embedding
            
        Returns:
            str: ID of the added vector, or None if failed
        """
        try:
            # Store the vector and metadata
            self.vectors[vector_id] = (embedding, metadata)
            
            # Update content chunk mapping if content_id and chunk_id are in metadata
            content_id = metadata.get("content_id")
            chunk_id = metadata.get("chunk_id")
            
            if content_id and chunk_id is not None:
                if content_id not in self.content_chunks:
                    self.content_chunks[content_id] = {}
                    
                # Map chunk to vector ID
                self.content_chunks[content_id][str(chunk_id)] = vector_id
            
            logger.info(f"Added vector to in-memory store: {vector_id}")
            return vector_id
            
        except Exception as e:
            logger.error(f"Error adding vector to in-memory store: {e}")
            return None
    
    def add_vectors_batch(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]) -> List[Optional[str]]:
        """Add multiple vectors in a batch.
        
        Args:
            embeddings: List of vector embeddings
            metadatas: List of metadata dictionaries
            
        Returns:
            List[str]: List of vector IDs, or None for failed vectors
        """
        if not self.initialized:
            logger.warning("Vector repository not initialized")
            return [None] * len(embeddings)
            
        if len(embeddings) != len(metadatas):
            logger.error("Number of embeddings and metadatas must match")
            return [None] * len(embeddings)
            
        try:
            # Generate vector IDs
            vector_ids = [str(uuid.uuid4()) for _ in range(len(embeddings))]
            
            if self.vector_store_type == "vertex_ai":
                # Implementation for Vertex AI Vector Search
                return self._add_vectors_batch_vertex_ai(vector_ids, embeddings, metadatas)
            elif self.vector_store_type == "chroma":
                # Implementation for ChromaDB
                return self._add_vectors_batch_chroma(vector_ids, embeddings, metadatas)
            else:
                # Implementation for in-memory store
                return [self._add_vector_in_memory(vector_ids[i], embeddings[i], metadatas[i])
                        for i in range(len(embeddings))]
                
        except Exception as e:
            logger.error(f"Error adding vectors batch: {e}")
            logger.error(traceback.format_exc())
            return [None] * len(embeddings)
    
    def _add_vectors_batch_vertex_ai(self, vector_ids: List[str], embeddings: List[List[float]], 
                                    metadatas: List[Dict[str, Any]]) -> List[Optional[str]]:
        """Add vectors batch to Vertex AI Vector Search.
        
        Args:
            vector_ids: List of vector IDs
            embeddings: List of vector embeddings
            metadatas: List of metadata dictionaries
            
        Returns:
            List[str]: List of vector IDs, or None for failed vectors
        """
        try:
            # TODO: Implement batch vector addition for Vertex AI
            logger.info(f"Mock adding {len(vector_ids)} vectors to Vertex AI Vector Search")
            return vector_ids
            
        except Exception as e:
            logger.error(f"Error adding vectors batch to Vertex AI: {e}")
            return [None] * len(vector_ids)
    
    def _add_vectors_batch_chroma(self, vector_ids: List[str], embeddings: List[List[float]], 
                                metadatas: List[Dict[str, Any]]) -> List[Optional[str]]:
        """Add vectors batch to ChromaDB.
        
        Args:
            vector_ids: List of vector IDs
            embeddings: List of vector embeddings
            metadatas: List of metadata dictionaries
            
        Returns:
            List[str]: List of vector IDs, or None for failed vectors
        """
        try:
            # Convert metadata to string values for ChromaDB
            chroma_metadatas = []
            for metadata in metadatas:
                chroma_metadata = {}
                for k, v in metadata.items():
                    if isinstance(v, (str, int, float, bool)):
                        chroma_metadata[k] = v
                    elif v is None:
                        continue
                    else:
                        # Convert complex types to string
                        chroma_metadata[k] = str(v)
                chroma_metadatas.append(chroma_metadata)
            
            # Add vectors to collection
            self.vector_collection.add(
                ids=vector_ids,
                embeddings=embeddings,
                metadatas=chroma_metadatas
            )
            
            logger.info(f"Added {len(vector_ids)} vectors to ChromaDB")
            return vector_ids
            
        except Exception as e:
            logger.error(f"Error adding vectors batch to ChromaDB: {e}")
            return [None] * len(vector_ids)
    
    def search_similar_vectors(self, embedding: List[float], num_neighbors: int = 5, 
                             filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors.
        
        Args:
            embedding: The query embedding vector
            num_neighbors: Number of similar vectors to return
            filters: Optional filters for the search
            
        Returns:
            List[Dict]: List of similar vectors with metadata
        """
        if not self.initialized:
            logger.warning("Vector repository not initialized")
            return []
            
        try:
            if self.vector_store_type == "vertex_ai":
                # Implementation for Vertex AI Vector Search
                return self._search_similar_vectors_vertex_ai(embedding, num_neighbors, filters)
            elif self.vector_store_type == "chroma":
                # Implementation for ChromaDB
                return self._search_similar_vectors_chroma(embedding, num_neighbors, filters)
            else:
                # Implementation for in-memory store
                return self._search_similar_vectors_in_memory(embedding, num_neighbors, filters)
                
        except Exception as e:
            logger.error(f"Error searching similar vectors: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def _search_similar_vectors_vertex_ai(self, embedding: List[float], num_neighbors: int = 5, 
                                        filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors using Vertex AI Vector Search.
        
        Args:
            embedding: The query embedding vector
            num_neighbors: Number of similar vectors to return
            filters: Optional filters for the search
            
        Returns:
            List[Dict]: List of similar vectors with metadata
        """
        try:
            # TODO: Implement actual Vertex AI Vector Search
            # For now, return a mock empty result
            logger.info(f"Mock searching with Vertex AI Vector Search: {num_neighbors} neighbors")
            return []
            
        except Exception as e:
            logger.error(f"Error searching similar vectors with Vertex AI: {e}")
            return []
    
    def _search_similar_vectors_chroma(self, embedding: List[float], num_neighbors: int = 5, 
                                     filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors using ChromaDB.
        
        Args:
            embedding: The query embedding vector
            num_neighbors: Number of similar vectors to return
            filters: Optional filters for the search
            
        Returns:
            List[Dict]: List of similar vectors with metadata
        """
        try:
            # Convert filters to ChromaDB where clauses if provided
            where_clause = None
            if filters:
                where_clause = {}
                for k, v in filters.items():
                    if isinstance(v, list):
                        # For list values, use '$in' operator
                        where_clause[k] = {"$in": v}
                    else:
                        where_clause[k] = v
            
            # Query the collection
            results = self.vector_collection.query(
                query_embeddings=[embedding],
                n_results=num_neighbors,
                where=where_clause
            )
            
            # Process results
            similar_vectors = []
            
            if results and 'ids' in results and results['ids']:
                ids = results['ids'][0]  # First query result
                distances = results.get('distances', [[0] * len(ids)])[0]
                metadatas = results.get('metadatas', [[{}] * len(ids)])[0]
                
                for i, vector_id in enumerate(ids):
                    # Calculate similarity from distance (ChromaDB returns distances)
                    # Convert distance to similarity score (1 - normalized distance)
                    similarity = 1.0 - min(distances[i], 1.0)
                    
                    # Get metadata
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    
                    # Add to results
                    similar_vectors.append({
                        "id": vector_id,
                        "similarity": similarity,
                        "content_id": metadata.get("content_id", "unknown"),
                        "chunk_id": metadata.get("chunk_id", "0"),
                        "metadata": metadata
                    })
            
            logger.info(f"Found {len(similar_vectors)} similar vectors with ChromaDB")
            return similar_vectors
            
        except Exception as e:
            logger.error(f"Error searching similar vectors with ChromaDB: {e}")
            return []
    
    def _search_similar_vectors_in_memory(self, embedding: List[float], num_neighbors: int = 5, 
                                        filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors using in-memory store.
        
        Args:
            embedding: The query embedding vector
            num_neighbors: Number of similar vectors to return
            filters: Optional filters for the search
            
        Returns:
            List[Dict]: List of similar vectors with metadata
        """
        try:
            # Convert embedding to numpy array
            query_vector = np.array(embedding)
            
            # Calculate similarities for all vectors
            similarities = []
            
            for vector_id, (stored_embedding, metadata) in self.vectors.items():
                # Apply filters if provided
                if filters and not self._matches_filters(metadata, filters):
                    continue
                
                # Calculate cosine similarity
                stored_vector = np.array(stored_embedding)
                similarity = self._cosine_similarity(query_vector, stored_vector)
                
                # Store result
                similarities.append({
                    "id": vector_id,
                    "similarity": similarity,
                    "content_id": metadata.get("content_id", "unknown"),
                    "chunk_id": metadata.get("chunk_id", "0"),
                    "metadata": metadata
                })
            
            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Return top results
            top_results = similarities[:num_neighbors]
            
            logger.info(f"Found {len(top_results)} similar vectors in-memory")
            return top_results
            
        except Exception as e:
            logger.error(f"Error searching similar vectors in-memory: {e}")
            return []
    
    def delete_vectors_by_content_id(self, content_id: str) -> bool:
        """Delete all vectors associated with a content ID.
        
        Args:
            content_id: The content ID to delete vectors for
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.initialized:
            logger.warning("Vector repository not initialized")
            return False
            
        try:
            if self.vector_store_type == "vertex_ai":
                # Implementation for Vertex AI Vector Search
                return self._delete_vectors_by_content_id_vertex_ai(content_id)
            elif self.vector_store_type == "chroma":
                # Implementation for ChromaDB
                return self._delete_vectors_by_content_id_chroma(content_id)
            else:
                # Implementation for in-memory store
                return self._delete_vectors_by_content_id_in_memory(content_id)
                
        except Exception as e:
            logger.error(f"Error deleting vectors by content ID: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _delete_vectors_by_content_id_vertex_ai(self, content_id: str) -> bool:
        """Delete vectors by content ID using Vertex AI Vector Search.
        
        Args:
            content_id: The content ID to delete vectors for
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # TODO: Implement deletion from Vertex AI Vector Search
            logger.info(f"Mock deleting vectors for content ID {content_id} from Vertex AI")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from Vertex AI: {e}")
            return False
    
    def _delete_vectors_by_content_id_chroma(self, content_id: str) -> bool:
        """Delete vectors by content ID using ChromaDB.
        
        Args:
            content_id: The content ID to delete vectors for
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Delete by metadata filter
            self.vector_collection.delete(
                where={"content_id": content_id}
            )
            
            logger.info(f"Deleted vectors for content ID {content_id} from ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from ChromaDB: {e}")
            return False
    
    def _delete_vectors_by_content_id_in_memory(self, content_id: str) -> bool:
        """Delete vectors by content ID using in-memory store.
        
        Args:
            content_id: The content ID to delete vectors for
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get vector IDs to delete
            vector_ids_to_delete = []
            
            for vector_id, (_, metadata) in self.vectors.items():
                if metadata.get("content_id") == content_id:
                    vector_ids_to_delete.append(vector_id)
            
            # Delete vectors
            for vector_id in vector_ids_to_delete:
                if vector_id in self.vectors:
                    del self.vectors[vector_id]
            
            # Remove content from mapping
            if content_id in self.content_chunks:
                del self.content_chunks[content_id]
            
            logger.info(f"Deleted {len(vector_ids_to_delete)} vectors for content ID {content_id} from in-memory store")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from in-memory store: {e}")
            return False
    
    def update_vector_metadata(self, vector_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a vector.
        
        Args:
            vector_id: The vector ID to update metadata for
            metadata: The new metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.initialized:
            logger.warning("Vector repository not initialized")
            return False
            
        try:
            if self.vector_store_type == "vertex_ai":
                # Implementation for Vertex AI Vector Search
                return False  # Not supported in this implementation
            elif self.vector_store_type == "chroma":
                # Implementation for ChromaDB
                return self._update_vector_metadata_chroma(vector_id, metadata)
            else:
                # Implementation for in-memory store
                return self._update_vector_metadata_in_memory(vector_id, metadata)
                
        except Exception as e:
            logger.error(f"Error updating vector metadata: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _update_vector_metadata_chroma(self, vector_id: str, metadata: Dict[str, Any]) -> bool:
        """Update vector metadata using ChromaDB.
        
        Args:
            vector_id: The vector ID to update metadata for
            metadata: The new metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert metadata to ChromaDB compatible format
            chroma_metadata = {}
            for k, v in metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    chroma_metadata[k] = v
                elif v is None:
                    continue
                else:
                    # Convert complex types to string
                    chroma_metadata[k] = str(v)
            
            # Update metadata
            self.vector_collection.update(
                ids=[vector_id],
                metadatas=[chroma_metadata]
            )
            
            logger.info(f"Updated metadata for vector {vector_id} in ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Error updating vector metadata in ChromaDB: {e}")
            return False
    
    def _update_vector_metadata_in_memory(self, vector_id: str, metadata: Dict[str, Any]) -> bool:
        """Update vector metadata using in-memory store.
        
        Args:
            vector_id: The vector ID to update metadata for
            metadata: The new metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if vector_id not in self.vectors:
                logger.warning(f"Vector {vector_id} not found in in-memory store")
                return False
            
            # Get the embedding
            embedding, _ = self.vectors[vector_id]
            
            # Update the vector with new metadata
            self.vectors[vector_id] = (embedding, metadata)
            
            logger.info(f"Updated metadata for vector {vector_id} in in-memory store")
            return True
            
        except Exception as e:
            logger.error(f"Error updating vector metadata in in-memory store: {e}")
            return False
    
    def find_similar_by_direct_comparison(self, embedding: List[float], 
                                        embeddings: List[Tuple[str, List[float]]], 
                                        limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar documents by direct comparison.
        
        Args:
            embedding: The query embedding
            embeddings: List of (content_id, embedding) tuples
            limit: Maximum number of results
            
        Returns:
            List[Dict]: Similar documents with scores
        """
        try:
            if not embeddings:
                return []
                
            # Convert query embedding to numpy array
            query_vector = np.array(embedding)
            
            # Calculate similarities
            similarities = []
            
            for content_id, doc_embedding in embeddings:
                doc_vector = np.array(doc_embedding)
                similarity = self._cosine_similarity(query_vector, doc_vector)
                
                similarities.append({
                    "id": content_id,
                    "similarity": similarity
                })
            
            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Return limited results
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Error in direct comparison: {e}")
            return []
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            float: Cosine similarity (between -1 and 1)
        """
        try:
            # Normalize vectors
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            # Calculate cosine similarity
            return np.dot(vec1, vec2) / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches filters.
        
        Args:
            metadata: The metadata to check
            filters: The filters to apply
            
        Returns:
            bool: True if metadata matches filters, False otherwise
        """
        for key, filter_value in filters.items():
            metadata_value = metadata.get(key)
            
            # Handle list values
            if isinstance(filter_value, list):
                # If the filter is a list, check if metadata value is in the list
                if not metadata_value or (not isinstance(metadata_value, list) and metadata_value not in filter_value):
                    if isinstance(metadata_value, list):
                        # Check for any intersection between the lists
                        if not any(value in filter_value for value in metadata_value):
                            return False
                    else:
                        return False
            # Handle scalar values
            elif metadata_value != filter_value:
                return False
                
        return True 