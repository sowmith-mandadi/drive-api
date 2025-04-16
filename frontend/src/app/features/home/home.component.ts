import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
import { MatBadgeModule } from '@angular/material/badge';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule } from '@angular/forms';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MatTabsModule } from '@angular/material/tabs';

interface Content {
  id: string;
  title: string;
  description: string;
  track: string;
  tags: string[];
  sessionType: string;
  sessionDate?: string;
  thumbnail?: string;
  learningLevel?: string;
  topic?: string;
  presenters: Presenter[];
  dateCreated: Date;
  dateModified: Date;
  status: 'draft' | 'review' | 'approved' | 'published' | 'rejected';
}

interface Presenter {
  id: string;
  name: string;
  company: string;
  title?: string;
  photoUrl?: string;
}

interface Filter {
  name: string;
  options: FilterOption[];
  expanded: boolean;
}

interface FilterOption {
  value: string;
  label: string;
  selected: boolean;
  count: number;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatDividerModule,
    MatChipsModule,
    MatBadgeModule,
    MatProgressBarModule,
    MatSidenavModule,
    MatCheckboxModule,
    MatExpansionModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatListModule,
    MatTooltipModule,
    MatMenuModule,
    MatTabsModule
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  showFilters = false;
  searchQuery = '';
  selectedCarouselIndex = 0;
  selectedLatestIndex = 0;
  carouselAutoplayInterval: any;
  latestAutoplayInterval: any;

  // Featured content for carousel
  featuredContent = [
    {
      id: 'f1',
      title: 'Google Cloud Next Keynote',
      description: 'Join us for the opening keynote to hear about the latest innovations in cloud technology',
      image: 'assets/content-thumbnails/default-thumbnail.jpg',
      track: 'Keynote',
      status: 'published',
      tags: ['Cloud', 'Innovation', 'Keynote'],
      presenters: [
        {
          id: 'p1',
          name: 'Sundar Pichai',
          company: 'Google',
          title: 'CEO'
        }
      ],
      dateModified: new Date('2023-06-15')
    },
    {
      id: 'f2',
      title: 'AI Summit',
      description: 'Explore the latest in artificial intelligence and machine learning with hands-on workshops and expert speakers',
      image: 'assets/content-thumbnails/default-thumbnail.jpg',
      track: 'AI & Machine Learning',
      status: 'approved',
      tags: ['AI', 'ML', 'Workshops'],
      presenters: [
        {
          id: 'p2',
          name: 'Sarah Chen',
          company: 'Google',
          title: 'AI/ML Product Lead'
        },
        {
          id: 'p3',
          name: 'Michael Johnson',
          company: 'Google',
          title: 'Senior Engineer'
        }
      ],
      dateModified: new Date('2023-06-10')
    },
    {
      id: 'f3',
      title: 'Developer Workshops',
      description: 'Hands-on sessions for developers to build with Google Cloud and learn best practices from experts',
      image: 'assets/content-thumbnails/default-thumbnail.jpg',
      track: 'Developer Tools',
      status: 'review',
      tags: ['Dev Tools', 'Best Practices', 'Hands-on'],
      presenters: [
        {
          id: 'p4',
          name: 'David Kim',
          company: 'Google',
          title: 'Cloud Architect'
        }
      ],
      dateModified: new Date('2023-06-08')
    },
    {
      id: 'f4',
      title: 'Cloud Security Summit',
      description: 'Deep-dive into the latest security features and best practices for protecting your cloud environment',
      image: 'assets/content-thumbnails/default-thumbnail.jpg',
      track: 'Security',
      status: 'published',
      tags: ['Security', 'Best Practices', 'Cloud'],
      presenters: [
        {
          id: 'p5',
          name: 'Jennifer Lopez',
          company: 'Google',
          title: 'Security Specialist'
        },
        {
          id: 'p6',
          name: 'Mark Davis',
          company: 'Google',
          title: 'Solutions Architect'
        }
      ],
      dateModified: new Date('2023-06-05')
    },
    {
      id: 'f5',
      title: 'Data & Analytics',
      description: 'Learn how to leverage BigQuery, Looker, and other Google Cloud data tools to drive insights',
      image: 'assets/content-thumbnails/default-thumbnail.jpg',
      track: 'Data & Analytics',
      status: 'approved',
      tags: ['BigQuery', 'Looker', 'Analytics'],
      presenters: [
        {
          id: 'p7',
          name: 'Robert Chen',
          company: 'Google',
          title: 'BigQuery Specialist'
        }
      ],
      dateModified: new Date('2023-06-01')
    }
  ];

