import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ContentService } from '../../services/content.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';

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
  
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private contentService: ContentService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog
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
      title: 'Modern Frontend Architecture with Angular and State Management',
      description: 'In this session, we explore advanced patterns for building large-scale Angular applications. We cover state management strategies using NgRx, performance optimization techniques, and modular architecture approaches that help teams scale their development efforts. You\'ll learn how to structure your application for maintainability, implement effective testing strategies, and leverage Angular\'s latest features to create robust enterprise applications.',
      track: 'Web Development',
      sessionType: 'Presentation',
      tags: ['Angular', 'Architecture', 'State Management', 'NgRx', 'Performance'],
      slideUrl: 'https://slides.example.com/angular-architecture',
      videoUrl: 'https://youtube.com/watch?v=example',
      resourcesUrl: 'https://github.com/example/angular-architecture',
      dateAdded: '2023-06-15',
      views: 423,
      likes: 87,
      files: [
        {
          id: 'f1',
          name: 'Angular Architecture Slides.pdf',
          type: 'pdf',
          size: 2400000, // 2.4 MB
          url: '/assets/mock/slides.pdf',
          thumbnailUrl: '/assets/images/content/pdf-thumbnail.jpg',
          dateAdded: '2023-06-15'
        },
        {
          id: 'f2',
          name: 'Code Examples.zip',
          type: 'zip',
          size: 5800000, // 5.8 MB
          url: '/assets/mock/code.zip',
          dateAdded: '2023-06-15'
        },
        {
          id: 'f3',
          name: 'Architecture Diagram.png',
          type: 'image',
          size: 850000, // 850 KB
          url: '/assets/images/content/architecture-diagram.png',
          thumbnailUrl: '/assets/images/content/architecture-diagram.png',
          dateAdded: '2023-06-15'
        }
      ],
      presenters: [
        {
          id: 'p2',
          name: 'Sarah Chen',
          title: 'Product Lead',
          company: 'InnovateTech',
          bio: 'Sarah Chen is a product lead with over 8 years of experience building enterprise web applications. She specializes in Angular development and modern frontend architecture.',
          photoUrl: '/assets/images/presenters/sarah.jpg'
        }
      ],
      aiSummary: 'This presentation covers modern Angular architecture patterns with a focus on state management using NgRx. The speaker discusses component design, module organization, and performance optimization techniques. Key takeaways include implementing effective testing strategies, structuring large-scale applications, and leveraging dependency injection for maintainable code.'
    };
  }
} 