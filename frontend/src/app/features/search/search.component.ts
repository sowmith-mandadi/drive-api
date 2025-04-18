import { Component, signal, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, FormControl } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { catchError, of, Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';
import { RouterModule, Router } from '@angular/router';

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
import { MatSidenavModule } from '@angular/material/sidenav';

// Update imports to use our shared models
import { Content, Asset, SearchResult, Filter, FilterOption } from '../../shared/models/content.model';
import { ContentService } from '../../core/services/content.service';

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
    MatTooltipModule,
    MatSidenavModule
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
              (keydown)="handleKeyDown($event)"
            >
            <button
              *ngIf="searchForm.get('query')?.value"
              class="clear-button"
              type="button"
              (click)="clearSearch()"
            >
              <mat-icon>close</mat-icon>
            </button>
            <button
              class="search-button"
              type="button"
              (click)="search()"
            >
              <mat-icon>search</mat-icon>
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

            <button type="button" class="filters-button" (click)="toggleFilters()">
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

      <div class="search-results" *ngIf="!isLoading()" [class.with-filters]="showFilters">
        <div class="no-results" *ngIf="results().length === 0 && hasSearched()">
          <mat-icon>search_off</mat-icon>
          <h3>No results found</h3>
          <p>Try adjusting your search or filter criteria</p>
        </div>

        <div class="results-grid" *ngIf="results().length > 0">
          <div class="result-card" *ngFor="let item of results(); let i = index" (click)="navigateToContent(item.id)">
            <button class="bookmark-button" [class.bookmarked]="item.bookmarked" (click)="toggleBookmark($event, item)">
              <mat-icon>{{ item.bookmarked ? 'bookmark' : 'bookmark_border' }}</mat-icon>
            </button>

            <h3 class="card-title">{{ item.title }}</h3>

            <div class="card-labels">
              <div class="label priority" *ngIf="item.priority">Priority</div>
              <div class="label recommended" *ngIf="item.recommended">Recommended</div>
              <div class="label new" *ngIf="isNewContent(item)">New</div>
            </div>

            <div class="ai-summary" *ngIf="hasAiSummary(item)">
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
                (click)="toggleShowMore($event, i)">
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
                  class="asset-link"
                  (click)="$event.stopPropagation()">
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

      <!-- Filter sidebar -->
      <div class="filter-sidebar" [class.open]="showFilters">
        <div class="filter-header">
          <h2>Filters</h2>
          <button type="button" class="close-filters-button" (click)="toggleFilters()">
            <mat-icon>close</mat-icon>
          </button>
        </div>

        <div class="filter-body">
          <div class="filter-section" *ngFor="let filter of filters; let i = index">
            <div
              class="filter-section-header"
              (click)="filter.expanded = !filter.expanded"
            >
              <h3>{{ filter.name }}</h3>
              <mat-icon>{{ filter.expanded ? 'expand_less' : 'expand_more' }}</mat-icon>
            </div>

            <div class="filter-options" *ngIf="filter.expanded">
              <div class="filter-option" *ngFor="let option of filter.options">
                <mat-checkbox
                  [checked]="option.selected"
                  (change)="option.selected = !option.selected"
                  [ngStyle]="{'color': '#202124', 'font-weight': '400'}"
                >
                  {{ option.label }}
                </mat-checkbox>
                <span class="option-count">{{ option.count }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="filter-actions">
          <button
            type="button"
            class="clear-filters-button"
            (click)="clearAllFilters()"
          >
            Clear all
          </button>
          <button
            type="button"
            class="apply-filters-button"
            (click)="applyFilters()"
          >
            Apply
          </button>
        </div>
      </div>

      <!-- Overlay to close filters when clicking outside -->
      <div
        class="filters-overlay"
        *ngIf="showFilters"
        (click)="toggleFilters()"
      ></div>
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
      position: relative;
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

    .search-results {
      transition: padding 0.3s ease;
      width: 100%;
    }

    .search-results.with-filters {
      padding-right: 320px;
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
      cursor: pointer;
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
      z-index: 1;
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
      z-index: 2;
      position: relative;
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
      z-index: 2;
      position: relative;
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

    /* Filter Sidebar Styles */
    .filter-sidebar {
      position: fixed;
      top: 0;
      right: -320px;
      width: 320px;
      height: 100%;
      background-color: #fff;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      z-index: 1001;
      transition: right 0.3s ease;
      display: flex;
      flex-direction: column;
      overflow-y: auto;
    }

    .filter-sidebar.open {
      right: 0;
    }

    .filter-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 24px;
      border-bottom: 1px solid #e0e0e0;
      position: sticky;
      top: 0;
      background-color: #fff;
      z-index: 1;
    }

    .filter-header h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 500;
      color: #202124;
    }

    .close-filters-button {
      background: none;
      border: none;
      color: #5f6368;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 4px;
    }

    .filter-body {
      flex: 1;
      overflow-y: auto;
      padding: 16px 24px;
    }

    .filter-section {
      margin-bottom: 24px;
    }

    .filter-section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      margin-bottom: 12px;
    }

    .filter-section-header h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 500;
      color: #202124;
    }

    .filter-options {
      margin-left: 8px;
    }

    .filter-option {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
    }

    .filter-option mat-checkbox {
      color: #202124;
      font-weight: normal;
    }

    /* Override Material checkbox styles to ensure text readability */
    ::ng-deep .filter-option .mat-mdc-checkbox {
      --mdc-checkbox-unselected-hover-icon-color: #5f6368;
      --mdc-checkbox-unselected-icon-color: #5f6368;
    }

    ::ng-deep .filter-option .mat-mdc-checkbox .mdc-checkbox .mdc-checkbox__background {
      border-color: #5f6368 !important;
    }

    ::ng-deep .filter-option .mat-mdc-checkbox .mdc-checkbox__background {
      border-width: 2px;
    }

    ::ng-deep .filter-option .mat-mdc-checkbox.mat-accent {
      --mdc-checkbox-selected-checkmark-color: #fff;
      --mdc-checkbox-selected-focus-icon-color: #1a73e8;
      --mdc-checkbox-selected-hover-icon-color: #1a73e8;
      --mdc-checkbox-selected-icon-color: #1a73e8;
      --mdc-checkbox-selected-pressed-icon-color: #1a73e8;
    }

    /* Make checkbox label text darker and more readable */
    ::ng-deep .filter-option .mdc-form-field {
      color: #202124 !important;
    }

    ::ng-deep .filter-option .mdc-label {
      color: #202124 !important;
      font-weight: 400 !important;
    }

    ::ng-deep .filter-option .mat-mdc-checkbox .mdc-label {
      color: #202124 !important;
    }

    .option-count {
      font-size: 12px;
      color: #5f6368;
      margin-left: 8px;
    }

    .filter-actions {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      padding: 16px 24px;
      border-top: 1px solid #e0e0e0;
      position: sticky;
      bottom: 0;
      background-color: #fff;
      z-index: 1;
    }

    .clear-filters-button {
      background: none;
      border: none;
      color: #5f6368;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      padding: 8px 16px;
    }

    .apply-filters-button {
      background-color: #1a73e8;
      color: #fff;
      border: none;
      border-radius: 4px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      padding: 8px 16px;
      transition: background-color 0.2s;
    }

    .apply-filters-button:hover {
      background-color: #1765cc;
    }

    .filters-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.3);
      z-index: 1000;
    }

    .search-button {
      background: none;
      border: none;
      color: #1a73e8;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      width: 46px;
      height: 46px;
    }

    .search-button:hover {
      background-color: rgba(26, 115, 232, 0.04);
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

      .filter-sidebar {
        width: 280px;
      }

      .search-results.with-filters {
        padding-right: 0;
      }
    }
  `]
})
export class SearchComponent implements OnInit, OnDestroy {
  searchForm: FormGroup;
  sortField = 'newest';
  sortDropdownOpen = false;
  pageSize = 8;
  pageIndex = 0;
  showFilters = false;

  // For managing abstract expansions
  expandedAbstracts: { [key: number]: boolean } = {};
  abstractMaxLength = 150;

  // For cleaning up subscriptions
  private destroy$ = new Subject<void>();

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
      name: 'Content Tags',
      options: [
        { value: 'ai', label: 'AI', selected: false, count: 42 },
        { value: 'innovation', label: 'Innovation', selected: false, count: 28 },
        { value: 'cloud', label: 'Cloud', selected: false, count: 62 },
        { value: 'security', label: 'Security', selected: false, count: 26 },
        { value: 'best-practices', label: 'Best Practices', selected: false, count: 43 }
      ],
      expanded: false
    }
  ];

  // Signals
  isLoading = signal(false);
  results = signal<Content[]>([]);
  resultsTotal = signal(0);
  hasSearched = signal(false);

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router,
    private contentService: ContentService
  ) {
    this.searchForm = this.fb.group({
      query: ['AI']
    });
    // Set up the FormControl reference
    this.queryControl = this.searchForm.get('query') as FormControl;

    // Auto-search on component init
    this.search();
  }

  // Define queryControl as a class property
  queryControl: FormControl;

  toggleSortDropdown(): void {
    this.sortDropdownOpen = !this.sortDropdownOpen;
  }

  setSortField(field: string): void {
    this.sortField = field;
    this.sortDropdownOpen = false;
    this.search();
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

    // Search with filters applied
    this.search();

    // Close filter panel on small screens
    if (window.innerWidth <= 768) {
      this.showFilters = false;
    }
  }

  search(): void {
    this.isLoading.set(true);
    this.hasSearched.set(true);
    this.expandedAbstracts = {}; // Reset expanded state when new search is performed

    // Build search params
    const query = this.searchForm.get('query')?.value || '';

    const params = {
      query,
      page: this.pageIndex,
      size: this.pageSize,
      sort: this.sortField,
      filters: this.getSelectedFilters()
    };

    console.log('Searching with params:', params);

    // Use ContentService instead of direct HTTP request
    this.contentService.searchContent(params).subscribe({
      next: (data) => {
        console.log('Search results:', data);
        this.results.set(data.items || []);
        this.resultsTotal.set(data.total || 0);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Search error', err);
        this.isLoading.set(false);
        this.results.set([]);
      }
    });
  }

  getSelectedFilters(): any {
    const filters: any = {};

    this.filters.forEach(filter => {
      const selected = filter.options
        .filter(option => option.selected)
        .map(option => option.value);

      if (selected.length > 0) {
        // Convert filter name to camelCase for API parameters
        const key = filter.name.toLowerCase().replace(/\s(.)/g, ($1) => $1.toUpperCase()).replace(/\s/g, '');
        filters[key] = selected;
      }
    });

    return filters;
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

  toggleBookmark(event: Event, item: Content): void {
    event.stopPropagation(); // Prevent navigation
    item.bookmarked = !item.bookmarked;
    // In a real app, this would also call an API to save the bookmark state
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

  clearSearch(): void {
    this.searchForm.get('query')?.setValue('');
    // The valueChanges subscription will trigger the search
  }

  // Add a method to handle Enter key
  handleKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      event.preventDefault();
      this.search();
    }
  }

  navigateToContent(contentId: string): void {
    this.router.navigate(['/content', contentId]);
  }

  isNewContent(item: Content): boolean {
    // Check if the item has a 'New' tag
    return item.tags?.some(tag => tag === 'New');
  }

  hasAiSummary(item: Content): boolean {
    // Check if item has an AI summary or an AI tag
    return !!item.aiSummary || item.tags?.some(tag => tag.includes('AI'));
  }

  ngOnInit(): void {
    // Set up debounced search
    this.queryControl.valueChanges.pipe(
      takeUntil(this.destroy$),
      debounceTime(300), // Wait 300ms after the user stops typing
      distinctUntilChanged() // Only trigger if the value has changed
    ).subscribe(value => {
      if (value && value.length >= 2) {
        // Only search if the query is at least 2 characters long
        this.search();
      } else if (value === '') {
        this.search(); // Search with empty query to show all results
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
