import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { catchError, of } from 'rxjs';
import { RouterLink, RouterModule } from '@angular/router';

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
    RouterLink,
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
    MatBadgeModule
  ],
  template: `
    <div class="search-container">
      <div class="search-header">
        <h1>Search Google Cloud Next Content</h1>
      </div>

      <div class="search-form-container">
        <form [formGroup]="searchForm" (ngSubmit)="search()">
          <div class="search-bar">
            <mat-form-field appearance="outline" class="search-input">
              <mat-label>Search content</mat-label>
              <input matInput formControlName="query" placeholder="Enter keywords...">
              <mat-icon matPrefix>search</mat-icon>
              <button *ngIf="searchForm.get('query')?.value" matSuffix mat-icon-button aria-label="Clear"
                      (click)="clearSearch()">
                <mat-icon>close</mat-icon>
              </button>
            </mat-form-field>

            <button mat-raised-button color="primary" type="submit" class="search-button">
              Search
            </button>
          </div>

          <div class="filter-actions">
            <button
              mat-button
              type="button"
              [matBadge]="getActiveFiltersCount()"
              [matBadgeHidden]="getActiveFiltersCount() === 0"
              matBadgePosition="after"
              matBadgeColor="accent"
              (click)="filtersExpanded = !filtersExpanded">
              <mat-icon>filter_list</mat-icon>
              {{ filtersExpanded ? 'Hide Filters' : 'Show Filters' }}
            </button>

            <button
              mat-button
              type="button"
              color="warn"
              (click)="resetFilters()"
              [disabled]="getActiveFiltersCount() === 0">
              <mat-icon>clear_all</mat-icon>
              Reset Filters
            </button>
          </div>

          <div class="filters-panel" *ngIf="filtersExpanded">
            <div class="grid-filters">
              <mat-form-field appearance="outline">
                <mat-label>Content Type</mat-label>
                <mat-select formControlName="type" multiple>
                  <mat-option value="Presentation">Presentation</mat-option>
                  <mat-option value="Workshop">Workshop</mat-option>
                  <mat-option value="Technical Session">Technical Session</mat-option>
                  <mat-option value="Keynote">Keynote</mat-option>
                </mat-select>
              </mat-form-field>

              <mat-form-field appearance="outline">
                <mat-label>Track</mat-label>
                <mat-select formControlName="track" multiple>
                  <mat-option value="Infrastructure">Infrastructure</mat-option>
                  <mat-option value="Data & Analytics">Data & Analytics</mat-option>
                  <mat-option value="Application Development">Application Development</mat-option>
                  <mat-option value="AI & Machine Learning">AI & Machine Learning</mat-option>
                  <mat-option value="Security">Security</mat-option>
                </mat-select>
              </mat-form-field>

              <mat-form-field appearance="outline">
                <mat-label>Date From</mat-label>
                <input matInput [matDatepicker]="pickerFrom" formControlName="dateFrom">
                <mat-datepicker-toggle matIconSuffix [for]="pickerFrom"></mat-datepicker-toggle>
                <mat-datepicker #pickerFrom></mat-datepicker>
              </mat-form-field>

              <mat-form-field appearance="outline">
                <mat-label>Date To</mat-label>
                <input matInput [matDatepicker]="pickerTo" formControlName="dateTo">
                <mat-datepicker-toggle matIconSuffix [for]="pickerTo"></mat-datepicker-toggle>
                <mat-datepicker #pickerTo></mat-datepicker>
              </mat-form-field>
            </div>

            <div class="tag-filters">
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Tags</mat-label>
                <mat-select formControlName="tags" multiple>
                  <mat-option value="Infrastructure">Infrastructure</mat-option>
                  <mat-option value="DevOps">DevOps</mat-option>
                  <mat-option value="Kubernetes">Kubernetes</mat-option>
                  <mat-option value="Machine Learning">Machine Learning</mat-option>
                  <mat-option value="BigQuery">BigQuery</mat-option>
                  <mat-option value="Serverless">Serverless</mat-option>
                  <mat-option value="Security">Security</mat-option>
                  <mat-option value="Networking">Networking</mat-option>
                  <mat-option value="Cloud Functions">Cloud Functions</mat-option>
                  <mat-option value="Monitoring">Monitoring</mat-option>
                </mat-select>
              </mat-form-field>
            </div>
          </div>
        </form>
      </div>

      <mat-divider class="section-divider"></mat-divider>

      <div class="loading-spinner" *ngIf="isLoading()">
        <mat-spinner diameter="40"></mat-spinner>
      </div>

      <div class="search-results" *ngIf="!isLoading()">
        <div class="results-header" *ngIf="resultsTotal() > 0">
          <h2>Found {{ resultsTotal() }} results</h2>
          <mat-form-field appearance="outline" class="sort-select">
            <mat-label>Sort by</mat-label>
            <mat-select [(value)]="sortField" (selectionChange)="search()">
              <mat-option value="relevance">Relevance</mat-option>
              <mat-option value="date">Date (Newest first)</mat-option>
              <mat-option value="title">Title (A-Z)</mat-option>
            </mat-select>
          </mat-form-field>
        </div>

        <div class="no-results" *ngIf="resultsTotal() === 0 && hasSearched()">
          <mat-icon>search_off</mat-icon>
          <h3>No results found</h3>
          <p>Try adjusting your search or filter criteria</p>
        </div>

        <div class="results-grid" *ngIf="resultsTotal() > 0">
          <mat-card class="result-card" *ngFor="let item of results()">
            <div class="card-header" [style.background-image]="item.thumbUrl ? 'url(' + item.thumbUrl + ')' : ''">
              <div class="card-overlay">
                <mat-chip-set>
                  <mat-chip *ngFor="let tag of item.tags.slice(0, 2)">{{ tag }}</mat-chip>
                </mat-chip-set>
              </div>
            </div>
            <mat-card-content>
              <h3 class="card-title">{{ item.title }}</h3>
              <p class="card-abstract">{{ item.abstract }}</p>
              <div class="card-meta">
                <span class="meta-type">{{ item.type }}</span>
                <span class="meta-track">{{ item.track }}</span>
                <span class="meta-date">{{ formatDate(item.dateModified) }}</span>
              </div>
            </mat-card-content>
            <mat-card-actions>
              <button mat-button color="primary" [routerLink]="['/content-management/content', item.id]">
                <mat-icon>visibility</mat-icon>
                View
              </button>
            </mat-card-actions>
          </mat-card>
        </div>

        <mat-paginator
          *ngIf="resultsTotal() > 0"
          [length]="resultsTotal()"
          [pageSize]="pageSize"
          [pageIndex]="pageIndex"
          [pageSizeOptions]="[6, 12, 24, 48]"
          (page)="handlePageEvent($event)"
          aria-label="Select page">
        </mat-paginator>
      </div>
    </div>
  `,
  styles: [`
    .search-container {
      @apply max-w-7xl mx-auto p-6;
    }

    .search-header {
      @apply mb-6;

      h1 {
        @apply text-2xl font-semibold text-gray-800 m-0;
      }
    }

    .search-form-container {
      @apply bg-white rounded-lg shadow-md p-6 mb-6;
    }

    .search-bar {
      @apply flex gap-4 items-center;
    }

    .search-input {
      @apply flex-1;
    }

    .filter-actions {
      @apply flex justify-between mt-4;
    }

    .filters-panel {
      @apply mt-4 pt-4 border-t border-gray-200;
    }

    .grid-filters {
      @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4;
    }

    .tag-filters {
      @apply mt-4;
    }

    .full-width {
      @apply w-full;
    }

    .section-divider {
      @apply my-6;
    }

    .results-header {
      @apply flex justify-between items-center mb-6;

      h2 {
        @apply text-xl font-medium text-gray-800 m-0;
      }
    }

    .sort-select {
      @apply w-48;
    }

    .no-results {
      @apply flex flex-col items-center justify-center py-16 text-center text-gray-500;

      mat-icon {
        @apply text-5xl mb-4;
      }

      h3 {
        @apply text-xl font-medium mb-2;
      }
    }

    .results-grid {
      @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6;
    }

    .result-card {
      @apply flex flex-col h-full transition-transform duration-300;

      &:hover {
        transform: translateY(-4px);
        @apply shadow-lg;
      }
    }

    .card-header {
      height: 160px;
      background-color: #673ab7;
      background-size: cover;
      background-position: center;
      position: relative;
    }

    .card-overlay {
      @apply absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/70 to-transparent;
    }

    .card-title {
      @apply text-lg font-medium mb-2 line-clamp-2;
    }

    .card-abstract {
      @apply text-sm text-gray-600 mb-3 line-clamp-3;
    }

    .card-meta {
      @apply flex flex-wrap gap-2 text-xs;
      margin-top: auto;
    }

    .meta-type, .meta-track, .meta-date {
      @apply px-2 py-1 rounded-full;
    }

    .meta-type {
      @apply bg-purple-100 text-purple-800;
    }

    .meta-track {
      @apply bg-blue-100 text-blue-800;
    }

    .meta-date {
      @apply bg-gray-100 text-gray-700;
    }

    .loading-spinner {
      @apply flex justify-center my-16;
    }

    @media (max-width: 768px) {
      .search-bar {
        @apply flex-col;

        .search-button {
          @apply w-full;
        }
      }
    }
  `]
})
export class SearchComponent {
  searchForm: FormGroup;
  filtersExpanded = false;
  sortField = 'relevance';
  pageSize = 12;
  pageIndex = 0;

