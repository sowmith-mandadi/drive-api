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
    
    // For demo purposes, use mock data
    // In a real implementation, you would call the content service
    setTimeout(() => {
      this.content = this.getMockContentDetails(id);
      this.isLoading = false;
      
      // Increment view count (simulated)
      console.log(`View count incremented for content ${id}`);
    }, 1500);
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
    return {
      id: id,
      title: '10 infrastructure innovations to accelerate your AI solutions anywhere',
      description: 'Up to 90% of organizations are building across cloud environments, from edge to to multiple clouds - and the scale and speed of AI is putting pressure on these architectures. In this spotlight discover how organizations are leveraging decades of our infrastructure expertise to build secure, sovereign AI solutions. Also, learn how industry leaders are using the latest advances in networking, storage, and distributed cloud solutions to accelerate AI solution deployment anywhere.',
      track: 'Web Development',
      sessionType: 'Presentation',
      tags: ['AI', 'Infrastructure', 'On demand session', 'Technical', 'Retrieval augmented generation'],
      slideUrl: 'https://slides.example.com/angular-architecture',
      videoUrl: 'https://youtube.com/watch?v=example',
      resourcesUrl: 'https://github.com/example/angular-architecture',
      dateAdded: '2025-04-10',
      views: 423,
      likes: 87,
      files: [
        {
          id: 'f1',
          name: 'Infrastructure Innovations Slides.pdf',
          type: 'pdf',
          size: 2400000, // 2.4 MB
          url: '/assets/mock/slides.pdf',
          thumbnailUrl: '/assets/images/content/pdf-thumbnail.jpg',
          dateAdded: '2025-04-10'
        },
        {
          id: 'f2',
          name: 'Code Examples.zip',
          type: 'zip',
          size: 5800000, // 5.8 MB
          url: '/assets/mock/code.zip',
          dateAdded: '2025-04-10'
        },
        {
          id: 'f3',
          name: 'Infrastructure Diagram.png',
          type: 'image',
          size: 850000, // 850 KB
          url: '/assets/images/content/architecture-diagram.png',
          thumbnailUrl: '/assets/images/content/architecture-diagram.png',
          dateAdded: '2025-04-10'
        }
      ],
      presenters: [
        {
          id: 'p2',
          name: 'Sarah Chen',
          title: 'Product Lead',
          company: 'InnovateTech',
          bio: 'Sarah Chen is a product lead with over 8 years of experience building enterprise web applications. She specializes in cloud infrastructure and AI solutions deployment.',
          photoUrl: '/assets/images/presenters/sarah.jpg'
        }
      ],
      aiSummary: 'Up to 90% of organizations are building across cloud environments, from edge to to multiple clouds - and the scale and speed of AI is putting pressure on these architectures. In this spotlight discover how organizations are leveraging decades of our infrastructure expertise to build secure, sovereign AI solutions. Also, learn how industry leaders are using the latest advances in networking, storage, and distributed cloud solutions to accelerate AI solution deployment anywhere.'
    };
  }
} 