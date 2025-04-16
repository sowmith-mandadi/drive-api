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
  // Make Math available to the template
  Math = Math;

  showFilters = false;
  searchQuery = '';
  selectedCarouselIndex = 0;
  selectedLatestIndex = 0;
  carouselAutoplayInterval: any;
  latestAutoplayInterval: any;
  sortDropdownOpen = false;

  // Current page indices for pagination
  latestPage = 0;
  recommendedPage = 0;

  // Items per page
  itemsPerPage = 3;

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
    const maxPage = Math.ceil(this.latestUpdates.length / this.itemsPerPage) - 1;
    this.latestPage = Math.min(this.latestPage + 1, maxPage);
    this.updateVisibleItems();
  }

  prevLatestSlide(): void {
    this.latestPage = Math.max(this.latestPage - 1, 0);
    this.updateVisibleItems();
  }

  toggleFilters(): void {
    this.showFilters = !this.showFilters;
    this.sortDropdownOpen = false;
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
    this.sortDropdownOpen = false;

    // Simple sorting implementation
    if (sortOption === 'newest') {
      this.latestUpdates.sort((a, b) => b.dateCreated.getTime() - a.dateCreated.getTime());
      this.recommendedContent.sort((a, b) => b.dateCreated.getTime() - a.dateCreated.getTime());
    } else if (sortOption === 'title') {
      this.latestUpdates.sort((a, b) => a.title.localeCompare(b.title));
      this.recommendedContent.sort((a, b) => a.title.localeCompare(b.title));
    }

    // Reset pagination and update visible items
    this.latestPage = 0;
    this.recommendedPage = 0;
    this.updateVisibleItems();
  }

  updateVisibleItems(): void {
    // Update visible latest updates based on current page
    const latestStart = this.latestPage * this.itemsPerPage;
    this.visibleLatestUpdates = this.latestUpdates.slice(latestStart, latestStart + this.itemsPerPage);

    // Update visible recommended content based on current page
    const recommendedStart = this.recommendedPage * this.itemsPerPage;
    this.visibleRecommended = this.recommendedContent.slice(recommendedStart, recommendedStart + this.itemsPerPage);
  }

  nextRecommendedSlide(): void {
    const maxPage = Math.ceil(this.recommendedContent.length / this.itemsPerPage) - 1;
    this.recommendedPage = Math.min(this.recommendedPage + 1, maxPage);
    this.updateVisibleItems();
  }

  prevRecommendedSlide(): void {
    this.recommendedPage = Math.max(this.recommendedPage - 1, 0);
    this.updateVisibleItems();
  }

  isNew(item: any): boolean {
    // Consider an item "new" if it's less than 7 days old
    const now = new Date();
    const itemDate = new Date(item.dateCreated);
    const diffTime = Math.abs(now.getTime() - itemDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 7;
  }

  isRecommended(item: any): boolean {
    // This could be based on a property from the backend
    // For now, let's mark some items as recommended based on some criteria
    return item.tags.some((tag: string) =>
      ['Recommended', 'Featured', 'Popular'].includes(tag)
    );
  }

  generateMockData(): void {
    // Generate latest updates that match the wireframe
    this.latestUpdates = [
      {
        id: 'lu1',
        title: 'Build the future of global carbon market analytics in Google Cloud',
        description: 'This session talks about two rising startups in carbon credit market, Perennial and Pachama, and their approach to building scalable solutions.',
        track: 'Cloud',
        tags: ['New', 'AI', 'Cloud', 'Data Analytics'],
        sessionType: 'workshop',
        learningLevel: 'intermediate',
        thumbnail: 'assets/content-thumbnails/carbon-analytics.jpg',
        presenters: [
          {
            id: 'p1',
            name: 'Sarah Chen',
            company: 'Google',
            title: 'Product Lead',
            photoUrl: 'assets/avatars/sarah-chen.jpg'
          }
        ],
        dateCreated: new Date('2023-04-10'),
        dateModified: new Date('2023-04-10'),
        status: 'published'
      },
      {
        id: 'lu2',
        title: 'Migrating Spark and Hadoop to Dataproc',
        description: 'Learn how Dataproc can support your hybrid multicloud strategy and help you meet your business goals for your big data workloads.',
        track: 'Big Data',
        tags: ['New', 'AI', 'Big Data', 'Advanced Technical'],
        sessionType: 'breakout',
        learningLevel: 'advanced',
        thumbnail: 'assets/content-thumbnails/dataproc.jpg',
        presenters: [
          {
            id: 'p3',
            name: 'David Kim',
            company: 'Google',
            title: 'Cloud Architect',
            photoUrl: 'assets/avatars/david-kim.jpg'
          }
        ],
        dateCreated: new Date('2023-04-03'),
        dateModified: new Date('2023-04-03'),
        status: 'published'
      },
      {
        id: 'lu3',
        title: 'Advanced productivity for data science',
        description: 'This session will explore how Vertex AI can help data scientists be more productive.',
        track: 'Data Analytics',
        tags: ['New', 'Data Analytics', 'Advanced Technical', 'BigQuery', 'Vertex AI'],
        sessionType: 'workshop',
        learningLevel: 'intermediate',
        thumbnail: 'assets/content-thumbnails/data-science.jpg',
        presenters: [
          {
            id: 'p4',
            name: 'Jennifer Lopez',
            company: 'Google',
            title: 'Data Science Lead',
            photoUrl: 'assets/avatars/jennifer-lopez.jpg'
          }
        ],
        dateCreated: new Date('2023-03-27'),
        dateModified: new Date('2023-03-27'),
        status: 'published'
      },
      {
        id: 'lu4',
        title: 'Introduction to BigQuery ML for predictive analytics',
        description: 'Learn how to use BigQuery ML to build machine learning models directly in BigQuery without moving your data.',
        track: 'Data Analytics',
        tags: ['New', 'Data Analytics', 'BigQuery', 'ML'],
        sessionType: 'workshop',
        learningLevel: 'beginner',
        thumbnail: 'assets/content-thumbnails/bigquery-ml.jpg',
        presenters: [
          {
            id: 'p5',
            name: 'Robert Chen',
            company: 'Google',
            title: 'BigQuery Specialist',
            photoUrl: 'assets/avatars/robert-chen.jpg'
          }
        ],
        dateCreated: new Date('2023-03-20'),
        dateModified: new Date('2023-03-22'),
        status: 'published'
      }
    ];

    // Generate recommended content that matches the wireframe
    this.recommendedContent = [
      {
        id: 'rc1',
        title: 'Founder series panel: How to get $100 million in funding',
        description: 'This session talks about how disruptive Generative AI startups secured over $100M in funding. Founders share their investment stories and insights.',
        track: 'Technology & Leadership',
        tags: ['Recommended', 'Technology & Leadership', 'Startup'],
        sessionType: 'panel',
        learningLevel: 'intermediate',
        thumbnail: 'assets/content-thumbnails/founder-series.jpg',
        presenters: [
          {
            id: 'p8',
            name: 'Thomas Lee',
            company: 'Venture Capital',
            title: 'Partner',
            photoUrl: 'assets/avatars/thomas-lee.jpg'
          }
        ],
        dateCreated: new Date('2023-04-01'),
        dateModified: new Date('2023-04-01'),
        status: 'published'
      },
      {
        id: 'rc2',
        title: 'How the cloud and digital packaging deliver elevated brand experiences',
        description: 'This session talks about how Germany\'s Koenig & Bauer, the world\'s oldest printing press manufacturer, teamed with Deloitte and Google Cloud to transform their business.',
        track: 'Technology',
        tags: ['Recommended', 'Technology', 'Manufacturing'],
        sessionType: 'breakout',
        learningLevel: 'intermediate',
        thumbnail: 'assets/content-thumbnails/packaging.jpg',
        presenters: [
          {
            id: 'p10',
            name: 'Koenig & Bauer',
            company: 'Manufacturing',
            title: 'CTO',
            photoUrl: 'assets/avatars/koenig.jpg'
          }
        ],
        dateCreated: new Date('2023-03-10'),
        dateModified: new Date('2023-03-10'),
        status: 'published'
      },
      {
        id: 'rc3',
        title: 'Useful applications of Imagen for image generation and customization',
        description: 'This session focuses on how to use Imagen on Vertex AI to assist in the creative process across multiple applications, such as product ads.',
        track: 'Technology',
        tags: ['Recommended', 'Technology', 'Vertex AI', 'App Dev'],
        sessionType: 'demo',
        learningLevel: 'advanced',
        thumbnail: 'assets/content-thumbnails/imagen.jpg',
        presenters: [
          {
            id: 'p11',
            name: 'Jessica Brown',
            company: 'Google',
            title: 'AI Specialist',
            photoUrl: 'assets/avatars/jessica-brown.jpg'
          }
        ],
        dateCreated: new Date('2023-03-12'),
        dateModified: new Date('2023-03-15'),
        status: 'published'
      },
      {
        id: 'rc4',
        title: 'Generative AI for enterprise knowledge management',
        description: 'Learn how to use generative AI to improve knowledge discovery and management within your organization.',
        track: 'AI & Machine Learning',
        tags: ['Recommended', 'GenAI', 'Enterprise'],
        sessionType: 'workshop',
        learningLevel: 'intermediate',
        thumbnail: 'assets/content-thumbnails/genai-km.jpg',
        presenters: [
          {
            id: 'p12',
            name: 'Mark Davis',
            company: 'Google',
            title: 'Solutions Architect',
            photoUrl: 'assets/avatars/mark-davis.jpg'
          }
        ],
        dateCreated: new Date('2023-03-08'),
        dateModified: new Date('2023-03-10'),
        status: 'published'
      }
    ];
  }
}
