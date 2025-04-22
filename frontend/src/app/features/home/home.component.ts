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
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MatTabsModule } from '@angular/material/tabs';
import { FormControl } from '@angular/forms';
import { debounceTime, distinctUntilChanged, switchMap, startWith, tap } from 'rxjs/operators';

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
    MatTabsModule,
    ReactiveFormsModule
  ],
  templateUrl: './home.component.html',
  styles: [`
    ::ng-deep .mat-mdc-chip-option {
      --mdc-chip-elevated-container-color: transparent !important;
      --mdc-chip-elevated-selected-container-color: transparent !important;
      --mdc-chip-elevated-selected-label-text-color: inherit !important;
      --mdc-chip-with-trailing-icon-trailing-icon-color: inherit !important;
      --mdc-chip-with-trailing-icon-selected-trailing-icon-color: inherit !important;
      --mdc-chip-elevated-selected-label-text-color: inherit !important;
      --mdc-chip-elevated-selected-state-layer-color: transparent !important;
      box-shadow: none !important;
      padding: 0 16px !important;
      height: 40px !important;
      border-radius: 20px !important;
    }

    ::ng-deep .mat-mdc-chip-option .mdc-evolution-chip__checkmark {
      display: none !important;
    }

    ::ng-deep .mat-mdc-standard-chip {
      background-color: transparent !important;
    }

    ::ng-deep .mat-mdc-chip-option-selected {
      background-color: #EBF5FF !important;
      color: #0057D2 !important;
      border-color: #0057D2 !important;
    }

    ::ng-deep .mat-mdc-chip-listbox {
      gap: 8px !important;
      display: flex !important;
      flex-wrap: wrap !important;
    }

    ::ng-deep .mdc-evolution-chip__action--primary {
      padding-left: 8px !important;
      padding-right: 8px !important;
    }

    ::ng-deep .mdc-evolution-chip__graphic {
      display: none !important;
    }

    ::ng-deep .mdc-evolution-chip__text-label {
      padding-left: 0 !important;
      padding-right: 0 !important;
      font-size: 14px !important;
    }

    ::ng-deep .mat-icon {
      font-size: 20px !important;
      height: 20px !important;
      width: 20px !important;
      line-height: 20px !important;
    }

    .cursor-pointer:hover {
      background-color: #F5F7FA;
    }

    .border-primary {
      border-color: #D2E3FC !important;
    }

    .bg-primary-light {
      background-color: #D2E3FC !important;
    }

    .text-primary {
      color: #1967D2 !important;
    }

    .selected-chip {
      background-color: #D2E3FC !important;
      color: #1967D2 !important;
      border-color: #D2E3FC !important;
    }
  `]
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
      name: 'Event',
      options: [
        { value: 'conferences', label: 'Conferences', selected: false, count: 0 },
        { value: 'webinars', label: 'Webinars', selected: false, count: 0 },
        { value: 'workshops', label: 'Workshops', selected: false, count: 0 }
      ],
      expanded: false
    },
    {
      name: 'Topic',
      options: [
        { value: 'ai-ml', label: 'AI & Machine Learning', selected: false, count: 0 },
        { value: 'cloud-infrastructure', label: 'Cloud Infrastructure', selected: false, count: 0 },
        { value: 'data-analytics', label: 'Data & Analytics', selected: false, count: 0 },
        { value: 'app-modernization', label: 'App Modernization', selected: false, count: 0 },
        { value: 'security', label: 'Security', selected: false, count: 0 }
      ],
      expanded: false
    },
    {
      name: 'Industry',
      options: [
        { value: 'financial-services', label: 'Financial Services', selected: false, count: 0 },
        { value: 'healthcare', label: 'Healthcare', selected: false, count: 0 },
        { value: 'retail', label: 'Retail', selected: false, count: 0 },
        { value: 'manufacturing', label: 'Manufacturing', selected: false, count: 0 },
        { value: 'government', label: 'Government', selected: false, count: 0 }
      ],
      expanded: false
    },
    {
      name: 'Content Type',
      options: [
        { value: 'article', label: 'Article', selected: false, count: 0 },
        { value: 'video', label: 'Video', selected: false, count: 0 },
        { value: 'whitepaper', label: 'Whitepaper', selected: false, count: 0 },
        { value: 'demo', label: 'Demo', selected: false, count: 0 },
        { value: 'code-sample', label: 'Code Sample', selected: false, count: 0 }
      ],
      expanded: false
    },
    {
      name: 'Account Type',
      options: [
        { value: 'personal', label: 'Personal', selected: false, count: 0 },
        { value: 'business', label: 'Business', selected: false, count: 0 },
        { value: 'enterprise', label: 'Enterprise', selected: false, count: 0 }
      ],
      expanded: false
    },
    {
      name: 'Products',
      options: [
        { value: 'compute-engine', label: 'Compute Engine', selected: false, count: 0 },
        { value: 'cloud-storage', label: 'Cloud Storage', selected: false, count: 0 },
        { value: 'bigquery', label: 'BigQuery', selected: false, count: 0 },
        { value: 'kubernetes', label: 'Kubernetes', selected: false, count: 0 },
        { value: 'vertex-ai', label: 'Vertex AI', selected: false, count: 0 }
      ],
      expanded: false
    },
    {
      name: 'Region',
      options: [
        { value: 'north-america', label: 'North America', selected: false, count: 0 },
        { value: 'europe', label: 'Europe', selected: false, count: 0 },
        { value: 'asia-pacific', label: 'Asia Pacific', selected: false, count: 0 },
        { value: 'latin-america', label: 'Latin America', selected: false, count: 0 }
      ],
      expanded: false
    },
    {
      name: 'Tags',
      options: [
        { value: 'ai', label: 'AI', selected: false, count: 0 },
        { value: 'apis', label: 'APIs', selected: false, count: 0 },
        { value: 'app-dev', label: 'App Dev', selected: false, count: 0 },
        { value: 'applied-ai', label: 'Applied AI', selected: false, count: 0 },
        { value: 'architecture', label: 'Architecture', selected: false, count: 0 },
        { value: 'business-intelligence', label: 'Business Intelligence', selected: false, count: 0 },
        { value: 'chrome', label: 'Chrome', selected: false, count: 0 },
        { value: 'compute', label: 'Compute', selected: false, count: 0 },
        { value: 'cost-optimization', label: 'Cost Optimization', selected: false, count: 0 }
      ],
      expanded: true
    }
  ];

  // Live search
  searchControl = new FormControl('');
  searchResults: Content[] = [];
  isSearching = false;
  searchLoading = false;

  // For managing abstract expansions in search results
  expandedAbstracts: { [key: number]: boolean } = {};
  abstractMaxLength = 150;

  constructor(
    private contentService: ContentService,
    private router: Router
  ) {}

  isNewContent(item: Content): boolean {
    // First check if the item has isNew flag set
    if (item.isNew) return true;

    // Otherwise, consider an item "new" if it's less than 7 days old
    const now = new Date();
    const itemDate = new Date(item.dateCreated);
    const diffTime = Math.abs(now.getTime() - itemDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 7;
  }

  hasAiSummary(item: Content): boolean {
    // Check if item has an AI summary or an AI tag
    return !!item.aiSummary || item.tags?.some(tag => tag.includes('AI'));
  }

  getAbstractToShow(item: Content, index: number): string {
    if (!item.abstract) return item.description;
    if (this.expandedAbstracts[index] || item.abstract.length <= this.abstractMaxLength) {
      return item.abstract;
    }
    return item.abstract.substring(0, this.abstractMaxLength) + '...';
  }

  shouldShowMoreButton(item: Content, index: number): boolean {
    const text = item.abstract || item.description;
    return !!(text && text.length > this.abstractMaxLength);
  }

  toggleShowMore(event: Event, index: number): void {
    event.stopPropagation(); // Prevent navigation
    this.expandedAbstracts[index] = !this.expandedAbstracts[index];
  }

  getAssetIcon(assetType: string): string {
    switch(assetType.toLowerCase()) {
      case 'pdf':
        return 'picture_as_pdf';
      case 'slide':
        return 'slideshow';
      case 'video':
        return 'videocam';
      case 'demo':
        return 'code';
      case 'github':
        return 'code';
      case 'youtube':
        return 'smart_display';
      case 'notebook':
        return 'book';
      default:
        return 'insert_drive_file';
    }
  }

  ngOnInit(): void {
    this.loadContent();
    this.startLatestAutoplay();
    // Live search subscription
    const searchSub = this.searchControl.valueChanges.pipe(
      startWith(''),
      debounceTime(300),
      distinctUntilChanged(),
      tap(query => {
        this.isSearching = !!query && query.trim().length > 0;
        this.searchLoading = !!query && query.trim().length > 0;
      }),
      switchMap(query => {
        if (!query || query.trim() === '') {
          this.searchResults = [];
          this.searchLoading = false;
          return [];
        }
        // Placeholder: search all content (latest + recommended union, deduped by id)
        const allContent = [...this.latestUpdates, ...this.recommendedContent].filter((v, i, a) => a.findIndex(t => t.id === v.id) === i);
        // Simulate async search (replace with API call later)
        return this.contentService.searchContent({ query, page: 0, size: 12 }).pipe(
          tap(() => this.searchLoading = false),
          tap(result => this.searchResults = result.items)
        );
      })
    ).subscribe();
    this.subscriptions.push(searchSub);
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
    // First check if the item has isNew flag set
    if (item.isNew) return true;

    // Otherwise, consider an item "new" if it's less than 7 days old
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

  getFilteredTags(item: Content): string[] {
    // Filter out any recommended-related tags for the recommended section
    return item.tags.filter(tag =>
      tag.toLowerCase() !== 'recommended' &&
      tag.toLowerCase() !== 'featured' &&
      tag.toLowerCase() !== 'popular' &&
      tag.toLowerCase() !== 'new'
    );
  }

  navigateToContent(contentId: string): void {
    this.router.navigate(['/content', contentId]);
  }
}
