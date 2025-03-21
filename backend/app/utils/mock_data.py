"""Mock data generator for testing and development."""

import datetime
import random
import uuid
from typing import List, Dict, Any, Optional, Union

class MockDataGenerator:
    """Generator for mock data used in development and testing."""
    
    def __init__(self):
        """Initialize the mock data generator."""
        # Sample conference tracks
        self.tracks = [
            "AI & Machine Learning",
            "Cloud & Infrastructure",
            "Web Development",
            "Mobile Development",
            "DevOps & SRE",
            "Security",
            "Data Science",
            "Blockchain",
            "AR/VR",
            "IoT"
        ]
        
        # Sample session types
        self.session_types = [
            "Workshop",
            "Keynote",
            "Panel",
            "Technical Talk",
            "Case Study",
            "Deep Dive",
            "Lightning Talk",
            "Hands-on Lab"
        ]
        
        # Sample presentation titles
        self.presentation_titles = [
            "Building Scalable Microservices with Kubernetes",
            "The Future of AI in Enterprise Applications",
            "Modern Web Development with React and GraphQL",
            "Security Best Practices for Cloud Deployments",
            "Machine Learning for Predictive Analytics",
            "Data Engineering at Scale: Lessons Learned",
            "Building Resilient Systems: A Cloud-Native Approach",
            "From Monolith to Microservices: A Journey",
            "Real-time Analytics with Stream Processing",
            "Serverless Architecture: Patterns and Practices",
            "Modern DevOps: CI/CD Pipeline Automation",
            "Blockchain for Enterprise Applications",
            "Progressive Web Apps: The Future of Mobile Web",
            "Edge Computing: Processing Data Where It's Created",
            "Natural Language Processing in the Real World",
            "Designing for Performance and Scalability",
            "The Art of Technical Leadership",
            "Testing Strategies for Distributed Systems",
            "Building Accessible Applications",
            "Machine Learning Operations (MLOps) in Practice"
        ]
        
        # Sample speakers
        self.speakers = [
            {"name": "Dr. Sarah Chen", "title": "Chief AI Officer", "company": "TechInnovate Inc."},
            {"name": "Michael Rodriguez", "title": "Principal Cloud Architect", "company": "CloudScale Solutions"},
            {"name": "Dr. James Wong", "title": "Research Scientist", "company": "AI Research Labs"},
            {"name": "Emily Johnson", "title": "VP of Engineering", "company": "DevOps Masters"},
            {"name": "David Smith", "title": "Security Specialist", "company": "SecureNow"},
            {"name": "Priya Patel", "title": "Data Science Director", "company": "DataDriven Tech"},
            {"name": "Alex Turner", "title": "Frontend Engineering Lead", "company": "WebForward"},
            {"name": "Sophia Garcia", "title": "Mobile Development Manager", "company": "AppGenius"},
            {"name": "Nathan Kim", "title": "Blockchain Architect", "company": "DistributedLedger"},
            {"name": "Olivia Martinez", "title": "DevOps Engineer", "company": "InfrastructureNow"}
        ]
        
        # Sample tags
        self.tags = [
            "artificial intelligence", "machine learning", "deep learning", "neural networks",
            "cloud computing", "kubernetes", "docker", "containerization", "microservices",
            "javascript", "typescript", "react", "vue", "angular", "frontend", "backend",
            "python", "java", "golang", "rust", "programming languages",
            "devops", "ci/cd", "infrastructure as code", "automation", "testing",
            "security", "authentication", "authorization", "encryption", "data protection",
            "data science", "analytics", "big data", "data visualization", "data pipelines",
            "blockchain", "smart contracts", "cryptocurrency", "distributed ledger",
            "mobile development", "ios", "android", "cross-platform", "responsive design",
            "serverless", "lambda functions", "api gateway", "event-driven",
            "databases", "sql", "nosql", "postgresql", "mongodb", "redis",
            "web development", "html", "css", "web assembly", "progressive web apps",
            "iot", "edge computing", "sensors", "connected devices",
            "augmented reality", "virtual reality", "mixed reality", "spatial computing",
            "best practices", "case study", "performance optimization", "scalability",
            "user experience", "user interface", "design systems", "accessibility"
        ]
        
        # Sample locations
        self.locations = [
            "Main Auditorium", "Hall A", "Hall B", "Workshop Room 1", "Workshop Room 2",
            "Conference Room 101", "Conference Room 102", "Expo Floor", "Innovation Lab",
            "Meeting Room East", "Meeting Room West", "Executive Briefing Center"
        ]
    
    def mock_content(self, content_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate mock content item.
        
        Args:
            content_id: Optional ID for the content, generates a new ID if not provided
            
        Returns:
            Dict: Mock content item
        """
        # Generate a content ID if not provided
        if not content_id:
            content_id = str(uuid.uuid4())
        
        # Pick a random title and create a description
        title = random.choice(self.presentation_titles)
        description = f"This session explores {title.lower()} with practical examples and case studies. Attendees will learn best practices and implementation strategies."
        
        # Select a random track and session type
        track = random.choice(self.tracks)
        session_type = random.choice(self.session_types)
        
        # Generate random tags
        content_tags = random.sample(self.tags, random.randint(3, 8))
        
        # Pick random speakers
        content_speakers = random.sample(self.speakers, random.randint(1, 3))
        
        # Generate random date and time
        today = datetime.datetime.now()
        
        # Session date will be between now and 7 days from now
        session_date = today + datetime.timedelta(days=random.randint(0, 7))
        
        # Session time will be between 9 AM and 5 PM
        session_hour = random.randint(9, 17)
        session_time = session_date.replace(hour=session_hour, minute=0)
        
        # Session duration between 30 and 120 minutes
        duration_minutes = random.choice([30, 45, 60, 90, 120])
        
        # Generate mock content
        content = {
            "id": content_id,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "metadata": {
                "title": title,
                "description": description,
                "track": track,
                "session_type": session_type,
                "tags": content_tags,
                "speakers": content_speakers,
                "session_time": session_time.isoformat(),
                "duration_minutes": duration_minutes,
                "location": random.choice(self.locations),
                "ai_summary": self._generate_summary(title, track),
                "ai_tags": random.sample(self.tags, random.randint(3, 6))
            },
            "files": [
                {
                    "name": f"{title.replace(' ', '_')}.pdf",
                    "size": random.randint(500000, 5000000),
                    "type": "application/pdf",
                    "url": f"https://storage.example.com/conferences/files/{content_id}/presentation.pdf"
                }
            ],
            "metadata_embedding": [random.uniform(-1, 1) for _ in range(768)],
            "document_chunks": {
                f"{title.replace(' ', '_')}.pdf": self._generate_document_chunks(title, 5)
            }
        }
        
        return content
    
    def mock_content_list(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate a list of mock content items.
        
        Args:
            count: Number of mock content items to generate
            
        Returns:
            List[Dict]: List of mock content items
        """
        return [self.mock_content() for _ in range(count)]
    
    def mock_rag_response(self, question: str) -> Dict[str, Any]:
        """Generate a mock RAG response.
        
        Args:
            question: The question to generate a mock response for
            
        Returns:
            Dict: Mock RAG response
        """
        # Generate mock passages
        passages = []
        for i in range(3):
            title = random.choice(self.presentation_titles)
            content_id = str(uuid.uuid4())
            
            passages.append({
                "text": f"From: {title}\n\nThis section discusses key principles and implementation strategies for modern applications. It highlights best practices and provides specific examples of how to address common challenges.",
                "id": f"{content_id}_{i}",
                "metadata": {
                    "content_id": content_id,
                    "file_name": f"{title.replace(' ', '_')}.pdf",
                    "chunk_id": i,
                    "title": title,
                    "position_type": "page",
                    "position": i + 1
                }
            })
        
        # Generate a mock answer
        answer = f"Based on the conference materials, {question.strip().rstrip('?')} involves several key considerations. Best practices include establishing clear requirements, leveraging appropriate technologies, and following a structured implementation approach. The speakers emphasized the importance of testing and validation throughout the process."
        
        return {
            "answer": answer,
            "passages": passages,
            "metadata": {
                "model": "mock-rag-model",
                "is_grounded": True,
                "passage_count": len(passages)
            }
        }
    
    def mock_similar_documents(self, query: Optional[str] = None, 
                             content_id: Optional[str] = None, 
                             limit: int = 5) -> List[Dict[str, Any]]:
        """Generate mock similar documents.
        
        Args:
            query: Optional query text
            content_id: Optional content ID to find similar documents to
            limit: Maximum number of results
            
        Returns:
            List[Dict]: Mock similar documents
        """
        # Generate the requested number of similar documents
        similar_docs = []
        
        for _ in range(min(limit, 10)):
            similar_docs.append(self.mock_content())
        
        return similar_docs
    
    def _generate_summary(self, title: str, track: str) -> str:
        """Generate a mock summary based on title and track.
        
        Args:
            title: The title of the content
            track: The track of the content
            
        Returns:
            str: Mock summary
        """
        summaries = [
            f"This {track} presentation explores {title.lower()} with practical insights and implementation strategies. The speaker shares valuable best practices based on real-world experience, highlighting key techniques and methodologies that attendees can apply in their own environments.",
            f"An in-depth exploration of {title.lower()}, this session presents cutting-edge approaches in the {track} domain. The presentation offers a comprehensive overview of current challenges and innovative solutions, with demonstrations of practical applications.",
            f"This compelling {track} session on {title.lower()} addresses common challenges faced by practitioners and presents proven strategies for success. The speaker provides a framework for implementing these concepts, supported by case studies and practical examples."
        ]
        
        return random.choice(summaries)
    
    def _generate_document_chunks(self, title: str, num_chunks: int) -> List[Dict[str, Any]]:
        """Generate mock document chunks.
        
        Args:
            title: The title of the content
            num_chunks: Number of chunks to generate
            
        Returns:
            List[Dict]: Mock document chunks
        """
        chunks = []
        
        for i in range(num_chunks):
            chunk_text = f"Section {i+1}: {title}\n\n"
            
            if i == 0:
                # Introduction
                chunk_text += f"This presentation explores {title.lower()}. We will discuss the fundamental concepts, key technologies, and implementation strategies. Our goal is to provide attendees with practical knowledge they can apply immediately in their own projects.\n\n"
                chunk_text += "Agenda:\n1. Introduction and Overview\n2. Core Concepts\n3. Implementation Strategies\n4. Case Studies\n5. Best Practices\n6. Q&A"
            elif i == 1:
                # Core concepts
                chunk_text += f"Core Concepts of {title}:\n\n"
                chunk_text += "The foundation of this approach rests on several key principles. First, we must understand the problem domain thoroughly. Second, we need to select appropriate technologies and architectures. Third, implementation must follow established patterns while allowing for innovation where beneficial.\n\n"
                chunk_text += "The diagram on this slide illustrates the relationship between these concepts and how they interact within a typical system architecture."
            elif i == 2:
                # Implementation
                chunk_text += f"Implementation Strategies for {title}:\n\n"
                chunk_text += "When implementing these concepts, we recommend a phased approach:\n\n"
                chunk_text += "Phase 1: Discovery and Planning\n- Identify requirements and constraints\n- Select appropriate technologies\n- Design initial architecture\n\n"
                chunk_text += "Phase 2: Development\n- Implement core functionality\n- Continuous testing and feedback\n- Iterative refinement\n\n"
                chunk_text += "Phase 3: Deployment and Evolution\n- Production deployment\n- Monitoring and optimization\n- Continuous improvement"
            elif i == 3:
                # Case studies
                chunk_text += f"Case Studies: {title} in Action\n\n"
                chunk_text += "Case Study 1: Enterprise Implementation\nA Fortune 500 company implemented these approaches and achieved 40% improvement in system performance while reducing operational costs by 25%. Key lessons included the importance of cross-functional teams and continuous feedback loops.\n\n"
                chunk_text += "Case Study 2: Startup Innovation\nA fast-growing startup leveraged these concepts to scale their platform from 10,000 to 1 million users without significant downtime. Their focus on automation and infrastructure as code proved crucial for success."
            else:
                # Best practices
                chunk_text += f"Best Practices for {title}:\n\n"
                chunk_text += "1. Always begin with clear requirements and success metrics\n"
                chunk_text += "2. Choose technologies based on problem fit, not trends\n"
                chunk_text += "3. Design for scalability and maintainability from the start\n"
                chunk_text += "4. Implement robust testing at all levels\n"
                chunk_text += "5. Monitor performance and user experience continuously\n"
                chunk_text += "6. Document decisions, architecture, and code\n\n"
                chunk_text += "Questions to consider for your own implementation:\n- What are your specific requirements and constraints?\n- How will you measure success?\n- What is your timeline and resource availability?"
            
            chunks.append({
                "chunk_id": i,
                "text": chunk_text,
                "page": i + 1,
                "embedding": [random.uniform(-1, 1) for _ in range(768)]
            })
        
        return chunks 