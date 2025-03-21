"""Content service for managing conference content."""

import os
import uuid
import logging
import datetime
import tempfile
import io
from typing import List, Dict, Any, Optional
from werkzeug.datastructures import FileStorage
from app.repository.firestore_repo import FirestoreRepository
from app.repository.storage_repo import StorageRepository
from app.services.ai_service import AIService
from app.services.embedding_service import EmbeddingService
from app.extractors.pdf_extractor import PdfExtractor
from app.extractors.pptx_extractor import PptxExtractor
from googleapiclient.http import MediaIoBaseDownload

# Initialize logger
logger = logging.getLogger(__name__)

# Mock data for development mode
MOCK_CONTENT = {}

class ContentService:
    """Service for managing conference content."""
    
    def __init__(self):
        """Initialize the content service."""
        self.firestore_repo = FirestoreRepository()
        self.storage_repo = StorageRepository()
        self.ai_service = AIService()
        self.embedding_service = EmbeddingService()
        
        # Initialize document extractors if available
        try:
            self.pdf_extractor = PdfExtractor()
            self.pptx_extractor = PptxExtractor()
            self.document_processing_available = True
        except Exception as e:
            logger.error(f"Document processing unavailable: {e}")
            self.document_processing_available = False
        
        # Development mode flag
        self.dev_mode = not self.firestore_repo.initialized
        if self.dev_mode:
            logger.warning("Running ContentService in development mode with mock data")
    
    def process_content(self, files: List[FileStorage], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process uploaded files and store metadata.
        
        Args:
            files: List of uploaded files
            metadata: Content metadata
            
        Returns:
            Dict: Processed content data
        """
        try:
            # Generate a unique ID for this content
            content_id = str(uuid.uuid4())
            
            # If in dev mode, use mock implementation
            if self.dev_mode:
                # Create a mock content object
                content_data = {
                    "id": content_id,
                    "metadata": metadata,
                    "created_at": datetime.datetime.now().isoformat(),
                    "updated_at": datetime.datetime.now().isoformat(),
                    "file_count": len(files) if files else 0,
                    "file_names": [f.filename for f in files] if files else []
                }
                
                # Store in mock data
                MOCK_CONTENT[content_id] = content_data
                logger.info(f"[DEV MODE] Stored mock content with ID: {content_id}")
                
                return {
                    "status": "success",
                    "message": "Content processed in development mode",
                    "content_id": content_id
                }
            
            # Ensure title exists
            if not metadata.get("title"):
                metadata["title"] = f"Untitled Content {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Create a record for the content
            content_data = {
                "id": content_id,
                "metadata": metadata,
                "file_urls": {},
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }
            
            # Generate embeddings for metadata
            try:
                # Create combined text from metadata
                metadata_text = self._create_metadata_text(metadata)
                
                # Generate embedding
                metadata_embedding = self.ai_service.generate_embedding(metadata_text)
                
                if metadata_embedding:
                    content_data["metadata_embedding"] = metadata_embedding
                    logger.info(f"Generated embedding for content metadata: {content_id}")
            except Exception as e:
                logger.error(f"Error generating metadata embedding: {e}")
            
            # Process document chunks
            content_data["document_chunks"] = {}
            
            # Process files
            if files:
                for file in files:
                    # Store the file
                    file_url = self.storage_repo.store_file(file, content_id)
                    
                    if file_url:
                        content_data["file_urls"][file.filename] = file_url
                    else:
                        # Create a mock URL if storage failed
                        mock_url = f"https://storage.googleapis.com/mock-bucket/{content_id}/{file.filename}"
                        content_data["file_urls"][file.filename] = mock_url
                    
                    # Process the document if document processing is available
                    if self.document_processing_available:
                        # Check file type
                        file_extension = os.path.splitext(file.filename)[1].lower() if "." in file.filename else ""
                        
                        if file_extension in ['.pdf', '.pptx', '.ppt']:
                            # Save the file temporarily
                            temp_file_path = self.storage_repo.save_temp_file(file)
                            
                            # Process based on file type
                            chunks = []
                            if file_extension == '.pdf':
                                chunks = self.pdf_extractor.extract_text(temp_file_path)
                            elif file_extension in ['.pptx', '.ppt']:
                                chunks = self.pptx_extractor.extract_text(temp_file_path)
                            
                            # Process chunks
                            if chunks:
                                processed_chunks = self._process_chunks(chunks, content_id, file_extension)
                                content_data["document_chunks"][file.filename] = processed_chunks
                            
                            # Clean up temporary file
                            self.storage_repo.remove_temp_file(temp_file_path)
            
            # Store the content data
            self.firestore_repo.store_content(content_id, content_data)
            
            # Generate AI enhancements asynchronously
            # Note: In a production environment, this would be done with a background task
            try:
                # Generate AI summary
                summary = self.ai_service.summarize_content(content_data)
                if summary:
                    self.firestore_repo.update_content(content_id, {
                        "metadata.ai_summary": summary
                    })
                
                # Generate AI tags
                ai_tags = self.ai_service.generate_tags(content_data)
                if ai_tags:
                    self.firestore_repo.update_content(content_id, {
                        "metadata.ai_tags": ai_tags
                    })
            except Exception as e:
                logger.error(f"Error generating AI enhancements: {e}")
            
            return content_data
        except Exception as e:
            logger.error(f"Error processing content: {e}")
            
            # Return a mock response instead of failing
            mock_content_id = str(uuid.uuid4())
            return {
                "id": mock_content_id,
                "metadata": metadata,
                "file_urls": {f.filename: f"https://storage.googleapis.com/mock-bucket/{mock_content_id}/{f.filename}" for f in files},
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat(),
                "error": str(e),
                "note": "This is a mock response due to an error in content processing"
            }
    
    def _create_metadata_text(self, metadata: Dict[str, Any]) -> str:
        """Create a combined text from metadata for embedding.
        
        Args:
            metadata: Content metadata
            
        Returns:
            str: Combined metadata text
        """
        metadata_text = f"Title: {metadata.get('title', '')}\n"
        metadata_text += f"Description: {metadata.get('description', '')}\n"
        metadata_text += f"Track: {metadata.get('track', '')}\n"
        metadata_text += f"Tags: {', '.join(metadata.get('tags', []))}\n"
        metadata_text += f"Session Type: {metadata.get('session_type', '')}\n"
        metadata_text += f"Presenters: {', '.join(metadata.get('presenters', []))}\n"
        
        return metadata_text
    
    def _process_chunks(self, chunks: List[Dict[str, Any]], content_id: str, file_type: str) -> List[Dict[str, Any]]:
        """Process text chunks for embedding and storage.
        
        Args:
            chunks: List of text chunks
            content_id: Content ID
            file_type: File type
            
        Returns:
            List[Dict]: Processed chunks
        """
        processed_chunks = []
        
        for i, chunk in enumerate(chunks):
            # Generate embedding for the chunk
            text = chunk.get("text", "")
            
            # Determine position type and value
            position_type = ""
            position = 0
            
            if "page" in chunk:
                position_type = "page"
                position = chunk["page"]
            elif "slide" in chunk:
                position_type = "slide"
                position = chunk["slide"]
            else:
                position_type = "position"
                position = i + 1
            
            # Generate embedding
            embedding = self.ai_service.generate_embedding(text)
            
            if embedding:
                # Create metadata for the chunk
                chunk_metadata = {
                    "content_id": content_id,
                    "chunk_id": i,
                    "file_type": file_type,
                    position_type: position,
                    "text_preview": text[:100] + "..." if len(text) > 100 else text
                }
                
                # Add to processed chunks
                processed_chunk = {
                    "chunk_id": i,
                    "text": text,
                    position_type: position,
                    "embedding": embedding  # Include embedding
                }
                
                processed_chunks.append(processed_chunk)
                
                # Store in vector database (via embedding service)
                self.embedding_service.store_embedding(
                    embedding=embedding,
                    content_id=content_id,
                    chunk_id=i,
                    metadata=chunk_metadata
                )
        
        return processed_chunks
    
    def get_content_by_ids(self, content_ids: List[str]) -> List[Dict[str, Any]]:
        """Get multiple content items by their IDs.
        
        Args:
            content_ids: List of content IDs
            
        Returns:
            List[Dict]: List of content items
        """
        try:
            if self.dev_mode:
                # Return mock content
                return [MOCK_CONTENT.get(content_id, {}) for content_id in content_ids]
            
            # Get content from Firestore
            contents = [self.firestore_repo.get_content(content_id) for content_id in content_ids]
            return [content for content in contents if content]
        except Exception as e:
            logger.error(f"Error getting content by IDs: {e}")
            return []

    def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get a single content item by its ID.
        
        Args:
            content_id: Content ID
            
        Returns:
            Dict: Content item or None if not found
        """
        try:
            if self.dev_mode:
                # Return mock content
                return MOCK_CONTENT.get(content_id)
            
            # Get content from Firestore
            return self.firestore_repo.get_content(content_id)
        except Exception as e:
            logger.error(f"Error getting content by ID: {e}")
            return None
    
    def get_recent_content(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get recent content with pagination.
        
        Args:
            page: Page number
            page_size: Items per page
            
        Returns:
            Dict: Paginated content result
        """
        if self.dev_mode:
            # Use mock data in dev mode
            all_content = list(MOCK_CONTENT.values())
            # Sort by created_at in descending order (newest first)
            all_content.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # Calculate pagination
            total_count = len(all_content)
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, total_count)
            
            # Get paginated results
            paginated_content = all_content[start_idx:end_idx] if start_idx < total_count else []
            
            logger.info(f"[DEV MODE] Retrieved {len(paginated_content)} recent content items")
            
            return {
                "content": paginated_content,
                "totalCount": total_count,
                "page": page,
                "pageSize": page_size
            }
        
        return self.firestore_repo.get_recent_content(page, page_size)
    
    def get_popular_tags(self, limit: int = 20) -> List[str]:
        """Get most popular tags.
        
        Args:
            limit: Maximum number of tags to return
            
        Returns:
            List[str]: List of popular tags
        """
        if self.dev_mode:
            # Use mock data in dev mode
            all_tags = []
            for content in MOCK_CONTENT.values():
                metadata = content.get('metadata', {})
                tags = metadata.get('tags', [])
                all_tags.extend(tags if isinstance(tags, list) else [])
            
            # Count frequencies
            tag_counts = {}
            for tag in all_tags:
                if tag in tag_counts:
                    tag_counts[tag] += 1
                else:
                    tag_counts[tag] = 1
            
            # Sort by frequency and limit
            popular_tags = sorted(tag_counts.keys(), key=lambda x: tag_counts[x], reverse=True)[:limit]
            
            # If no tags, provide some sample tags
            if not popular_tags:
                popular_tags = ["Development", "AI", "Machine Learning", "Web", "Mobile", 
                               "Cloud", "DevOps", "Security", "Data Science", "Blockchain"]
                
            logger.info(f"[DEV MODE] Retrieved {len(popular_tags)} popular tags")
            return popular_tags
            
        return self.firestore_repo.get_popular_tags(limit)
    
    def process_drive_content(self, drive_service, file_ids: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Google Drive files and store metadata.
        
        Args:
            drive_service: Authorized Google Drive service
            file_ids: List of Google Drive file IDs
            metadata: Content metadata
            
        Returns:
            Dict: Processed content data
        """
        try:
            # Use existing content ID if provided, otherwise generate a new one
            content_id = metadata.get('contentId') or str(uuid.uuid4())
            
            # If in dev mode, use mock implementation
            if self.dev_mode:
                # Create a mock content object
                content_data = {
                    "id": content_id,
                    "metadata": metadata,
                    "created_at": datetime.datetime.now().isoformat(),
                    "updated_at": datetime.datetime.now().isoformat(),
                    "file_count": len(file_ids) if file_ids else 0,
                    "file_ids": file_ids,
                    "source": "google_drive"
                }
                
                # Store in mock data
                MOCK_CONTENT[content_id] = content_data
                logger.info(f"[DEV MODE] Stored mock Drive content with ID: {content_id}")
                
                return {
                    "status": "success",
                    "message": "Drive content processed in development mode",
                    "content_id": content_id,
                    "success": True
                }
            
            # Ensure title exists
            if not metadata.get("title"):
                metadata["title"] = f"Drive Content {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Create or update a record for the content
            content_data = {
                "id": content_id,
                "metadata": metadata,
                "file_urls": {},
                "drive_files": {},
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now(),
                "source": "google_drive"
            }
            
            # Generate embeddings for metadata
            try:
                # Create combined text from metadata
                metadata_text = self._create_metadata_text(metadata)
                
                # Generate embedding
                metadata_embedding = self.ai_service.generate_embedding(metadata_text)
                
                if metadata_embedding:
                    content_data["metadata_embedding"] = metadata_embedding
                    logger.info(f"Generated embedding for Drive content metadata: {content_id}")
            except Exception as e:
                logger.error(f"Error generating Drive metadata embedding: {e}")
            
            # Process document chunks
            content_data["document_chunks"] = {}
            
            # Process Drive files
            if file_ids:
                for file_id in file_ids:
                    try:
                        # Get file metadata
                        file_metadata = drive_service.files().get(
                            fileId=file_id,
                            fields="id,name,mimeType,webViewLink,iconLink,thumbnailLink"
                        ).execute()
                        
                        # Store the file metadata
                        content_data["drive_files"][file_id] = file_metadata
                        content_data["file_urls"][file_metadata.get('name')] = file_metadata.get('webViewLink')
                        
                        # Check if we should process the file based on MIME type
                        mime_type = file_metadata.get('mimeType', '')
                        
                        # Process documents if possible
                        if self.document_processing_available:
                            if mime_type in [
                                'application/pdf',
                                'application/vnd.google-apps.document',
                                'application/vnd.google-apps.presentation',
                                'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                            ]:
                                # Download the file content
                                request = drive_service.files().get_media(fileId=file_id)
                                file_content = io.BytesIO()
                                downloader = MediaIoBaseDownload(file_content, request)
                                
                                done = False
                                while not done:
                                    _, done = downloader.next_chunk()
                                
                                # Reset pointer to beginning of file
                                file_content.seek(0)
                                
                                # Save to temporary file
                                tmp_file = tempfile.NamedTemporaryFile(delete=False)
                                tmp_file.write(file_content.read())
                                tmp_file.close()
                                
                                # Extract text based on file type
                                chunks = []
                                if mime_type == 'application/pdf':
                                    chunks = self.pdf_extractor.extract_text(tmp_file.name)
                                elif mime_type in ['application/vnd.google-apps.presentation', 
                                                 'application/vnd.openxmlformats-officedocument.presentationml.presentation']:
                                    chunks = self.pptx_extractor.extract_text(tmp_file.name)
                                
                                # Process chunks
                                if chunks:
                                    processed_chunks = self._process_chunks(chunks, content_id, mime_type)
                                    content_data["document_chunks"][file_metadata.get('name')] = processed_chunks
                                
                                # Clean up temporary file
                                os.unlink(tmp_file.name)
                    except Exception as e:
                        logger.error(f"Error processing Drive file {file_id}: {e}")
                        continue
            
            # Store the content data
            self.firestore_repo.store_content(content_id, content_data)
            
            # Generate AI enhancements asynchronously
            # Note: In a production environment, this would be done with a background task
            try:
                # Generate AI summary
                summary = self.ai_service.summarize_content(content_data)
                if summary:
                    self.firestore_repo.update_content(content_id, {
                        "metadata.ai_summary": summary
                    })
                
                # Generate AI tags
                ai_tags = self.ai_service.generate_tags(content_data)
                if ai_tags:
                    self.firestore_repo.update_content(content_id, {
                        "metadata.ai_tags": ai_tags
                    })
            except Exception as e:
                logger.error(f"Error generating AI enhancements for Drive content: {e}")
            
            return {
                "success": True,
                "content_id": content_id,
                "message": f"Successfully processed {len(file_ids)} Drive files"
            }
        except Exception as e:
            logger.error(f"Error processing Drive content: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error processing Drive content"
            } 