  // Filter configurations
  filters: Filter[] = [
    {
      name: 'Track',
      options: [
        { value: 'ai-ml', label: 'AI & Machine Learning', selected: false, count: 28 },
        { value: 'cloud-infrastructure', label: 'Cloud Infrastructure', selected: false, count: 35 },
        { value: 'data-analytics', label: 'Data & Analytics', selected: false, count: 22 },
        { value: 'application-modernization', label: 'App Modernization', selected: false, count: 19 },
        { value: 'security', label: 'Security', selected: false, count: 16 }
      ],
      expanded: true
    },
    {
      name: 'Session Type',
      options: [
        { value: 'keynote', label: 'Keynote', selected: false, count: 5 },
        { value: 'workshop', label: 'Workshop', selected: false, count: 32 },
        { value: 'breakout', label: 'Breakout Session', selected: false, count: 48 },
        { value: 'panel', label: 'Panel Discussion', selected: false, count: 12 },
        { value: 'demo', label: 'Demo', selected: false, count: 28 }
      ],
      expanded: false
    },
    {
      name: 'Learning Level',
      options: [
        { value: 'beginner', label: 'Beginner', selected: false, count: 35 },
        { value: 'intermediate', label: 'Intermediate', selected: false, count: 54 },
        { value: 'advanced', label: 'Advanced', selected: false, count: 36 }
      ],
      expanded: false
    },
    {
      name: 'Status',
      options: [
        { value: 'draft', label: 'Draft', selected: false, count: 12 },
        { value: 'review', label: 'In Review', selected: false, count: 24 },
        { value: 'approved', label: 'Approved', selected: false, count: 45 },
        { value: 'published', label: 'Published', selected: false, count: 44 }
      ],
      expanded: false
    }
  ];

  // Latest updates data (mock)
  latestUpdates: Content[] = [];
  visibleLatestUpdates: Content[] = [];

  // Recommended content data (mock)
  recommendedContent: Content[] = [];
  visibleRecommended: Content[] = [];

  constructor() {}

  ngOnInit(): void {
    this.generateMockData();
    this.updateVisibleItems();
    this.startCarouselAutoplay();
    this.startLatestAutoplay();
  }

  ngOnDestroy(): void {
    this.stopCarouselAutoplay();
    this.stopLatestAutoplay();
  }

  startCarouselAutoplay(): void {
    this.carouselAutoplayInterval = setInterval(() => {
      this.nextCarouselSlide();
    }, 5000);
  }

  stopCarouselAutoplay(): void {
    if (this.carouselAutoplayInterval) {
      clearInterval(this.carouselAutoplayInterval);
    }
  }

  startLatestAutoplay(): void {
    this.latestAutoplayInterval = setInterval(() => {
      this.nextLatestSlide();
    }, 6000);
  }

  stopLatestAutoplay(): void {
    if (this.latestAutoplayInterval) {
      clearInterval(this.latestAutoplayInterval);
    }
  }

  onCarouselTabChange(index: number): void {
    this.selectedCarouselIndex = index;
    this.stopCarouselAutoplay();
    this.startCarouselAutoplay();
  }

  nextCarouselSlide(): void {
    this.selectedCarouselIndex = (this.selectedCarouselIndex + 1) % this.featuredContent.length;
  }

