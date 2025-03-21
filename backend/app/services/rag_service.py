"""RAG service for question answering and similar document finding."""

import logging
from typing import List, Dict, Any, Optional
from app.services.ai_service import AIService
from app.repository.firestore_repo import FirestoreRepository
from app.repository.vector_repo import VectorRepository
from app.utils.mock_data import MockDataGenerator

# Initialize logger
logger = logging.getLogger(__name__)

class RagService:
    """Service for RAG (Retrieval-Augmented Generation) operations."""
    
    def __init__(self):
        """Initialize the RAG service."""
        self.ai_service = AIService()
        self.firestore_repo = FirestoreRepository()
        self.vector_repo = VectorRepository()
        self.mock_generator = MockDataGenerator()
        
        # Development mode flag
        self.dev_mode = not self.firestore_repo.initialized
        if self.dev_mode:
            logger.warning("Running RAGService in development mode with mock data")
    
    def get_rag_response(self, question: str, content_ids: Optional[List[str]] = None, 
                        filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a RAG response using Vertex AI.
        
        Args:
            question: The question to answer
            content_ids: Optional list of content IDs to scope the search
            filters: Optional filters for content
            
        Returns:
            Dict: RAG response with answer and passages
        """
        try:
            logger.info(f"Generating RAG response for question: {question}")
            
            # Handle development mode
            if self.dev_mode:
                logger.info(f"[DEV MODE] Generating mock RAG response for: {question}")
                mock_passages = self.mock_generator.generate_mock_passages(question)
                return {
                    "answer": self.mock_generator.generate_mock_answer(question, mock_passages),
                    "passages": mock_passages,
                    "source": "mock_data",
                    "is_mock": True
                }
            
            # Get relevant passages
            passages = self._get_relevant_passages(question, content_ids, filters)
            
            if not passages:
                # If no passages found, fall back to ungrounded response
                logger.warning("No passages found for RAG, using model without grounding")
                return self.ai_service.generate_direct_response(question)
            
            # Generate response with retrieved passages
            response = self.ai_service.generate_rag_response(question, passages)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG: {e}")
            # Fallback to ungrounded response
            return self.ai_service.generate_direct_response(question)
    
    def _get_relevant_passages(self, question: str, content_ids: Optional[List[str]] = None, 
                              filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get relevant passages for a question.
        
        Args:
            question: The question to answer
            content_ids: Optional list of content IDs to scope the search
            filters: Optional filters for content
            
        Returns:
            List[Dict]: List of relevant passages
        """
        passages = []
        
        # Try to use vector search if available
        if self.vector_repo.initialized:
            try:
                # Generate an embedding for the question
                question_embedding = self.ai_service.generate_embedding(question)
                
                if question_embedding:
                    # Search for similar vectors
                    vector_results = self.vector_repo.search_similar_vectors(
                        embedding=question_embedding,
                        num_neighbors=5
                    )
                    
                    if vector_results:
                        # Process the results
                        for result in vector_results:
                            content_id = result.get("content_id")
                            chunk_id = result.get("chunk_id")
                            
                            # Skip if we have content_ids filter and this content is not in it
                            if content_ids and content_id not in content_ids:
                                continue
                            
                            # Get the content document
                            content = self.firestore_repo.get_content(content_id)
                            
                            if content:
                                # Extract chunk information
                                doc_chunks = content.get("document_chunks", {})
                                
                                for file_name, chunks in doc_chunks.items():
                                    for chunk in chunks:
                                        if chunk.get("chunk_id") == int(chunk_id):
                                            # Create passage from chunk
                                            chunk_text = chunk.get("text", "")
                                            chunk_position = ""
                                            
                                            # Add position info (page/slide)
                                            if "page" in chunk:
                                                chunk_position = f" (Page {chunk['page']})"
                                            elif "slide" in chunk:
                                                chunk_position = f" (Slide {chunk['slide']})"
                                            
                                            metadata = content.get("metadata", {})
                                            title = metadata.get("title", "Untitled")
                                            
                                            # Create passage text with context
                                            passage_text = f"From: {title}{chunk_position}\n\n{chunk_text}"
                                            
                                            # Add to passages
                                            passages.append({
                                                "text": passage_text,
                                                "id": f"{content_id}_{chunk_id}",
                                                "metadata": {
                                                    "content_id": content_id,
                                                    "file_name": file_name,
                                                    "chunk_id": chunk_id,
                                                    "title": title,
                                                    "position_type": "page" if "page" in chunk else "slide" if "slide" in chunk else "unknown",
                                                    "position": chunk.get("page", chunk.get("slide", 0))
                                                }
                                            })
            except Exception as e:
                logger.error(f"Error using vector search for RAG: {e}")
        
        # If no passages found from vector search, fall back to content-level search
        if not passages:
            try:
                # Query content from Firestore
                contents = []
                
                if content_ids:
                    # Get specific content by IDs
                    contents = self.firestore_repo.get_contents_by_ids(content_ids)
                elif filters:
                    # Get filtered content
                    contents = self.firestore_repo.find_content_by_filters(filters, limit=10)
                else:
                    # Get recent content
                    result = self.firestore_repo.get_recent_content(page=1, page_size=10)
                    contents = result.get("content", [])
                
                # Create passages from content metadata
                for content in contents:
                    # Combine title and description for better context
                    title = content.get("metadata", {}).get("title", "")
                    description = content.get("metadata", {}).get("description", "")
                    
                    # Only include if there's actual content
                    if title or description:
                        passage_text = f"Title: {title}\n\nDescription: {description}"
                        passages.append({
                            "text": passage_text,
                            "id": content.get("id", "unknown"),
                            "metadata": {
                                "content_id": content.get("id", "unknown"),
                                "title": title
                            }
                        })
            except Exception as e:
                logger.error(f"Error querying content for RAG passages: {e}")
        
        return passages
    
    def summarize_document(self, content_id: str) -> str:
        """Summarize a document using Vertex AI.
        
        Args:
            content_id: The ID of the content to summarize
            
        Returns:
            str: Generated summary
        """
        try:
            logger.info(f"Summarize request for content ID: {content_id}")
            
            # Get the content
            content = self.firestore_repo.get_content(content_id)
            
            if not content:
                logger.warning(f"Content not found with ID: {content_id}")
                return "Content not found"
            
            # Generate summary
            summary = self.ai_service.summarize_content(content)
            
            # Update the content with the summary
            if summary:
                self.firestore_repo.update_content(content_id, {"metadata.ai_summary": summary})
            
            return summary
        except Exception as e:
            logger.error(f"Error in document summarization: {e}")
            return f"Error summarizing document: {str(e)}"
    
    def generate_tags(self, content_id: str) -> List[str]:
        """Generate tags for a document using Vertex AI.
        
        Args:
            content_id: The ID of the content to generate tags for
            
        Returns:
            List[str]: Generated tags
        """
        try:
            logger.info(f"Generate tags request for content ID: {content_id}")
            
            # Get the content
            content = self.firestore_repo.get_content(content_id)
            
            if not content:
                logger.warning(f"Content not found with ID: {content_id}")
                return []
            
            # Generate tags
            tags = self.ai_service.generate_tags(content)
            
            # Update the content with the tags
            if tags:
                self.firestore_repo.update_content(content_id, {"metadata.ai_tags": tags})
            
            return tags
        except Exception as e:
            logger.error(f"Error in tag generation: {e}")
            return []
    
    def find_similar_documents(self, query: Optional[str] = None, content_id: Optional[str] = None, 
                              limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar documents based on a query or content ID.
        
        Args:
            query: Text query to find similar documents
            content_id: Content ID to find similar documents to
            limit: Maximum number of results
            
        Returns:
            List[Dict]: Similar documents
        """
        try:
            logger.info(f"Finding similar documents for query: {query}, content_id: {content_id}")
            
            similar_docs = []
            
            # We need either a query or a content ID
            if not query and not content_id:
                logger.warning("No query or content ID provided for similarity search")
                return self.mock_generator.mock_similar_documents(query, content_id, limit)
            
            # Get base document embedding if content_id provided
            base_embedding = None
            
            if content_id:
                # Get the content
                content = self.firestore_repo.get_content(content_id)
                
                if content:
                    # Get embedding if it exists
                    base_embedding = content.get("metadata_embedding")
                    
                    # If no embedding exists, generate one
                    if not base_embedding:
                        # Create text representation for embedding
                        title = content.get("metadata", {}).get("title", "")
                        description = content.get("metadata", {}).get("description", "")
                        content_text = f"{title}. {description}"
                        
                        # Generate embedding
                        base_embedding = self.ai_service.generate_embedding(content_text)
            
            # If query provided but no base embedding
            elif query:
                # Generate embedding for the query
                base_embedding = self.ai_service.generate_embedding(query)
            
            # If we have a base embedding, find similar documents
            if base_embedding:
                # Try using vector search if available
                if self.vector_repo.initialized:
                    # Use vector search for similarity
                    vector_results = self.vector_repo.search_similar_vectors(
                        embedding=base_embedding,
                        num_neighbors=limit
                    )
                    
                    if vector_results:
                        # Get unique content IDs
                        content_ids = set()
                        for result in vector_results:
                            content_ids.add(result.get("content_id"))
                        
                        # Get content documents
                        for similar_content_id in content_ids:
                            if similar_content_id != content_id:  # Skip the original document
                                content = self.firestore_repo.get_content(similar_content_id)
                                if content:
                                    similar_docs.append(content)
                                    
                                    # If we have enough results, break
                                    if len(similar_docs) >= limit:
                                        break
                
                # If no results from vector search or it's not available, use direct comparison
                if not similar_docs:
                    # Get recent content to compare with
                    result = self.firestore_repo.get_recent_content(page=1, page_size=20)
                    contents = result.get("content", [])
                    
                    # Prepare for direct comparison
                    embeddings_to_compare = []
                    
                    for content in contents:
                        content_id_to_compare = content.get("id")
                        
                        # Skip the original document
                        if content_id_to_compare == content_id:
                            continue
                        
                        # Get embedding
                        embedding = content.get("metadata_embedding")
                        
                        if embedding:
                            embeddings_to_compare.append((content_id_to_compare, embedding))
                    
                    if embeddings_to_compare:
                        # Use direct comparison
                        comparison_results = self.vector_repo.find_similar_by_direct_comparison(
                            embedding=base_embedding,
                            embeddings=embeddings_to_compare,
                            limit=limit
                        )
                        
                        # Get the content for the results
                        for result in comparison_results:
                            similar_content_id = result.get("id")
                            content = self.firestore_repo.get_content(similar_content_id)
                            if content:
                                similar_docs.append(content)
            
            # If still no results, try metadata filtering
            if not similar_docs and content_id:
                content = self.firestore_repo.get_content(content_id)
                
                if content:
                    # Filter based on common metadata
                    track = content.get("metadata", {}).get("track")
                    tags = content.get("metadata", {}).get("tags", [])
                    
                    filters = {}
                    if track:
                        filters["tracks"] = [track]
                    elif tags and len(tags) > 0:
                        filters["tags"] = [tags[0]]
                    
                    # Get filtered content
                    filtered_content = self.firestore_repo.find_content_by_filters(filters, limit)
                    
                    # Filter out the original content
                    similar_docs = [doc for doc in filtered_content if doc.get("id") != content_id]
            
            # If still no results, use mock data
            if not similar_docs:
                return self.mock_generator.mock_similar_documents(query, content_id, limit)
            
            return similar_docs[:limit]
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            # Fallback to mock implementation
            return self.mock_generator.mock_similar_documents(query, content_id, limit) 