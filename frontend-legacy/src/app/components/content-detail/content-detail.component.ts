import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ContentService } from '../../services/content.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { RagService } from '../../services/rag.service';

interface ContentFile {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
  thumbnailUrl?: string;
  dateAdded: string;
  imageError?: boolean;
}

interface Presenter {
  id: string;
  name: string;
  title: string;
  company: string;
  bio?: string;
  photoUrl?: string;
}

interface ContentDetails {
  id: string;
  title: string;
  description: string;
  track: string;
  sessionType: string;
  tags: string[];
  slideUrl?: string;
  videoUrl?: string;
  resourcesUrl?: string;
  dateAdded: string;
  views: number;
  likes: number;
  files: ContentFile[];
  presenters: Presenter[];
  aiSummary?: string;
}

@Component({
  selector: 'app-content-detail',
  templateUrl: './content-detail.component.html',
  styleUrls: ['./content-detail.component.scss']
})
export class ContentDetailComponent implements OnInit {
  contentId: string | null = null;
  content: ContentDetails | null = null;
  isLoading = true;
  error = false;
  activeTab = 0;
  isLiked = false;
  showingAllFiles = false;
  
  // RAG Question Answering properties
  ragQuestion: string = '';
  ragAnswer: string = '';
  isAskingQuestion = false;
  
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private contentService: ContentService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private ragService: RagService
  ) { }

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.contentId = params.get('id');
      if (this.contentId) {
        this.loadContentDetails(this.contentId);
      } else {
        this.handleError('Content ID not provided');
      }
    });
  }

  private loadContentDetails(id: string): void {
    this.isLoading = true;
    this.error = false;
    
    // In a real implementation with the API
    this.contentService.getContentById(id).subscribe({
      next: (content) => {
        // Transform backend data format to frontend model
        this.content = this.transformContentDetails(content);
        this.isLoading = false;
        
        // Increment view count (simulated)
        console.log(`View count incremented for content ${id}`);
      },
      error: (err) => {
        console.error('Error loading content:', err);
        this.handleError('Could not load the requested content');
        
        // Fallback to mock data for demo purposes
        setTimeout(() => {
          this.content = this.getMockContentDetails(id);
          this.isLoading = false;
          this.error = false;
        }, 1500);
      }
    });
  }
  
  /**
   * Transform content data from backend format to frontend model
   */
  private transformContentDetails(content: any): ContentDetails {
    // Extract metadata from the content object
    const metadata = content.metadata || {};
    
    // Map the file data
    const files: ContentFile[] = [];
    if (content.files && Array.isArray(content.files)) {
      content.files.forEach((file: any) => {
        files.push({
          id: file.id || `file-${Math.random().toString(36).substr(2, 9)}`,
          name: file.name,
          type: file.type || this.getFileTypeFromName(file.name),
          size: file.size || 0,
          url: file.url,
          thumbnailUrl: file.thumbnailUrl,
          dateAdded: file.dateAdded || new Date().toISOString(),
          imageError: false
        });
      });
    }
    
    // Map the presenters data
    const presenters: Presenter[] = [];
    if (metadata.speakers && Array.isArray(metadata.speakers)) {
      metadata.speakers.forEach((speaker: any) => {
        if (typeof speaker === 'string') {
          // If speaker is just a string, create a basic presenter object
          presenters.push({
            id: `presenter-${Math.random().toString(36).substr(2, 9)}`,
            name: speaker,
            title: '',
            company: ''
          });
        } else {
          // If speaker is an object, map its properties
          presenters.push({
            id: speaker.id || `presenter-${Math.random().toString(36).substr(2, 9)}`,
            name: speaker.name,
            title: speaker.title || '',
            company: speaker.company || '',
            bio: speaker.bio,
            photoUrl: speaker.photoUrl
          });
        }
      });
    }
    
    // Build the content details object
    return {
      id: content.id,
      title: metadata.title || "Untitled Content",
      description: metadata.description || "",
      track: metadata.track || "",
      sessionType: metadata.session_type || "",
      tags: metadata.tags || [],
      slideUrl: metadata.slide_url,
      videoUrl: metadata.video_url,
      resourcesUrl: metadata.resources_url,
      dateAdded: content.created_at || new Date().toISOString(),
      views: metadata.views || 0,
      likes: metadata.likes || 0,
      files: files,
      presenters: presenters,
      aiSummary: metadata.ai_summary || ""
    };
  }
  
  /**
   * Get file type from filename
   */
  private getFileTypeFromName(filename: string): string {
    if (!filename) return 'unknown';
    
    const extension = filename.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf': return 'pdf';
      case 'png': case 'jpg': case 'jpeg': case 'gif': case 'webp': return 'image';
      case 'zip': case 'rar': case 'tar': case 'gz': return 'zip';
      case 'doc': case 'docx': return 'doc';
      case 'xls': case 'xlsx': return 'xls';
      case 'ppt': case 'pptx': return 'ppt';
      default: return 'unknown';
    }
  }

  toggleLike(): void {
    if (!this.content) return;
    
    this.isLiked = !this.isLiked;
    if (this.isLiked) {
      this.content.likes++;
      this.showMessage('Added to favorites');
    } else {
      this.content.likes--;
      this.showMessage('Removed from favorites');
    }
  }

  shareContent(): void {
    if (!this.content) return;
    
    // In a real implementation, you would open a share dialog
    // For now, simulate copying a link to clipboard
    this.copyToClipboard(window.location.href);
    this.showMessage('Link copied to clipboard');
  }

  downloadFile(file: ContentFile): void {
    // In a real implementation, you would initiate the download
    console.log(`Downloading file: ${file.name}`);
    this.showMessage(`Downloading ${file.name}...`);
    
    // Simulate download by opening the URL in a new tab
    window.open(file.url, '_blank');
  }

  openUrl(url: string): void {
    if (!url) return;
    
    window.open(url, '_blank');
  }

  // Handle image loading errors
  handleImageError(event: Event, file: ContentFile): void {
    console.warn('Image failed to load:', file.thumbnailUrl);
    file.imageError = true;
  }

  navigateBack(): void {
    this.router.navigate(['/search']);
  }
  
  // RAG question answering method
  askQuestion(): void {
    if (!this.ragQuestion || !this.contentId) return;
    
    this.isAskingQuestion = true;
    this.ragAnswer = '';
    
    // For demo purposes, simulate API call
    setTimeout(() => {
      this.ragAnswer = `Based on the content you're viewing about "${this.content?.title}", here's what I found:
      
The presentation covers key concepts of ${this.content?.tags.join(', ')}. 

The main takeaways include:
- Best practices for structuring large-scale applications
- Implementing effective state management with NgRx
- Performance optimization techniques
- Testing strategies for maintainable code`;
      
      this.isAskingQuestion = false;
    }, 2000);
    
    // In a real implementation, you would call the RAG service like this:
    /*
    this.ragService.askQuestion(this.ragQuestion, this.contentId)
      .subscribe({
        next: (response) => {
          this.ragAnswer = response.answer;
          this.isAskingQuestion = false;
        },
        error: (error) => {
          this.showMessage('Error processing your question. Please try again.');
          console.error('Error asking question:', error);
          this.isAskingQuestion = false;
        }
      });
    */
  }

  private copyToClipboard(text: string): void {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
  }

  private showMessage(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000
    });
  }

  private handleError(message: string): void {
    this.error = true;
    this.isLoading = false;
    this.showMessage(`Error: ${message}`);
  }

  // Mock data for demonstration
  private getMockContentDetails(id: string): ContentDetails {
    const mockData: ContentDetails = {
      id: '12345',
      title: 'Leveraging Cloud Infrastructure for Enterprise AI Solutions',
      description: 'This session explores how to build scalable AI infrastructure using cloud services. We cover deployment patterns, optimization techniques, and cost management strategies.',
      track: 'Cloud Infrastructure',
      sessionType: 'Technical Presentation',
      tags: ['AI', 'Cloud', 'Enterprise', 'Infrastructure'],
      slideUrl: 'https://example.com/slides',
      videoUrl: 'https://example.com/video',
      resourcesUrl: 'https://example.com/resources',
      dateAdded: '2023-03-10',
      views: 3475,
      likes: 287,
      aiSummary: 'This presentation discusses how infrastructure innovations can be effectively leveraged to build and deploy AI solutions at scale. The content emphasizes cloud-native approaches for AI deployment, and highlights techniques for cost optimization while maintaining performance. The primary audience is infrastructure architects and IT decision-makers looking to enhance their AI capabilities.',
      files: [
        // PDF mock file
        {
          id: '456',
          name: 'Product Specifications.pdf',
          type: 'application/pdf',
          size: 3500000, // 3.5 MB
          dateAdded: '2023-03-15',
          url: 'https://example.com/files/specs.pdf',
          thumbnailUrl: 'https://via.placeholder.com/300x200?text=PDF+Document',
          imageError: false
        },
        // Infrastructure diagram mock file
        {
          id: '789',
          name: 'Cloud Architecture Diagram.png',
          type: 'image/png',
          size: 2500000, // 2.5 MB
          dateAdded: '2023-04-05',
          url: 'https://example.com/files/diagram.png',
          thumbnailUrl: 'https://via.placeholder.com/300x200?text=Architecture+Diagram',
          imageError: false
        },
        // Presentation slides
        {
          id: '123',
          name: 'Presentation Slides.pptx',
          type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
          size: 2500000, // 2.5 MB
          dateAdded: '2023-03-20',
          url: 'https://example.com/files/presentation.pptx',
          imageError: false
        },
        // Document
        {
          id: '234',
          name: 'Research Document.docx',
          type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          size: 1500000, // 1.5 MB
          dateAdded: '2023-03-25',
          url: 'https://example.com/files/document.docx',
          imageError: false
        },
        // Spreadsheet
        {
          id: '345',
          name: 'Data Analysis.xlsx',
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          size: 1800000, // 1.8 MB
          dateAdded: '2023-04-01',
          url: 'https://example.com/files/spreadsheet.xlsx',
          imageError: false
        },
        // Zip file
        {
          id: '567',
          name: 'Source Code.zip',
          type: 'application/zip',
          size: 5000000, // 5 MB
          dateAdded: '2023-04-10',
          url: 'https://example.com/files/source.zip',
          imageError: false
        }
      ],
      presenters: []
    };
    return mockData;
  }

  /**
   * Determines file type based on file name extension
   */
  getFileType(filename: string): string {
    if (!filename) return 'unknown';
    
    const extension = filename.split('.').pop()?.toLowerCase() || '';
    
    // Image types
    if (['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'].includes(extension)) {
      return 'image';
    }
    
    // Document types
    if (['pdf'].includes(extension)) {
      return 'pdf';
    }
    
    if (['doc', 'docx'].includes(extension)) {
      return 'doc';
    }
    
    if (['xls', 'xlsx', 'csv'].includes(extension)) {
      return 'xls';
    }
    
    if (['ppt', 'pptx'].includes(extension)) {
      return 'ppt';
    }
    
    if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension)) {
      return 'zip';
    }
    
    return 'unknown';
  }
  
  /**
   * Show all files instead of just the first 3
   */
  showAllFiles(): void {
    this.showingAllFiles = true;
  }
} 