  prevCarouselSlide(): void {
    this.selectedCarouselIndex = (this.selectedCarouselIndex - 1 + this.featuredContent.length) % this.featuredContent.length;
  }

  nextLatestSlide(): void {
    this.selectedLatestIndex = (this.selectedLatestIndex + 1) % this.latestUpdates.length;
  }

  prevLatestSlide(): void {
    this.selectedLatestIndex = (this.selectedLatestIndex - 1 + this.latestUpdates.length) % this.latestUpdates.length;
  }

  toggleFilters(): void {
    this.showFilters = !this.showFilters;
  }

  clearAllFilters(): void {
    this.filters.forEach(filter => {
      filter.options.forEach(option => {
        option.selected = false;
      });
    });
    this.searchQuery = '';
    this.applyFilters();
  }

  applyFilters(): void {
    // In a real implementation, this would filter the actual data using the API
    const selectedFilters = this.filters
      .map(filter => ({
        name: filter.name,
        selected: filter.options.filter(option => option.selected).map(option => option.label)
      }))
      .filter(filter => filter.selected.length > 0);

    console.log('Applied filters:', selectedFilters);
    console.log('Search query:', this.searchQuery);
    
    // If there's an HTTP call to the search API, it should use the correct endpoint:
    // Instead of '/api/search' it should be '/api/content/search'
  }

  saveFilterPreset(): void {
    // In a real implementation, this would save the current filter configuration
    console.log('Filter preset saved');
  }

  sortBy(sortOption: string): void {
    console.log('Sorting by:', sortOption);
    // Implement actual sorting logic here
  }

  updateVisibleItems(): void {
    // For now, just show all items
    this.visibleLatestUpdates = this.latestUpdates.slice(0, 3);
    this.visibleRecommended = this.recommendedContent.slice(0, 3);
  }

