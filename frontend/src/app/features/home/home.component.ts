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
  template: `
    <div class="home-container">
      <mat-drawer-container class="content-container">
        <!-- Drawer for filters - only visible when showFilters is true -->
        <mat-drawer mode="side" position="end" [opened]="showFilters" class="filter-drawer">
          <div class="filter-header">
            <h2>Filters</h2>
            <button mat-icon-button (click)="clearAllFilters()" matTooltip="Clear all filters">
              <mat-icon>clear_all</mat-icon>
            </button>
          </div>

          <div class="filter-search">
            <mat-form-field appearance="outline" class="filter-search-field">
              <mat-label>Search in results</mat-label>
              <input matInput [(ngModel)]="searchQuery" placeholder="Type to search...">
              <mat-icon matSuffix>search</mat-icon>
            </mat-form-field>
          </div>

          <div class="filter-groups">
            <mat-accordion multi>
              <mat-expansion-panel *ngFor="let filter of filters" [expanded]="filter.expanded">
                <mat-expansion-panel-header>
                  <mat-panel-title>
                    {{ filter.name }}
                  </mat-panel-title>
                </mat-expansion-panel-header>

                <div class="filter-options">
                  <mat-checkbox
                    *ngFor="let option of filter.options"
                    [(ngModel)]="option.selected"
                    (change)="applyFilters()"
                    class="filter-option">
                    {{ option.label }} ({{ option.count }})
                  </mat-checkbox>
                </div>
              </mat-expansion-panel>
            </mat-accordion>
          </div>

          <div class="filter-actions">
            <button mat-flat-button color="primary" (click)="saveFilterPreset()">
              <mat-icon>save</mat-icon> Save Filter
            </button>
          </div>
        </mat-drawer>

        <mat-drawer-content class="main-content">
          <!-- Welcome section -->
          <div class="welcome-section">
            <div class="welcome-text">
              <h1>Welcome back, User</h1>
              <p>Here's what's new in your content management system</p>
            </div>
          </div>

          <!-- Search and filter bar -->
          <div class="search-filter-bar">
            <div class="search-container">
              <mat-form-field appearance="outline" class="search-field">
                <mat-label>Search content</mat-label>
                <input matInput placeholder="Search...">
                <mat-icon matPrefix>search</mat-icon>
              </mat-form-field>
            </div>

            <div class="filter-buttons">
              <button mat-stroked-button [matMenuTriggerFor]="sortMenu">
                <mat-icon>sort</mat-icon> Sort by
              </button>

              <button mat-stroked-button (click)="toggleFilters()">
                <mat-icon>filter_list</mat-icon> Filters
              </button>
            </div>
          </div>

          <mat-menu #sortMenu="matMenu">
            <button mat-menu-item (click)="sortBy('dateNewest')">Newest first</button>
            <button mat-menu-item (click)="sortBy('dateOldest')">Oldest first</button>
            <button mat-menu-item (click)="sortBy('titleAZ')">Title A-Z</button>
            <button mat-menu-item (click)="sortBy('titleZA')">Title Z-A</button>
          </mat-menu>

          <!-- Featured Content Carousel -->
          <div class="carousel-section">
            <div class="section-header">
              <h2>Featured Content</h2>
              <a routerLink="/search" class="view-all">View All</a>
            </div>

            <div class="card-carousel-container">
              <button mat-mini-fab class="carousel-nav-button prev-button" (click)="prevCarouselSlide()" [attr.aria-label]="'Previous slide'">
                <mat-icon>chevron_left</mat-icon>
              </button>

              <div class="card-carousel">
                <div class="card-carousel-track" [style.transform]="'translateX(' + (-selectedCarouselIndex * 100) + '%)'">
                  <mat-card *ngFor="let feature of featuredContent; let i = index" class="content-card carousel-card" [class.active]="i === selectedCarouselIndex">
                    <div class="card-badge" *ngIf="feature.status === 'review'">NEEDS REVIEW</div>
                    <div class="card-badge approved" *ngIf="feature.status === 'approved'">APPROVED</div>
                    <div class="card-badge published" *ngIf="feature.status === 'published'">PUBLISHED</div>

                    <mat-card-content>
                      <div class="card-track">{{ feature.track || 'Featured' }}</div>
                      <h3 class="card-title">{{ feature.title }}</h3>
                      <p class="card-description">{{ feature.description | slice:0:120 }}{{ feature.description.length > 120 ? '...' : '' }}</p>

                      <div class="card-meta">
                        <div class="presenters" *ngIf="feature.presenters && feature.presenters.length > 0">
                          <div *ngFor="let presenter of feature.presenters.slice(0, 2)" class="presenter">
                            <span class="presenter-name">{{ presenter.name }}</span>
                            <span class="presenter-company" *ngIf="presenter.title">{{ presenter.title }}, </span>
                            <span class="presenter-company">{{ presenter.company }}</span>
                          </div>
                          <div *ngIf="feature.presenters.length > 2" class="presenter-more">
                            +{{ feature.presenters.length - 2 }} more
                          </div>
                        </div>

                        <div class="card-date" *ngIf="feature.dateModified">
                          {{ feature.dateModified | date:'mediumDate' }}
                        </div>
                      </div>

                      <div class="card-tags" *ngIf="feature.tags && feature.tags.length > 0">
                        <mat-chip-listbox aria-label="Tags" class="tag-list">
                          <mat-chip-option *ngFor="let tag of feature.tags.slice(0, 3)" disableRipple selected="false" disabled>
                            {{ tag }}
                          </mat-chip-option>
                          <mat-chip-option *ngIf="feature.tags.length > 3" disableRipple selected="false" disabled>
                            +{{ feature.tags.length - 3 }}
                          </mat-chip-option>
                        </mat-chip-listbox>
                      </div>
                    </mat-card-content>

                    <mat-card-actions>
                      <button mat-button color="primary" [routerLink]="['/content-management/content', feature.id]">VIEW DETAILS</button>
                      <button mat-button color="accent" *ngIf="feature.status === 'review'" [routerLink]="['/content-management/review']">REVIEW</button>
                    </mat-card-actions>
                  </mat-card>
                </div>
              </div>

              <button mat-mini-fab class="carousel-nav-button next-button" (click)="nextCarouselSlide()" [attr.aria-label]="'Next slide'">
                <mat-icon>chevron_right</mat-icon>
              </button>
            </div>

            <div class="carousel-indicators">
              <button
                *ngFor="let feature of featuredContent; let i = index"
                class="carousel-indicator"
                [class.active]="i === selectedCarouselIndex"
                (click)="selectedCarouselIndex = i"
                [attr.aria-label]="'Go to slide ' + (i+1)">
              </button>
            </div>
          </div>

          <!-- Latest Updates section -->
          <div class="content-section">
            <div class="section-header">
              <h2>Latest Updates</h2>
              <a routerLink="/search" class="view-all">View All</a>
            </div>

            <div class="card-carousel-container">
              <button mat-mini-fab class="carousel-nav-button prev-button" (click)="prevLatestSlide()" [attr.aria-label]="'Previous latest updates'">
                <mat-icon>chevron_left</mat-icon>
              </button>

              <div class="card-carousel">
                <div class="card-carousel-track" [style.transform]="'translateX(' + (-selectedLatestIndex * 100) + '%)'">
                  <mat-card *ngFor="let content of latestUpdates; let i = index" class="content-card carousel-card" [class.active]="i === selectedLatestIndex">
                    <div class="card-badge" *ngIf="content.status === 'review'">NEEDS REVIEW</div>
                    <div class="card-badge approved" *ngIf="content.status === 'approved'">APPROVED</div>
                    <div class="card-badge published" *ngIf="content.status === 'published'">PUBLISHED</div>

                    <mat-card-content>
                      <div class="card-track">{{ content.track }}</div>
                      <h3 class="card-title">{{ content.title }}</h3>
                      <p class="card-description">{{ content.description | slice:0:120 }}{{ content.description.length > 120 ? '...' : '' }}</p>

                      <div class="card-meta">
                        <div class="presenters" *ngIf="content.presenters && content.presenters.length > 0">
                          <div *ngFor="let presenter of content.presenters.slice(0, 2)" class="presenter">
                            <span class="presenter-name">{{ presenter.name }}</span>
                            <span class="presenter-company" *ngIf="presenter.title">{{ presenter.title }}, </span>
                            <span class="presenter-company">{{ presenter.company }}</span>
                          </div>
                          <div *ngIf="content.presenters.length > 2" class="presenter-more">
                            +{{ content.presenters.length - 2 }} more
                          </div>
                        </div>

                        <div class="card-date" *ngIf="content.dateModified">
                          {{ content.dateModified | date:'mediumDate' }}
                        </div>
                      </div>

                      <div class="card-tags" *ngIf="content.tags && content.tags.length > 0">
                        <mat-chip-listbox aria-label="Tags" class="tag-list">
                          <mat-chip-option *ngFor="let tag of content.tags.slice(0, 3)" disableRipple selected="false" disabled>
                            {{ tag }}
                          </mat-chip-option>
                          <mat-chip-option *ngIf="content.tags.length > 3" disableRipple selected="false" disabled>
                            +{{ content.tags.length - 3 }}
                          </mat-chip-option>
                        </mat-chip-listbox>
                      </div>
                    </mat-card-content>

                    <mat-card-actions>
                      <button mat-button color="primary" [routerLink]="['/content-management/content', content.id]">VIEW DETAILS</button>
                      <button mat-button color="accent" *ngIf="content.status === 'review'" [routerLink]="['/content-management/review']">REVIEW</button>
                    </mat-card-actions>
                  </mat-card>
                </div>
              </div>

              <button mat-mini-fab class="carousel-nav-button next-button" (click)="nextLatestSlide()" [attr.aria-label]="'Next latest updates'">
                <mat-icon>chevron_right</mat-icon>
              </button>
            </div>

            <div class="carousel-indicators">
              <button
                *ngFor="let content of latestUpdates; let i = index"
                class="carousel-indicator"
                [class.active]="i === selectedLatestIndex"
                (click)="selectedLatestIndex = i"
                [attr.aria-label]="'Go to latest slide ' + (i+1)">
              </button>
            </div>
          </div>

          <!-- Recommended Content section -->
          <div class="content-section">
            <div class="section-header">
              <h2>Recommended Content</h2>
              <a routerLink="/search" class="view-all">View All</a>
            </div>

            <div class="cards-grid">
              <mat-card *ngFor="let content of visibleRecommended" class="content-card">
                <div class="card-badge" *ngIf="content.status === 'review'">NEEDS REVIEW</div>
                <div class="card-badge approved" *ngIf="content.status === 'approved'">APPROVED</div>
                <div class="card-badge published" *ngIf="content.status === 'published'">PUBLISHED</div>

                <mat-card-content>
                  <div class="card-track">{{ content.track }}</div>
                  <h3 class="card-title">{{ content.title }}</h3>
                  <p class="card-description">{{ content.description | slice:0:120 }}{{ content.description.length > 120 ? '...' : '' }}</p>

                  <div class="card-meta">
                    <div class="presenters">
                      <div *ngFor="let presenter of content.presenters.slice(0, 2)" class="presenter">
                        <span class="presenter-name">{{ presenter.name }}</span>
                        <span class="presenter-company" *ngIf="presenter.title">{{ presenter.title }}, </span>
                        <span class="presenter-company">{{ presenter.company }}</span>
                      </div>
                      <div *ngIf="content.presenters.length > 2" class="presenter-more">
                        +{{ content.presenters.length - 2 }} more
                      </div>
                    </div>

                    <div class="card-date">
                      {{ content.dateModified | date:'mediumDate' }}
                    </div>
                  </div>

                  <div class="card-tags">
                    <mat-chip-listbox aria-label="Tags" class="tag-list">
                      <mat-chip-option *ngFor="let tag of content.tags.slice(0, 3)" disableRipple selected="false" disabled>
                        {{ tag }}
                      </mat-chip-option>
                      <mat-chip-option *ngIf="content.tags.length > 3" disableRipple selected="false" disabled>
                        +{{ content.tags.length - 3 }}
                      </mat-chip-option>
                    </mat-chip-listbox>
                  </div>
                </mat-card-content>

                <mat-card-actions>
                  <button mat-button color="primary" [routerLink]="['/content-management/content', content.id]">VIEW DETAILS</button>
                  <button mat-button color="accent" *ngIf="content.status === 'review'" [routerLink]="['/content-management/review']">REVIEW</button>
                </mat-card-actions>
              </mat-card>
            </div>
          </div>
        </mat-drawer-content>
      </mat-drawer-container>
    </div>
  `,
  styles: [`
    /* Main container - takes full height minus header and footer */
    .home-container {
      height: 100%;
      width: 100%;
      overflow: auto;
    }

    /* Content container with drawer */
    .content-container {
      height: 100%;
      width: 100%;
      overflow: visible;
    }

    /* Main content area */
    .main-content {
      padding: 32px;
      overflow-y: auto;
      height: 100%;
      background-color: #f8f9fa;
    }

    /* Welcome section */
    .welcome-section {
      margin-bottom: 32px;
    }

    .welcome-text h1 {
      font-size: 28px;
      font-weight: 500;
      margin: 0 0 8px 0;
      color: #202124;
    }

    .welcome-text p {
      font-size: 16px;
      color: #5f6368;
      margin: 0;
    }

    /* Search and filter bar */
    .search-filter-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .search-container {
      flex: 1;
      max-width: 800px;
    }

    .search-field {
      width: 100%;
    }

    .filter-buttons {
      display: flex;
      gap: 12px;
    }

    /* Filter drawer */
    .filter-drawer {
      width: 280px;
      padding: 24px;
      background-color: white;
      border-left: 1px solid rgba(0, 0, 0, 0.08);
    }

    .filter-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .filter-header h2 {
      margin: 0;
      font-size: 18px;
      font-weight: 500;
      color: #202124;
    }

    .filter-search {
      margin-bottom: 24px;
    }

    .filter-search-field {
      width: 100%;
    }

    .filter-groups {
      margin-bottom: 24px;
    }

    .filter-options {
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding: 8px 0;
    }

    .filter-actions {
      padding-top: 16px;
      border-top: 1px solid rgba(0, 0, 0, 0.08);
    }

    .filter-actions button {
      width: 100%;
    }

    /* Carousel section */
    .carousel-section,
    .content-section {
      margin-bottom: 40px;
      position: relative;
    }

    .card-carousel-container {
      position: relative;
      display: flex;
      align-items: center;
      margin: 0 -8px;
    }

    .card-carousel {
      width: 100%;
      overflow: hidden;
      padding: 16px 0;
    }

    .card-carousel-track {
      display: flex;
      transition: transform 0.3s ease;
    }

    .carousel-card {
      flex: 0 0 calc(33.333% - 24px);
      margin: 0 12px;
      height: auto;
      min-height: 380px;
    }

    .carousel-nav-button {
      z-index: 2;
      background-color: white;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);

      &.prev-button {
        margin-left: 4px;
      }

      &.next-button {
        margin-right: 4px;
      }
    }

    .carousel-indicators {
      display: flex;
      justify-content: center;
      gap: 8px;
      margin-top: 16px;

      .carousel-indicator {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #e0e0e0;
        border: none;
        padding: 0;
        cursor: pointer;
        transition: background-color 0.3s ease;

        &.active {
          background-color: #1a73e8;
        }
      }
    }

    /* Content sections */
    .content-section {
      margin-bottom: 48px;
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .section-header h2 {
      font-size: 20px;
      font-weight: 500;
      margin: 0;
      color: #202124;
    }

    .view-all {
      color: #1a73e8;
      text-decoration: none;
      font-weight: 500;
      font-size: 14px;
    }

    .cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 16px;
    }

    /* Cards styling */
    .content-card {
      display: flex;
      flex-direction: column;
      background-color: white;
      border-radius: 12px;
      overflow: hidden;
      position: relative;
      transition: box-shadow 0.3s ease, transform 0.3s ease;
      height: 100%;
      border-top: 4px solid #1a73e8;

      &:hover {
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        transform: translateY(-4px);
      }

      &:nth-child(3n+1) {
        border-top-color: #1a73e8; /* Google blue */
      }

      &:nth-child(3n+2) {
        border-top-color: #ea4335; /* Google red */
      }

      &:nth-child(3n+3) {
        border-top-color: #34a853; /* Google green */
      }

      .card-badge {
        position: absolute;
        top: 12px;
        right: 12px;
        background-color: #ea4335;
        color: white;
        font-size: 11px;
        font-weight: 500;
        padding: 4px 8px;
        border-radius: 4px;
        z-index: 2;

        &.approved {
          background-color: #fbbc04;
        }

        &.published {
          background-color: #34a853;
        }
      }

      .card-track {
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        color: #1a73e8;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
        display: inline-block;
        padding: 4px 8px;
        background-color: rgba(26, 115, 232, 0.1);
        border-radius: 4px;
      }

      mat-card-content {
        flex-grow: 1;
        padding: 24px;

        .card-title {
          font-size: 18px;
          font-weight: 500;
          margin: 0 0 16px 0;
          line-height: 1.3;
          color: #202124;
        }

        .card-description {
          font-size: 14px;
          color: #5f6368;
          margin-bottom: 20px;
          line-height: 1.5;
        }

        .card-meta {
          display: flex;
          flex-direction: column;
          margin-bottom: 20px;
          padding-top: 16px;
          border-top: 1px solid rgba(0, 0, 0, 0.08);

          .presenters {
            display: flex;
            flex-direction: column;
            margin-bottom: 12px;

            .presenter {
              display: flex;
              flex-wrap: wrap;
              margin-bottom: 4px;

              .presenter-name {
                font-size: 13px;
                font-weight: 500;
                color: #202124;
                margin-right: 4px;
              }

              .presenter-company {
                font-size: 13px;
                color: #5f6368;
              }
            }

            .presenter-more {
              font-size: 12px;
              color: #5f6368;
              margin-top: 4px;
            }
          }

          .card-date {
            font-size: 12px;
            color: #9aa0a6;
            margin-top: 4px;
          }
        }

        .card-tags {
          ::ng-deep .mat-mdc-chip {
            min-height: 24px;
            font-size: 12px;
          }
        }
      }

      mat-card-actions {
        padding: 8px 24px 24px;
        display: flex;
        justify-content: space-between;
      }
    }

    /* Responsive styles */
    @media (max-width: 1200px) {
      .search-container {
        max-width: 600px;
      }

      .carousel-card {
        flex: 0 0 calc(50% - 24px);
      }
    }

    @media (max-width: 768px) {
      .search-filter-bar {
        flex-direction: column;
        align-items: flex-start;
        gap: 16px;
      }

      .search-container {
        width: 100%;
        max-width: none;
      }

      .filter-drawer {
        width: 240px;
      }

      .carousel-card {
        flex: 0 0 calc(100% - 24px);
      }
    }
  `]
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
    // In a real implementation, this would filter the actual data
    // For now, we'll just log the selected filters
    const selectedFilters = this.filters
      .map(filter => ({
        name: filter.name,
        selected: filter.options.filter(option => option.selected).map(option => option.label)
      }))
      .filter(filter => filter.selected.length > 0);

    console.log('Applied filters:', selectedFilters);
    console.log('Search query:', this.searchQuery);
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
