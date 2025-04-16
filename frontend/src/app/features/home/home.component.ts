import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
import { MatBadgeModule } from '@angular/material/badge';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
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

import { Content, Filter } from '../../shared/models/content.model';
import { ContentService } from '../../core/services/content.service';
import { Subscription } from 'rxjs';

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
    MatProgressSpinnerModule,
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
export class HomeComponent implements OnInit, OnDestroy {
  // Make Math available to the template
  Math = Math;

  showFilters = false;
  searchQuery = '';
  selectedLatestIndex = 0;
  latestAutoplayInterval: any;
  sortDropdownOpen = false;

  // Current page indices for pagination
  latestPage = 0;
  recommendedPage = 0;

  // Items per page
  itemsPerPage = 3;

  // Content data
  latestUpdates: Content[] = [];
  visibleLatestUpdates: Content[] = [];
  recommendedContent: Content[] = [];
  visibleRecommended: Content[] = [];

  // Loading state
  loading = {
    latest: true,
    recommended: true
  };

  // Subscriptions to clean up
  private subscriptions: Subscription[] = [];

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

  constructor(
    private contentService: ContentService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadContent();
    this.startLatestAutoplay();
  }

  ngOnDestroy(): void {
    this.stopLatestAutoplay();

    // Clean up all subscriptions
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  loadContent(): void {
    // Load latest updates
    const latestSub = this.contentService.getLatestUpdates().subscribe({
      next: (data) => {
        this.latestUpdates = data;
        this.updateVisibleItems();
        this.loading.latest = false;
      },
      error: (err) => {
        console.error('Error loading latest updates:', err);
        this.loading.latest = false;
      }
    });

    // Load recommended content
    const recommendedSub = this.contentService.getRecommendedContent().subscribe({
      next: (data) => {
        this.recommendedContent = data;
        this.updateVisibleItems();
        this.loading.recommended = false;
      },
      error: (err) => {
        console.error('Error loading recommended content:', err);
        this.loading.recommended = false;
      }
    });

    // Store subscriptions for cleanup
    this.subscriptions.push(latestSub, recommendedSub);
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

    // Add class to body to prevent scrolling when filter panel is open
    if (this.showFilters) {
      document.body.classList.add('filters-open');
    } else {
      document.body.classList.remove('filters-open');
    }
  }

  clearAllFilters(): void {
    this.filters.forEach(filter => {
      filter.options.forEach(option => {
        option.selected = false;
      });
    });
    this.searchQuery = '';
    // Don't auto-apply filters, let the user click Apply button
  }

  applyFilters(): void {
    // Get selected filter values
    const selectedFilters = this.filters
      .map(filter => ({
        name: filter.name,
        selected: filter.options.filter(option => option.selected).map(option => option.value)
      }))
      .filter(filter => filter.selected.length > 0);

    console.log('Applied filters:', selectedFilters);
    console.log('Search query:', this.searchQuery);

    // Reset pagination when filters are applied
    this.latestPage = 0;
    this.recommendedPage = 0;

    // Update content
    this.updateFilteredContent(selectedFilters);

    // Close filter panel on mobile devices
    if (window.innerWidth <= 768) {
      this.showFilters = false;
    }
  }

  updateFilteredContent(selectedFilters: any[]): void {
    // Filter both content lists based on selected filters
    const filteredLatest = this.filterContent(this.latestUpdates, selectedFilters);
    const filteredRecommended = this.filterContent(this.recommendedContent, selectedFilters);

    // Update visible content
    this.latestUpdates = filteredLatest;
    this.recommendedContent = filteredRecommended;
    this.updateVisibleItems();
  }

  filterContent(items: Content[], selectedFilters: any[]): Content[] {
    if (selectedFilters.length === 0 && !this.searchQuery) {
      return items;
    }

    return items.filter(item => {
      // Apply search filter if query exists
      if (this.searchQuery &&
         !item.title.toLowerCase().includes(this.searchQuery.toLowerCase()) &&
         !item.description.toLowerCase().includes(this.searchQuery.toLowerCase()) &&
         !item.tags.some(tag => tag.toLowerCase().includes(this.searchQuery.toLowerCase()))) {
        return false;
      }

      // Check if item matches all selected filter criteria
      for (const filter of selectedFilters) {
        if (filter.name === 'Track' && filter.selected.length > 0) {
          const trackValue = item.track.toLowerCase().replace(/\s+/g, '-');
          if (!filter.selected.includes(trackValue)) {
            return false;
          }
        }

        if (filter.name === 'Session Type' && filter.selected.length > 0) {
          const sessionTypeValue = item.sessionType.toLowerCase().replace(/\s+/g, '-');
          if (!filter.selected.includes(sessionTypeValue)) {
            return false;
          }
        }

        if (filter.name === 'Learning Level' && filter.selected.length > 0) {
          const levelValue = item.learningLevel ? item.learningLevel.toLowerCase() : '';
          if (!filter.selected.includes(levelValue)) {
            return false;
          }
        }

        if (filter.name === 'Status' && filter.selected.length > 0) {
          if (!filter.selected.includes(item.status)) {
            return false;
          }
        }
      }

      return true;
    });
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
      this.latestUpdates.sort((a, b) => {
        const dateA = new Date(b.dateModified).getTime();
        const dateB = new Date(a.dateModified).getTime();
        return dateA - dateB;
      });

      this.recommendedContent.sort((a, b) => {
        const dateA = new Date(b.dateModified).getTime();
        const dateB = new Date(a.dateModified).getTime();
        return dateA - dateB;
      });
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

  isNew(item: Content): boolean {
    // Consider an item "new" if it's less than 7 days old
    const now = new Date();
    const itemDate = new Date(item.dateCreated);
    const diffTime = Math.abs(now.getTime() - itemDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 7;
  }

  isRecommended(item: Content): boolean {
    // Check if item has recommended flag or tag
    if (item.recommended) return true;
    return item.tags.some(tag =>
      tag.toLowerCase() === 'recommended' ||
      tag.toLowerCase() === 'featured' ||
      tag.toLowerCase() === 'popular'
    );
  }

  navigateToContent(contentId: string): void {
    this.router.navigate(['/content', contentId]);
  }
}
