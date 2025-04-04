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

interface Topic {
  id: string;
  name: string;
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
  topics: Topic[] = [];
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
      this.loadTopics();
      this.isLoading = false;
    }, 1000);
  }

  private loadFeaturedContent(): void {
    // Simulate API call for demo purposes
    this.recentContent = this.getMockRecentContent();
    this.popularContent = this.getMockPopularContent();
  }

  private loadTrackStats(): void {
    // Simulate API call for demo purposes - updated to match Google Cloud Next topics
    this.trackStats = [
      { name: 'AI & Machine Learning', count: 42, color: '#4285F4' },
      { name: 'Data Analytics', count: 35, color: '#0F9D58' },
      { name: 'Cloud & DevOps', count: 31, color: '#EA4335' },
      { name: 'Serverless', count: 26, color: '#FBBC04' },
      { name: 'Security', count: 24, color: '#34A853' },
      { name: 'App Development', count: 18, color: '#5F6368' }
    ];
  }

  private loadTopics(): void {
    // Load topics from search component
    this.topics = [
      { id: 'apis', name: 'APIs' },
      { id: 'app-dev', name: 'App Dev' },
      { id: 'applied-ai', name: 'Applied AI' },
      { id: 'architecture', name: 'Architecture' },
      { id: 'business-intelligence', name: 'Business Intelligence' },
      { id: 'chrome', name: 'Chrome' },
      { id: 'compute', name: 'Compute' },
      { id: 'cost-optimization', name: 'Cost Optimization' },
      { id: 'data-analytics', name: 'Data Analytics' },
      { id: 'databases', name: 'Databases' },
      { id: 'firebase', name: 'Firebase' },
      { id: 'gender', name: 'Gender' },
      { id: 'kaggle', name: 'Kaggle' },
      { id: 'migration', name: 'Migration' },
      { id: 'multicloud', name: 'Multicloud' },
      { id: 'networking', name: 'Networking' },
      { id: 'security', name: 'Security' },
      { id: 'serverless', name: 'Serverless' },
      { id: 'storage', name: 'Storage' },
      { id: 'vertex-ai', name: 'Vertex AI' },
      { id: 'workspace', name: 'Workspace' }
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

  navigateToTopic(topicId: string): void {
    this.router.navigate(['/search'], { queryParams: { topic: topicId } });
  }

  getTopicIcon(tag: string): string {
    // Return appropriate Material icons based on tag
    const tagLower = tag.toLowerCase();
    
    if (tagLower.includes('ai') || tagLower.includes('ml') || tagLower.includes('gemini') || tagLower.includes('vertex')) {
      return 'smart_toy';
    } else if (tagLower.includes('data') || tagLower.includes('analytics') || tagLower.includes('bigquery')) {
      return 'insights';
    } else if (tagLower.includes('security') || tagLower.includes('zero trust') || tagLower.includes('iam')) {
      return 'security';
    } else if (tagLower.includes('serverless') || tagLower.includes('cloud functions')) {
      return 'functions';
    } else if (tagLower.includes('kubernetes') || tagLower.includes('gke') || tagLower.includes('container')) {
      return 'view_in_ar';
    } else if (tagLower.includes('firebase')) {
      return 'local_fire_department';
    } else if (tagLower.includes('cost') || tagLower.includes('finops')) {
      return 'savings';
    } else if (tagLower.includes('vector') || tagLower.includes('rag')) {
      return 'search';
    } else if (tagLower.includes('devops')) {
      return 'developer_board';
    }
    
    // Default icon
    return 'article';
  }

  // Mock data for demonstration - updated to match Google Cloud Next topics
  private getMockRecentContent(): FeaturedContent[] {
    return [
      {
        id: 'c1',
        title: 'Getting Started with Vertex AI: Building Your First GenAI Application',
        description: 'Learn how to build and deploy generative AI applications using Google Vertex AI',
        presenter: 'Sarah Chen',
        imageUrl: 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/vertexai.max-1000x1000.jpg',
        tags: ['AI', 'Vertex AI', 'GenAI'],
        date: '2023-06-15',
        views: 723
      },
      {
        id: 'c2',
        title: 'Building RAG Applications with Gemini and Vector Search',
        description: 'How to implement powerful Retrieval Augmented Generation using Google Cloud tools',
        presenter: 'Michael Rodriguez',
        imageUrl: 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Gemini_1.5_launch_blog.max-1300x1300.jpg',
        tags: ['Gemini', 'Vector Search', 'RAG'],
        date: '2023-06-12',
        views: 517
      },
      {
        id: 'c3',
        title: 'Scaling Cloud Functions with Event-Driven Architecture',
        description: 'Best practices for serverless computing and event-driven applications',
        presenter: 'David Kim',
        imageUrl: 'https://storage.googleapis.com/gweb-cloudblog-publish/images/cloud_functions_JDeWj0N.max-2600x2600.jpg',
        tags: ['Serverless', 'Cloud Functions', 'Event-Driven'],
        date: '2023-06-08',
        views: 489
      },
      {
        id: 'c4',
        title: 'Zero Trust Security for Google Cloud Workloads',
        description: 'Implementing comprehensive security for your cloud infrastructure',
        presenter: 'Emma Wilson',
        imageUrl: 'https://storage.googleapis.com/gweb-cloudblog-publish/images/Security_command_center.max-2000x2000.jpg',
        tags: ['Security', 'Zero Trust', 'IAM'],
        date: '2023-06-02',
        views: 556
      }
    ];
  }

  private getMockPopularContent(): FeaturedContent[] {
    return [
      {
        id: 'p1',
        title: 'BigQuery ML: Machine Learning for Data Analysts',
        description: 'Simplifying ML model training and deployment directly in BigQuery',
        presenter: 'Priya Patel',
        imageUrl: 'https://storage.googleapis.com/gweb-cloudblog-publish/images/BQ_ML.max-2000x2000.jpg',
        tags: ['BigQuery', 'ML', 'Data Analytics'],
        date: '2023-05-28',
        views: 876
      },
      {
        id: 'p2',
        title: 'Google Kubernetes Engine: Best Practices for Production',
        description: 'Advanced techniques for running secure, scalable GKE clusters in production',
        presenter: 'Alex Johnson',
        imageUrl: 'https://storage.googleapis.com/gweb-cloudblog-publish/images/GKE_enterprise_2022.max-2000x2000.jpg',
        tags: ['Kubernetes', 'GKE', 'DevOps'],
        date: '2023-05-15',
        views: 925
      },
      {
        id: 'p3',
        title: 'Optimizing Cloud Costs with FinOps Practices',
        description: 'Strategies to monitor, optimize, and control your cloud spending',
        presenter: 'David Kim',
        imageUrl: 'https://storage.googleapis.com/gweb-cloudblog-publish/images/cost_management.max-2000x2000.jpg',
        tags: ['FinOps', 'Cost Optimization', 'Cloud Management'],
        date: '2023-05-10',
        views: 753
      },
      {
        id: 'p4',
        title: 'Building with Firebase and Angular: Full Stack Development',
        description: 'Create modern web applications with Firebase and Angular integration',
        presenter: 'Michael Rodriguez',
        imageUrl: 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Firebase.max-1100x1100.jpg',
        tags: ['Firebase', 'Angular', 'Web Development'],
        date: '2023-05-05',
        views: 689
      }
    ];
  }
} 