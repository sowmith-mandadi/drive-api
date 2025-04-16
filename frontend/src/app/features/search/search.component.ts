import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
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
              class="filters-toggle"
              (click)="filtersExpanded = !filtersExpanded">
              <mat-icon>{{ filtersExpanded ? 'expand_less' : 'expand_more' }}</mat-icon>
              {{ filtersExpanded ? 'Hide Filters' : 'Show Filters' }}
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
          <mat-card class="result-card" *ngFor="let item of results(); let i = index">
            <mat-card-content>
              <h3 class="card-title">{{ item.title }}</h3>

              <div class="card-tags">
                <mat-chip-set>
                  <mat-chip *ngFor="let tag of item.tags.slice(0, 3)" color="primary" selected>{{ tag }}</mat-chip>
                </mat-chip-set>
              </div>

              <div class="card-abstract">
                <p>
                  {{ getAbstractToShow(item, i) }}
                  <button
                    *ngIf="shouldShowMoreButton(item, i)"
                    mat-button
                    color="primary"
                    class="show-more-btn"
                    (click)="toggleShowMore(i)">
                    {{ expandedAbstracts[i] ? 'Show less' : 'Show more' }}
                  </button>
                </p>
              </div>

              <div class="card-meta">
                <span class="meta-type">{{ item.type }}</span>
                <span class="meta-track">{{ item.track }}</span>
                <span class="meta-date">{{ formatDate(item.dateModified) }}</span>
              </div>

              <div class="asset-links" *ngIf="item.assets && item.assets.length > 0">
                <div class="asset-buttons">
                  <a
                    *ngFor="let asset of item.assets"
                    mat-stroked-button
                    [href]="asset.url"
                    target="_blank"
                    [matTooltip]="asset.name">
                    <mat-icon>
                      {{ getAssetIcon(asset.type) }}
                    </mat-icon>
                    {{ asset.type }}
                  </a>
                </div>
              </div>
            </mat-card-content>
          </mat-card>
        </div>

        <mat-paginator
          *ngIf="resultsTotal() > 0"
          [length]="resultsTotal()"
          [pageSize]="pageSize"
          [pageIndex]="pageIndex"
          [pageSizeOptions]="[4, 8, 16, 32]"
          (page)="handlePageEvent($event)"
          aria-label="Select page">
        </mat-paginator>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
    }

    .search-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 1rem;
    }

    .search-header {
      text-align: center;
      margin-bottom: 2rem;
    }

    .search-header h1 {
      font-size: 1.75rem;
      color: #202124;
      margin: 0;
    }

    .search-form-container {
      background-color: #f8f9fa;
      border-radius: 8px;
      padding: 1.5rem;
      margin-bottom: 2rem;
    }

    .search-bar {
      display: flex;
      align-items: center;
      max-width: 800px;
      margin: 0 auto;
      gap: 0.5rem;
    }

    .search-input {
      flex: 1;
    }

    .search-button {
      height: 56px;
      min-width: 100px;
    }

    .filter-actions {
      display: flex;
      justify-content: center;
      margin-top: 1rem;
    }

    .filters-toggle {
      color: #5f6368;
      font-size: 0.875rem;
    }

    .filters-panel {
      margin-top: 1rem;
      border-top: 1px solid #dadce0;
      padding-top: 1rem;
    }

    .grid-filters {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 1rem;
    }

    .tag-filters {
      margin-top: 1rem;
    }

    .full-width {
      width: 100%;
    }

    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .results-header h2 {
      font-size: 1.25rem;
      font-weight: 500;
      color: #202124;
      margin: 0;
    }

    .sort-select {
      width: 180px;
    }

    .no-results {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 3rem 0;
      text-align: center;
      color: #5f6368;
    }

    .no-results mat-icon {
      font-size: 3rem;
      height: 3rem;
      width: 3rem;
      margin-bottom: 1rem;
    }

    .no-results h3 {
      font-size: 1.25rem;
      font-weight: 500;
      margin-bottom: 0.5rem;
    }

    .results-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }

    .result-card {
      height: 100%;
      border: 1px solid #dadce0;
      border-radius: 8px;
      box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
      transition: box-shadow 0.2s;
    }

    .result-card:hover {
      box-shadow: 0 1px 3px 0 rgba(60,64,67,.3), 0 4px 8px 3px rgba(60,64,67,.15);
    }

    .card-title {
      font-size: 1.25rem;
      font-weight: 500;
      color: #202124;
      margin-top: 0;
      margin-bottom: 0.75rem;
    }

    .card-tags {
      margin-bottom: 1rem;
    }

    .card-abstract {
      font-size: 0.875rem;
      color: #5f6368;
      margin-bottom: 1rem;
    }

    .card-abstract p {
      margin: 0;
    }

    .show-more-btn {
      padding: 0;
      min-width: 0;
      font-weight: 500;
      height: 24px;
      line-height: 24px;
    }

    .card-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      font-size: 0.75rem;
      margin-bottom: 1rem;
    }

    .meta-type, .meta-track, .meta-date {
      padding: 0.25rem 0.5rem;
      border-radius: 12px;
    }

    .meta-type {
      background-color: #e8f0fe;
      color: #1a73e8;
    }

    .meta-track {
      background-color: #e6f4ea;
      color: #137333;
    }

    .meta-date {
      background-color: #f1f3f4;
      color: #5f6368;
    }

    .asset-links {
      margin-top: 1rem;
    }

    .asset-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .asset-buttons a {
      font-size: 0.75rem;
    }

    .loading-spinner {
      display: flex;
      justify-content: center;
      padding: 3rem 0;
    }

    @media (max-width: 768px) {
      .search-bar {
        flex-direction: column;
      }

      .search-button {
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
  filtersExpanded = false;
  sortField = 'relevance';
  pageSize = 8;
  pageIndex = 0;

  // For managing abstract expansions
  expandedAbstracts: { [key: number]: boolean } = {};
  abstractMaxLength = 80;

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
    this.expandedAbstracts = {}; // Reset expanded state when new search is performed

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
      case 'slides':
        return 'slideshow';
      case 'video':
        return 'videocam';
      case 'demo':
        return 'code';
      case 'github':
        return 'code';
      default:
        return 'insert_drive_file';
    }
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
        abstract: 'Learn how to use Terraform to manage your Google Cloud infrastructure efficiently with code. This session will cover best practices, state management, and integration with CI/CD pipelines.',
        type: 'Technical Session',
        track: 'Infrastructure',
        author: 'Sarah Johnson',
        dateCreated: '2023-04-15T10:30:00Z',
        dateModified: '2023-05-10T14:20:00Z',
        thumbUrl: 'assets/images/terraform.jpg',
        assets: [
          { type: 'PDF', name: 'Terraform Best Practices', url: 'assets/documents/terraform-best-practices.pdf' },
          { type: 'Slides', name: 'Session Slides', url: 'assets/slides/terraform-slides.pptx' },
          { type: 'GitHub', name: 'Sample Code', url: 'https://github.com/example/terraform-samples' }
        ]
      },
      {
        id: '2',
        title: 'Building Scalable Microservices with GKE',
        tags: ['Kubernetes', 'Microservices', 'GKE'],
        abstract: 'Discover patterns for designing and deploying resilient microservices on Google Kubernetes Engine. Learn how to implement service mesh, autoscaling, and observability for your containerized applications.',
        type: 'Workshop',
        track: 'Application Development',
        author: 'Michael Chen',
        dateCreated: '2023-04-10T08:15:00Z',
        dateModified: '2023-05-05T09:45:00Z',
        thumbUrl: 'assets/images/kubernetes.jpg',
        assets: [
          { type: 'PDF', name: 'Workshop Guide', url: 'assets/documents/gke-workshop-guide.pdf' },
          { type: 'Demo', name: 'Live Demo', url: 'https://demo.example.com/gke-microservices' }
        ]
      },
      {
        id: '3',
        title: 'Data Analytics with BigQuery ML',
        tags: ['BigQuery', 'Machine Learning', 'Analytics'],
        abstract: 'Explore how to implement machine learning models directly in BigQuery using SQL. This session covers regression, classification, and clustering models without having to export your data.',
        type: 'Presentation',
        track: 'Data & Analytics',
        author: 'Emily Rodriguez',
        dateCreated: '2023-04-05T11:00:00Z',
        dateModified: '2023-05-01T15:30:00Z',
        thumbUrl: 'assets/images/bigquery.jpg',
        assets: [
          { type: 'Slides', name: 'Presentation Slides', url: 'assets/slides/bigquery-ml-slides.pptx' },
          { type: 'Video', name: 'Demo Recording', url: 'assets/videos/bigquery-ml-demo.mp4' }
        ]
      },
      {
        id: '4',
        title: 'Serverless Architecture with Cloud Functions',
        tags: ['Serverless', 'Cloud Functions', 'Event-driven'],
        abstract: 'Build event-driven applications without managing infrastructure using Google Cloud Functions. Learn best practices for function design, triggers, and how to integrate with other Google Cloud services.',
        type: 'Technical Session',
        track: 'Application Development',
        author: 'David Wilson',
        dateCreated: '2023-03-20T14:45:00Z',
        dateModified: '2023-04-25T10:15:00Z',
        thumbUrl: 'assets/images/serverless.jpg',
        assets: [
          { type: 'PDF', name: 'Architecture Diagrams', url: 'assets/documents/serverless-architecture.pdf' },
          { type: 'GitHub', name: 'Example Functions', url: 'https://github.com/example/cloud-functions-samples' }
        ]
      },
      {
        id: '5',
        title: 'CI/CD Pipelines with Cloud Build',
        tags: ['CI/CD', 'DevOps', 'Cloud Build'],
        abstract: 'Implement continuous integration and deployment pipelines using Google Cloud Build. This hands-on workshop will guide you through setting up a complete CI/CD pipeline for your applications.',
        type: 'Workshop',
        track: 'DevOps',
        author: 'Jessica Lee',
        dateCreated: '2023-03-15T09:30:00Z',
        dateModified: '2023-04-20T13:10:00Z',
        thumbUrl: 'assets/images/cicd.jpg',
        assets: [
          { type: 'PDF', name: 'Workshop Guide', url: 'assets/documents/cloudbuild-workshop.pdf' },
          { type: 'GitHub', name: 'Sample Pipeline', url: 'https://github.com/example/cloudbuild-pipeline' },
          { type: 'Slides', name: 'Workshop Slides', url: 'assets/slides/cloudbuild-slides.pptx' }
        ]
      },
      {
        id: '6',
        title: 'Securing APIs with Cloud Armor',
        tags: ['Security', 'API', 'Cloud Armor'],
        abstract: 'Protect your applications from web attacks and DDoS with Google Cloud Armor. Learn how to configure security policies, rate limiting, and integrate with WAF capabilities to safeguard your services.',
        type: 'Presentation',
        track: 'Security',
        author: 'Robert Garcia',
        dateCreated: '2023-03-10T16:20:00Z',
        dateModified: '2023-04-15T11:05:00Z',
        thumbUrl: 'assets/images/security.jpg',
        assets: [
          { type: 'PDF', name: 'Security Whitepaper', url: 'assets/documents/cloud-armor-security.pdf' },
          { type: 'Slides', name: 'Presentation Deck', url: 'assets/slides/cloud-armor-slides.pptx' }
        ]
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
