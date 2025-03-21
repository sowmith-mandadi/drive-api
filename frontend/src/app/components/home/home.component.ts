import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ContentService } from '../../services/content.service';

interface FeaturedContent {
  id: string;
  title: string;
  description: string;
  presenter: string;
  imageUrl: string;
  tags: string[];
  date: string;
  views: number;
}

interface TrackStats {
  name: string;
  count: number;
  color: string;
}

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  recentContent: FeaturedContent[] = [];
  popularContent: FeaturedContent[] = [];
  trackStats: TrackStats[] = [];
  isLoading = true;
  
  constructor(
    private contentService: ContentService,
    private router: Router
  ) { }

  ngOnInit(): void {
    // Simulate loading delay
    setTimeout(() => {
      this.loadFeaturedContent();
      this.loadTrackStats();
      this.isLoading = false;
    }, 1000);
  }

  private loadFeaturedContent(): void {
    // Simulate API call for demo purposes
    this.recentContent = this.getMockRecentContent();
    this.popularContent = this.getMockPopularContent();
  }

  private loadTrackStats(): void {
    // Simulate API call for demo purposes
    this.trackStats = [
      { name: 'Web Development', count: 42, color: '#3f51b5' },
      { name: 'Mobile Development', count: 28, color: '#4caf50' },
      { name: 'AI & Machine Learning', count: 35, color: '#f44336' },
      { name: 'Cloud & DevOps', count: 31, color: '#ff9800' },
      { name: 'Data Science', count: 24, color: '#9c27b0' },
      { name: 'Security', count: 18, color: '#607d8b' }
    ];
  }

  navigateToContent(id: string): void {
    this.router.navigate(['/content', id]);
  }

  navigateToSearch(params?: string | Record<string, any>): void {
    if (typeof params === 'string') {
      this.router.navigate(['/search'], { queryParams: { track: params } });
    } else if (params && typeof params === 'object') {
      this.router.navigate(['/search'], { queryParams: params });
    } else {
      this.router.navigate(['/search']);
    }
  }

  navigateToUpload(): void {
    this.router.navigate(['/upload']);
  }

  // Mock data for demonstration
  private getMockRecentContent(): FeaturedContent[] {
    return [
      {
        id: 'c1',
        title: 'Modern Frontend Architecture with Angular and State Management',
        description: 'A deep dive into modern architecture patterns for complex Angular applications',
        presenter: 'Sarah Chen',
        imageUrl: 'assets/images/content/angular-architecture.jpg',
        tags: ['Angular', 'Architecture', 'State Management'],
        date: '2023-06-15',
        views: 423
      },
      {
        id: 'c2',
        title: 'Implementing RAG-Based Search for Conference Content',
        description: 'How to build AI-powered search using Retrieval Augmented Generation',
        presenter: 'Michael Rodriguez',
        imageUrl: 'assets/images/content/rag-search.jpg',
        tags: ['AI', 'Search', 'RAG'],
        date: '2023-06-12',
        views: 317
      },
      {
        id: 'c3',
        title: 'Building Scalable APIs with Node.js and GraphQL',
        description: 'Learn how to design and implement GraphQL APIs that scale',
        presenter: 'David Kim',
        imageUrl: 'assets/images/content/graphql-api.jpg',
        tags: ['GraphQL', 'Node.js', 'API Design'],
        date: '2023-06-08',
        views: 289
      },
      {
        id: 'c4',
        title: 'Containerization Best Practices for Microservices',
        description: 'Optimizing Docker containers for production microservices',
        presenter: 'Emma Wilson',
        imageUrl: 'assets/images/content/containers.jpg',
        tags: ['Docker', 'Kubernetes', 'Microservices'],
        date: '2023-06-02',
        views: 356
      }
    ];
  }

  private getMockPopularContent(): FeaturedContent[] {
    return [
      {
        id: 'p1',
        title: 'Machine Learning for Real-Time Analytics',
        description: 'Implementing ML models for processing streaming data',
        presenter: 'Priya Patel',
        imageUrl: 'assets/images/content/ml-analytics.jpg',
        tags: ['Machine Learning', 'Analytics', 'Streaming'],
        date: '2023-05-28',
        views: 876
      },
      {
        id: 'p2',
        title: 'Zero to Production: Full-Stack Development with MEAN Stack',
        description: 'A complete guide to building applications with MongoDB, Express, Angular and Node.js',
        presenter: 'Alex Johnson',
        imageUrl: 'assets/images/content/mean-stack.jpg',
        tags: ['MEAN', 'Full-Stack', 'Web Development'],
        date: '2023-05-15',
        views: 925
      },
      {
        id: 'p3',
        title: 'Designing for Accessibility: Building Inclusive Web Apps',
        description: 'Best practices for creating accessible and inclusive user experiences',
        presenter: 'David Kim',
        imageUrl: 'assets/images/content/accessibility.jpg',
        tags: ['Accessibility', 'UX', 'Design'],
        date: '2023-05-10',
        views: 753
      },
      {
        id: 'p4',
        title: 'Building Secure APIs: Authentication and Authorization',
        description: 'Security best practices for modern API development',
        presenter: 'Michael Rodriguez',
        imageUrl: 'assets/images/content/api-security.jpg',
        tags: ['Security', 'API', 'Authentication'],
        date: '2023-05-05',
        views: 689
      }
    ];
  }
} 