  generateMockData(): void {
    // Generate mock latest updates
    this.latestUpdates = [
      {
        id: 'lu1',
        title: 'Building Enterprise AI Solutions with Gemini',
        description: 'Learn how to leverage Google\'s Gemini models to build enterprise-grade AI solutions that can transform your business processes.',
        track: 'AI & Machine Learning',
        tags: ['Gemini', 'Enterprise AI', 'LLM', 'RAG'],
        sessionType: 'workshop',
        learningLevel: 'intermediate',
        thumbnail: 'assets/content-thumbnails/ai-solutions.jpg',
        presenters: [
          {
            id: 'p1',
            name: 'Sarah Chen',
            company: 'Google',
            title: 'AI/ML Product Lead',
            photoUrl: 'assets/avatars/sarah-chen.jpg'
          },
          {
            id: 'p2',
            name: 'Michael Johnson',
            company: 'Google',
            title: 'Senior Engineer',
            photoUrl: 'assets/avatars/michael-johnson.jpg'
          }
        ],
        dateCreated: new Date('2023-06-12'),
        dateModified: new Date('2023-06-15'),
        status: 'review'
      },
      {
        id: 'lu2',
        title: 'Scaling Kubernetes in Production: Lessons Learned',
        description: 'Discover best practices for scaling Kubernetes clusters in production environments, based on real-world experiences from Google Cloud customers.',
        track: 'Cloud Infrastructure',
        tags: ['Kubernetes', 'GKE', 'DevOps', 'Scalability'],
        sessionType: 'breakout',
        learningLevel: 'advanced',
        thumbnail: 'assets/content-thumbnails/kubernetes.jpg',
        presenters: [
          {
            id: 'p3',
            name: 'David Kim',
            company: 'Google',
            title: 'Cloud Architect',
            photoUrl: 'assets/avatars/david-kim.jpg'
          }
        ],
        dateCreated: new Date('2023-06-10'),
        dateModified: new Date('2023-06-14'),
        status: 'approved'
      },
      {
        id: 'lu3',
        title: 'BigQuery ML: From Data to Predictions',
        description: 'A comprehensive guide to implementing machine learning models directly in BigQuery, enabling data teams to build and deploy ML solutions without moving data.',
        track: 'Data & Analytics',
        tags: ['BigQuery', 'ML', 'Data Analytics'],
        sessionType: 'workshop',
        learningLevel: 'intermediate',
        thumbnail: 'assets/content-thumbnails/bigquery-ml.jpg',
        presenters: [
          {
            id: 'p4',
            name: 'Jennifer Lopez',
            company: 'Google',
            title: 'Data Science Lead',
            photoUrl: 'assets/avatars/jennifer-lopez.jpg'
          },
          {
            id: 'p5',
            name: 'Robert Chen',
            company: 'Google',
            title: 'BigQuery Specialist',
            photoUrl: 'assets/avatars/robert-chen.jpg'
          }
        ],
        dateCreated: new Date('2023-06-08'),
        dateModified: new Date('2023-06-13'),
        status: 'published'
      }
    ];

    // Generate mock recommended content
    this.recommendedContent = [
      {
        id: 'rc1',
        title: 'Vertex AI: End-to-End ML Development',
        description: 'A comprehensive overview of Vertex AI and how it can streamline your machine learning development lifecycle.',
        track: 'AI & Machine Learning',
        tags: ['Vertex AI', 'ML Ops', 'AutoML'],
        sessionType: 'workshop',
        learningLevel: 'intermediate',
        thumbnail: 'assets/content-thumbnails/vertex-ai.jpg',
        presenters: [
          {
            id: 'p8',
            name: 'Thomas Lee',
            company: 'Google',
            title: 'ML Engineer',
            photoUrl: 'assets/avatars/thomas-lee.jpg'
          },
          {
            id: 'p9',
            name: 'Sophia Williams',
            company: 'Google',
            title: 'Product Manager',
            photoUrl: 'assets/avatars/sophia-williams.jpg'
          }
        ],
        dateCreated: new Date('2023-05-28'),
        dateModified: new Date('2023-06-02'),
        status: 'published'
      },
      {
        id: 'rc2',
        title: 'Spanner: Building Global-Scale Applications',
        description: 'Learn how to design and implement applications using Cloud Spanner for global scalability, strong consistency, and high availability.',
        track: 'Data & Analytics',
        tags: ['Spanner', 'Databases', 'Global Scale'],
        sessionType: 'breakout',
        learningLevel: 'advanced',
        thumbnail: 'assets/content-thumbnails/spanner.jpg',
        presenters: [
          {
            id: 'p10',
            name: 'Rajiv Patel',
            company: 'Google',
            title: 'Database Engineer',
            photoUrl: 'assets/avatars/rajiv-patel.jpg'
          }
        ],
        dateCreated: new Date('2023-05-25'),
        dateModified: new Date('2023-05-30'),
        status: 'approved'
      },
      {
        id: 'rc3',
        title: 'Cloud Asset Inventory: Track Your Resources',
        description: 'Discover how to use Cloud Asset Inventory to track, monitor, and analyze all your Google Cloud and Anthos assets.',
        track: 'Security',
        tags: ['Asset Management', 'Compliance', 'Inventory'],
        sessionType: 'demo',
        learningLevel: 'beginner',
        thumbnail: 'assets/content-thumbnails/asset-inventory.jpg',
        presenters: [
          {
            id: 'p11',
            name: 'Jessica Brown',
            company: 'Google',
            title: 'Security Specialist',
            photoUrl: 'assets/avatars/jessica-brown.jpg'
          },
          {
            id: 'p12',
            name: 'Mark Davis',
            company: 'Google',
            title: 'Solutions Architect',
            photoUrl: 'assets/avatars/mark-davis.jpg'
          }
        ],
        dateCreated: new Date('2023-05-20'),
        dateModified: new Date('2023-05-28'),
        status: 'review'
      }
    ];
  }
}
