import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, FormControl } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { catchError, of } from 'rxjs';
import { RouterModule } from '@angular/router';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatBadgeModule } from '@angular/material/badge';
import { MatTooltipModule } from '@angular/material/tooltip';

interface Asset {
  type: string;
  name: string;
  url: string;
}

interface ContentItem {
  id: string;
  title: string;
  tags: string[];
  abstract: string;
  type: string;
  track: string;
  author: string;
  dateModified: string;
  dateCreated: string;
  thumbUrl?: string;
  assets?: Asset[];
  priority?: boolean;
  recommended?: boolean;
  bookmarked?: boolean;
}

interface SearchResult {
  items: ContentItem[];
  total: number;
}

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
    MatChipsModule,
    MatCheckboxModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatDividerModule,
    MatExpansionModule,
    MatBadgeModule,
    MatTooltipModule
  ],
  template: `
    <div class="search-container">
      <div class="search-form-container">
        <div class="search-row">
          <div class="search-box">
            <div class="search-icon">
              <mat-icon>search</mat-icon>
            </div>
            <input
              type="text"
              formControlName="query"
              placeholder="AI"
              class="search-input"
              [formControl]="queryControl"
            >
            <button
              *ngIf="searchForm.get('query')?.value"
              class="clear-button"
              type="button"
              (click)="clearSearch()"
            >
              <mat-icon>close</mat-icon>
            </button>
          </div>

          <div class="sort-filters-wrapper">
            <div class="sort-by-button" (click)="toggleSortDropdown()">
              <span>Sort by</span>
              <span class="sort-value">{{ sortField | titlecase }}</span>
              <div class="sort-dropdown" *ngIf="sortDropdownOpen">
                <div
                  class="sort-option"
                  [class.active]="sortField === 'newest'"
                  (click)="setSortField('newest')"
                >
                  Newest
                </div>
                <div
                  class="sort-option"
                  [class.active]="sortField === 'relevance'"
                  (click)="setSortField('relevance')"
                >
                  Relevance
                </div>
                <div
                  class="sort-option"
                  [class.active]="sortField === 'title'"
                  (click)="setSortField('title')"
                >
                  Title
                </div>
              </div>
            </div>

            <button type="button" class="filters-button">
              <mat-icon>tune</mat-icon>
              <span>Filters</span>
            </button>
          </div>
        </div>

        <div class="showing-results" *ngIf="results().length > 0">
          <p>Showing results for "{{ searchForm.get('query')?.value || 'AI' }}"</p>
        </div>
      </div>

      <div class="loading-spinner" *ngIf="isLoading()">
        <mat-spinner diameter="36" color="accent"></mat-spinner>
      </div>

      <div class="search-results" *ngIf="!isLoading()">
        <div class="no-results" *ngIf="results().length === 0 && hasSearched()">
          <mat-icon>search_off</mat-icon>
          <h3>No results found</h3>
          <p>Try adjusting your search or filter criteria</p>
        </div>

        <div class="results-grid" *ngIf="results().length > 0">
          <div class="result-card" *ngFor="let item of results(); let i = index">
            <button class="bookmark-button" [class.bookmarked]="item.bookmarked">
              <mat-icon>{{ item.bookmarked ? 'bookmark' : 'bookmark_border' }}</mat-icon>
            </button>

            <h3 class="card-title">{{ item.title }}</h3>

            <div class="card-labels">
              <div class="label priority" *ngIf="item.priority">Priority</div>
              <div class="label recommended" *ngIf="item.recommended">Recommended</div>
              <div class="label new" *ngIf="item.type === 'New'">New</div>
            </div>

            <div class="ai-summary" *ngIf="item.type === 'AI Summary'">
              <div class="ai-icon">
                <mat-icon>smart_toy</mat-icon>
              </div>
              <span>AI Summary</span>
            </div>

            <div class="card-abstract">
              <p>
                {{ getAbstractToShow(item, i) }}
              </p>
              <button
                *ngIf="shouldShowMoreButton(item, i)"
                type="button"
                class="show-more-btn"
                (click)="toggleShowMore(i)">
                {{ expandedAbstracts[i] ? 'Show less' : 'Show more' }}
              </button>
            </div>

            <div class="card-assets" *ngIf="item.assets && item.assets.length > 0">
              <div class="assets-label">Assets</div>
              <div class="assets-list">
                <a
                  *ngFor="let asset of item.assets"
                  [href]="asset.url"
                  target="_blank"
                  class="asset-link">
                  <div class="asset-icon-wrapper" [class]="asset.type.toLowerCase()">
                    <mat-icon>{{ getAssetIcon(asset.type) }}</mat-icon>
                  </div>
                  <span class="asset-label">{{ asset.type }}</span>
                  <mat-icon *ngIf="asset.type === 'Slide'" class="external-icon">open_in_new</mat-icon>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
      background-color: #f8f9fa;
      min-height: 100vh;
      font-family: 'Google Sans', 'Roboto', sans-serif;
    }

    .search-container {
      max-width: 1280px;
      margin: 0 auto;
      padding: 16px 24px;
    }

    .search-form-container {
      margin-bottom: 24px;
    }

    .search-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      gap: 16px;
    }

    .search-box {
      position: relative;
      display: flex;
      align-items: center;
      flex: 1;
      height: 46px;
      border: 1px solid #dadce0;
      border-radius: 24px;
      background-color: #fff;
      transition: box-shadow 0.2s, border-color 0.2s;
    }

    .search-box:focus-within {
      box-shadow: 0 1px 6px rgba(32, 33, 36, 0.18);
      border-color: rgba(223, 225, 229, 0);
    }

    .search-icon {
      color: #5f6368;
      margin-left: 16px;
    }

    .search-input {
      flex: 1;
      border: none;
      outline: none;
      font-size: 16px;
      color: #202124;
      background: transparent;
      padding: 0 16px;
      height: 100%;
    }

    .clear-button {
      background: none;
      border: none;
      color: #5f6368;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      width: 46px;
      height: 46px;
    }

    .sort-filters-wrapper {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
    }

    .sort-by-button {
      position: relative;
      display: flex;
      align-items: center;
      gap: 8px;
      height: 36px;
      padding: 0 12px;
      border: 1px solid #dadce0;
      border-radius: 18px;
      background-color: #fff;
      font-size: 14px;
      color: #5f6368;
      cursor: pointer;
    }

    .sort-by-button:hover {
      background-color: #f8f9fa;
    }

    .sort-value {
      color: #202124;
      font-weight: 500;
    }

    .sort-dropdown {
      position: absolute;
      top: 100%;
      left: 0;
      min-width: 180px;
      margin-top: 4px;
      background-color: #fff;
      border-radius: 4px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
      z-index: 10;
      overflow: hidden;
    }

    .sort-option {
      padding: 12px 16px;
      font-size: 14px;
      color: #202124;
      cursor: pointer;
      transition: background-color 0.2s;
    }

    .sort-option:hover {
      background-color: #f1f3f4;
    }

    .sort-option.active {
      background-color: #e8f0fe;
      color: #1a73e8;
      font-weight: 500;
    }

    .filters-button {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background-color: #fff;
      border: 1px solid #dadce0;
      border-radius: 18px;
      height: 36px;
      padding: 0 16px;
      color: #5f6368;
      font-size: 14px;
      cursor: pointer;
      transition: background-color 0.2s;
      outline: none;
    }

    .filters-button:hover {
      background-color: #f8f9fa;
    }

    .filters-button mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }

    .showing-results {
      color: #5f6368;
      font-size: 14px;
      margin-bottom: 16px;
    }

    .showing-results p {
      margin: 0;
    }

    .no-results {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 48px 0;
      text-align: center;
      color: #5f6368;
    }

    .no-results mat-icon {
      font-size: 48px;
      height: 48px;
      width: 48px;
      margin-bottom: 16px;
      color: #dadce0;
    }

    .no-results h3 {
      font-size: 20px;
      font-weight: 500;
      margin-bottom: 8px;
      color: #202124;
    }

    .no-results p {
      font-size: 14px;
      margin: 0;
    }

    .results-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
      gap: 24px;
      margin-bottom: 32px;
    }

    .result-card {
      position: relative;
      background-color: #fff;
      border-radius: 8px;
      border: 1px solid #dadce0;
      padding: 24px;
      transition: box-shadow 0.2s;
    }

    .result-card:hover {
      box-shadow: 0 1px 6px rgba(0, 0, 0, 0.1);
    }

    .bookmark-button {
      position: absolute;
      top: 24px;
      right: 24px;
      background: none;
      border: none;
      cursor: pointer;
      padding: 4px;
      color: #dadce0;
      transition: color 0.2s;
    }

    .bookmark-button:hover {
      color: #5f6368;
    }

    .bookmark-button.bookmarked {
      color: #1a73e8;
    }

    .card-title {
      font-size: 20px;
      font-weight: 500;
      color: #202124;
      margin: 0 0 16px;
      padding-right: 32px;
      line-height: 1.3;
      letter-spacing: -0.2px;
    }

    .card-labels {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 16px;
    }

    .label {
      display: inline-flex;
      align-items: center;
      height: 24px;
      font-size: 12px;
      padding: 0 12px;
      border-radius: 12px;
      letter-spacing: 0.2px;
      font-weight: 500;
    }

    .priority {
      background-color: #f1f3f4;
      color: #5f6368;
    }

    .recommended {
      background-color: #e6f4ea;
      color: #137333;
    }

    .new {
      background-color: #e8f0fe;
      color: #1a73e8;
    }

    .ai-summary {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 16px;
      color: #1a73e8;
      font-size: 14px;
    }

    .ai-icon {
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .card-abstract {
      font-size: 14px;
      color: #5f6368;
      margin-bottom: 16px;
      line-height: 1.5;
    }

    .card-abstract p {
      margin: 0 0 8px;
    }

    .show-more-btn {
      background: none;
      border: none;
      padding: 0;
      color: #1a73e8;
      font-size: 14px;
      cursor: pointer;
      font-weight: 500;
    }

    .show-more-btn:hover {
      text-decoration: underline;
    }

    .card-assets {
      border-top: 1px solid #f1f3f4;
      padding-top: 16px;
    }

    .assets-label {
      font-size: 12px;
      color: #5f6368;
      margin-bottom: 12px;
    }

    .assets-list {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }

    .asset-link {
      display: flex;
      align-items: center;
      text-decoration: none;
      gap: 8px;
      color: #1a73e8;
      font-size: 14px;
      font-weight: 500;
    }

    .asset-link:hover {
      text-decoration: underline;
    }

    .asset-icon-wrapper {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      border-radius: 4px;
      color: #fff;
    }

    .asset-icon-wrapper.slide {
      background-color: #fbbc04;
    }

    .asset-icon-wrapper.pdf {
      background-color: #ea4335;
    }

    .asset-icon-wrapper.youtube {
      background-color: #ea4335;
    }

    .asset-icon-wrapper mat-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
    }

    .asset-label {
      color: #1a73e8;
    }

    .external-icon {
      font-size: 14px;
      width: 14px;
      height: 14px;
    }

    .loading-spinner {
      display: flex;
      justify-content: center;
      padding: 48px 0;
    }

    @media (max-width: 768px) {
      .search-container {
        padding: 16px;
      }

      .search-row {
        flex-direction: column;
        align-items: stretch;
      }

      .search-box {
        width: 100%;
      }

      .sort-filters-wrapper {
        justify-content: space-between;
        width: 100%;
      }

      .results-grid {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class SearchComponent {
  searchForm: FormGroup;
  sortField = 'newest';
  sortDropdownOpen = false;
  pageSize = 8;
  pageIndex = 0;

  // For managing abstract expansions
  expandedAbstracts: { [key: number]: boolean } = {};
  abstractMaxLength = 150;

  // Signals
  isLoading = signal(false);
  results = signal<ContentItem[]>([]);
  resultsTotal = signal(0);
  hasSearched = signal(false);

  constructor(private fb: FormBuilder, private http: HttpClient) {
    this.searchForm = this.fb.group({
      query: ['AI']
    });
    // Auto-search on component init
    this.search();
  }

  toggleSortDropdown(): void {
    this.sortDropdownOpen = !this.sortDropdownOpen;
  }

  setSortField(field: string): void {
    this.sortField = field;
    this.sortDropdownOpen = false;
    this.search();
  }

  search(): void {
    this.isLoading.set(true);
    this.hasSearched.set(true);
    this.expandedAbstracts = {}; // Reset expanded state when new search is performed

    // Build search params
    const params = {
      ...this.searchForm.value,
      page: this.pageIndex,
      size: this.pageSize,
      sort: this.sortField
    };

    this.http.post<SearchResult>('/api/content/search', params)
      .pipe(
        catchError(err => {
          console.error('Search error', err);
          this.isLoading.set(false);
          // For demo, return mock data
          return of(this.getMockSearchResults(params));
        })
      )
      .subscribe(data => {
        this.results.set(data.items);
        this.resultsTotal.set(data.total);
        this.isLoading.set(false);
      });
  }

  getAbstractToShow(item: ContentItem, index: number): string {
    if (!item.abstract) return '';

    if (this.expandedAbstracts[index] || item.abstract.length <= this.abstractMaxLength) {
      return item.abstract;
    }

    return item.abstract.substring(0, this.abstractMaxLength) + '...';
  }

  shouldShowMoreButton(item: ContentItem, index: number): boolean {
    return !!(item.abstract && item.abstract.length > this.abstractMaxLength);
  }

  toggleShowMore(index: number): void {
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
      case 'slide':
        return 'slideshow';
      case 'youtube':
        return 'smart_display';
      case 'pdf':
        return 'picture_as_pdf';
      default:
        return 'insert_drive_file';
    }
  }

  clearSearch(): void {
    this.searchForm.get('query')?.setValue('');
    this.search();
  }

  // Mock data for demo that matches the screenshot
  private getMockSearchResults(params: any): SearchResult {
    const mockData: ContentItem[] = [
      {
        id: '1',
        title: 'AI for Banking: Streamline core banking services and personalize customer experiences',
        tags: ['Finance', 'Banking'],
        abstract: 'This session talks about how Generative AI is transforming the way we live, work, bank, and invest. It covers Google Cloud\'s insights, real-world use cases for boosting productivity in banking, and features success stories from industry leaders leveraging AI for innovation. Attendees will gain a deeper understanding of how AI is reshaping financial services.',
        type: 'Technical Session',
        track: 'Finance',
        author: 'Google Cloud',
        dateCreated: '2023-05-15T10:30:00Z',
        dateModified: '2023-05-15T10:30:00Z',
        recommended: true,
        assets: [
          { type: 'Slide', name: 'Presentation Slides', url: '#' },
          { type: 'YouTube', name: 'Video Recording', url: '#' }
        ]
      },
      {
        id: '2',
        title: 'AI for media: How Paramount+ uses artificial intelligence to streamline and personalize video',
        tags: ['Media', 'Entertainment'],
        abstract: 'This session talks about how Generative AI is transforming the way we live, work, bank, and invest. It covers Google Cloud\'s insights, real-world use cases for boosting productivity in banking, and features success stories from industry leaders leveraging AI for innovation.',
        type: 'New',
        track: 'Media & Entertainment',
        author: 'Paramount+',
        dateCreated: '2023-06-01T14:00:00Z',
        dateModified: '2023-06-02T09:30:00Z',
        assets: [
          { type: 'Slide', name: 'Presentation Slides', url: '#' },
          { type: 'PDF', name: 'Case Study Document', url: '#' }
        ]
      },
      {
        id: '3',
        title: 'AI for healthcare: Efficient care delivery and drug discovery',
        tags: ['Healthcare', 'Life Sciences'],
        abstract: 'This session talks about how AI is poised to revolutionize the way we conduct research, leading to groundbreaking discoveries and transformative advancements in healthcare sector.',
        type: 'AI Summary',
        track: 'Healthcare & Life Sciences',
        author: 'Medical AI Team',
        dateCreated: '2023-05-20T11:15:00Z',
        dateModified: '2023-05-25T16:20:00Z',
        priority: true,
        assets: [
          { type: 'Slide', name: 'Presentation Slides', url: '#' },
          { type: 'YouTube', name: 'Demo Recording', url: '#' }
        ]
      },
      {
        id: '4',
        title: 'AI for telecommunications: Transform customer interactions and network operations',
        tags: ['Telecommunications', 'Customer Service'],
        abstract: 'This session talks about how Google Cloud is helping CSPs customers in implementing gen AI to improve online self service, increase effectiveness of agent assisted interactions, create optimized next best offers.',
        type: 'Technical Session',
        track: 'Healthcare & Life Sciences',
        author: 'Telecom Innovation Team',
        dateCreated: '2023-04-10T09:00:00Z',
        dateModified: '2023-04-15T13:45:00Z',
        priority: true,
        assets: [
          { type: 'Slide', name: 'Presentation Slides', url: '#' },
          { type: 'YouTube', name: 'Video Recording', url: '#' }
        ]
      }
    ];

    // Apply search filter if query exists
    let filtered = [...mockData];
    if (params.query && params.query !== 'AI') {
      const query = params.query.toLowerCase();
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(query) ||
        item.abstract.toLowerCase().includes(query) ||
        item.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // Sort
    switch(params.sort) {
      case 'newest':
        filtered.sort((a, b) => new Date(b.dateModified).getTime() - new Date(a.dateModified).getTime());
        break;
      case 'title':
        filtered.sort((a, b) => a.title.localeCompare(b.title));
        break;
      // For relevance, we'll just keep the current order in this mock
    }

    // Pagination
    const total = filtered.length;
    const startIndex = params.page * params.size;
    const paginatedItems = filtered.slice(startIndex, startIndex + params.size);

    return {
      items: paginatedItems,
      total: total
    };
  }

  get queryControl(): FormControl {
    return this.searchForm.get('query') as FormControl;
  }
}