  // Signals
  isLoading = signal(false);
  results = signal<ContentItem[]>([]);
  resultsTotal = signal(0);
  hasSearched = signal(false);

  constructor(private fb: FormBuilder, private http: HttpClient) {
    this.searchForm = this.fb.group({
      query: [''],
      type: [[]],
      track: [[]],
      tags: [[]],
      dateFrom: [null],
      dateTo: [null]
    });
  }

  search(): void {
    this.isLoading.set(true);
    this.hasSearched.set(true);

    // Build search params
    const params = {
      ...this.searchForm.value,
      page: this.pageIndex,
      size: this.pageSize,
      sort: this.sortField
    };

    // Convert date objects to ISO strings
    if (params.dateFrom) params.dateFrom = params.dateFrom.toISOString();
    if (params.dateTo) params.dateTo = params.dateTo.toISOString();

    this.http.post<SearchResult>('/api/search', params)
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

  handlePageEvent(event: PageEvent): void {
    this.pageIndex = event.pageIndex;
    this.pageSize = event.pageSize;
    this.search();
  }

  clearSearch(): void {
    this.searchForm.get('query')?.setValue('');
  }

  resetFilters(): void {
    this.searchForm.patchValue({
      type: [],
      track: [],
      tags: [],
      dateFrom: null,
      dateTo: null
    });
    this.search();
  }

  getActiveFiltersCount(): number {
    const form = this.searchForm.value;
    let count = 0;

    if (form.type?.length) count += form.type.length;
    if (form.track?.length) count += form.track.length;
    if (form.tags?.length) count += form.tags.length;
    if (form.dateFrom) count++;
    if (form.dateTo) count++;

    return count;
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  // Mock data for demo
  private getMockSearchResults(params: any): SearchResult {
    const mockData: ContentItem[] = [
      {
        id: '1',
        title: 'Infrastructure as Code with Terraform on Google Cloud',
        tags: ['Infrastructure', 'DevOps', 'Terraform'],
        abstract: 'Learn how to use Terraform to manage your Google Cloud infrastructure efficiently with code.',
        type: 'Technical Session',
        track: 'Infrastructure',
        author: 'Sarah Johnson',
        dateCreated: '2023-04-15T10:30:00Z',
        dateModified: '2023-05-10T14:20:00Z',
        thumbUrl: 'assets/images/terraform.jpg'
      },
      {
        id: '2',
        title: 'Building Scalable Microservices with GKE',
        tags: ['Kubernetes', 'Microservices', 'GKE'],
        abstract: 'Discover patterns for designing and deploying resilient microservices on Google Kubernetes Engine.',
        type: 'Workshop',
        track: 'Application Development',
        author: 'Michael Chen',
        dateCreated: '2023-04-10T08:15:00Z',
        dateModified: '2023-05-05T09:45:00Z',
        thumbUrl: 'assets/images/kubernetes.jpg'
      },
      {
        id: '3',
        title: 'Data Analytics with BigQuery ML',
        tags: ['BigQuery', 'Machine Learning', 'Analytics'],
        abstract: 'Explore how to implement machine learning models directly in BigQuery using SQL.',
        type: 'Presentation',
        track: 'Data & Analytics',
        author: 'Emily Rodriguez',
        dateCreated: '2023-04-05T11:00:00Z',
        dateModified: '2023-05-01T15:30:00Z',
        thumbUrl: 'assets/images/bigquery.jpg'
      },
      {
        id: '4',
        title: 'Serverless Architecture with Cloud Functions',
        tags: ['Serverless', 'Cloud Functions', 'Event-driven'],
        abstract: 'Build event-driven applications without managing infrastructure using Google Cloud Functions.',
        type: 'Technical Session',
        track: 'Application Development',
        author: 'David Wilson',
        dateCreated: '2023-03-20T14:45:00Z',
        dateModified: '2023-04-25T10:15:00Z',
        thumbUrl: 'assets/images/serverless.jpg'
      },
      {
        id: '5',
        title: 'CI/CD Pipelines with Cloud Build',
        tags: ['CI/CD', 'DevOps', 'Cloud Build'],
        abstract: 'Implement continuous integration and deployment pipelines using Google Cloud Build.',
        type: 'Workshop',
        track: 'DevOps',
        author: 'Jessica Lee',
        dateCreated: '2023-03-15T09:30:00Z',
        dateModified: '2023-04-20T13:10:00Z',
        thumbUrl: 'assets/images/cicd.jpg'
      },
      {
        id: '6',
        title: 'Securing APIs with Cloud Armor',
        tags: ['Security', 'API', 'Cloud Armor'],
        abstract: 'Protect your applications from web attacks and DDoS with Google Cloud Armor.',
        type: 'Presentation',
        track: 'Security',
        author: 'Robert Garcia',
        dateCreated: '2023-03-10T16:20:00Z',
        dateModified: '2023-04-15T11:05:00Z',
        thumbUrl: 'assets/images/security.jpg'
      }
    ];

    // Apply filters
    let filtered = [...mockData];

    if (params.query) {
      const query = params.query.toLowerCase();
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(query) ||
        item.abstract.toLowerCase().includes(query) ||
        item.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    if (params.type?.length) {
      filtered = filtered.filter(item => params.type.includes(item.type));
    }

    if (params.track?.length) {
      filtered = filtered.filter(item => params.track.includes(item.track));
    }

    if (params.tags?.length) {
      filtered = filtered.filter(item =>
        item.tags.some(tag => params.tags.includes(tag))
      );
    }

    if (params.dateFrom) {
      const fromDate = new Date(params.dateFrom);
      filtered = filtered.filter(item => new Date(item.dateModified) >= fromDate);
    }

    if (params.dateTo) {
      const toDate = new Date(params.dateTo);
      filtered = filtered.filter(item => new Date(item.dateModified) <= toDate);
    }

    // Sort
    switch(params.sort) {
      case 'date':
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
}
