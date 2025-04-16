import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { ContentService } from '../../../../core/services/content.service';
import { Content, Asset } from '../../../../shared/models/content.model';

@Component({
  selector: 'app-content-view',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatChipsModule,
    MatDividerModule,
    MatTableModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="content-view-container">
      <div class="back-link">
        <button mat-icon-button (click)="goBack()">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <span>Back to {{ referrer || 'previous page' }}</span>
      </div>

      <div class="loading-spinner" *ngIf="loading">
        <mat-spinner diameter="40"></mat-spinner>
      </div>

      <div class="error-message" *ngIf="error">
        <h2>Error loading content</h2>
        <p>{{ error }}</p>
        <button mat-raised-button color="primary" (click)="goBack()">Go Back</button>
      </div>

      <div class="content-main" *ngIf="!loading && !error && content">
        <div class="content-left">
          <div class="content-header">
            <h1>{{ content.title }}</h1>

            <div class="tags-container">
              <div class="tag recommended" *ngIf="content.recommended">Recommended</div>
              <div class="tag priority" *ngIf="content.priority">Priority</div>
              <div class="tag new" *ngIf="isNewContent(content)">New</div>
              <ng-container *ngFor="let tag of content.tags">
                <div class="tag" [ngClass]="getTagClass(tag)">{{ tag }}</div>
              </ng-container>
            </div>
          </div>

          <div class="abstract-section" *ngIf="content.abstract || content.description">
            <div class="section-content">
              <h2>Abstract</h2>
              <p class="abstract-text">
                {{ content.abstract || content.description }}
              </p>
            </div>
          </div>

          <div class="assets-section" *ngIf="content.assets && content.assets.length > 0">
            <div class="section-content">
              <h2>Assets</h2>
              <div class="assets-table-wrapper">
                <table class="assets-table">
                  <thead>
                    <tr>
                      <th class="asset-column">Asset</th>
                      <th class="type-column">Type</th>
                      <th class="actions-column"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr *ngFor="let asset of content.assets">
                      <td class="asset-column">{{ asset.name }}</td>
                      <td class="type-column">{{ asset.type }}</td>
                      <td class="actions-column">
                        <a [href]="asset.url" target="_blank" *ngIf="asset.url && asset.url !== '#'" mat-icon-button>
                          <mat-icon>open_in_new</mat-icon>
                        </a>
                        <button mat-icon-button *ngIf="!asset.url || asset.url === '#'">
                          <mat-icon>bookmark_border</mat-icon>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div class="ai-summary-section" *ngIf="content.aiSummary">
            <div class="section-content ai-gradient">
              <div class="ai-header">
                <h2>AI Summary</h2>
                <div class="ai-icon">
                  <mat-icon>smart_toy</mat-icon>
                </div>
              </div>
              <p class="ai-text">{{ content.aiSummary }}</p>
            </div>
          </div>
        </div>

        <div class="content-right">
          <div class="info-card">
            <div class="info-card-header">
              <h3>Details</h3>
            </div>
            <div class="info-card-content">
              <div class="info-row">
                <div class="info-label">ID</div>
                <div class="info-value highlight-value">{{ content.id }}</div>
              </div>
              <div class="info-row">
                <div class="info-label">Track</div>
                <div class="info-value highlight-value">{{ content.track }}</div>
              </div>
              <div class="info-row">
                <div class="info-label">Session Type</div>
                <div class="info-value highlight-value">{{ content.sessionType }}</div>
              </div>
              <div class="info-row" *ngIf="content.sessionDate">
                <div class="info-label">Session Date</div>
                <div class="info-value highlight-value">{{ formatDate(content.sessionDate) }}</div>
              </div>
              <div class="info-row" *ngIf="content.learningLevel">
                <div class="info-label">Learning Level</div>
                <div class="info-value highlight-value">{{ content.learningLevel }}</div>
              </div>
              <div class="info-row">
                <div class="info-label">Status</div>
                <div class="info-value status-value" [ngClass]="getStatusClass(content.status || '')">
                  {{ content.status || 'Draft' }}
                </div>
              </div>
            </div>
          </div>

          <div class="info-card" *ngIf="content.presenters && content.presenters.length > 0">
            <div class="info-card-header">
              <h3>Presenters</h3>
            </div>
            <div class="info-card-content">
              <div class="presenter" *ngFor="let presenter of content.presenters">
                <div class="presenter-name">{{ presenter.name }}</div>
                <div class="presenter-details">{{ presenter.title }}, {{ presenter.company }}</div>
              </div>
            </div>
          </div>

          <div class="info-card">
            <div class="info-card-header">
              <h3>Dates</h3>
            </div>
            <div class="info-card-content">
              <div class="info-row">
                <div class="info-label">Created</div>
                <div class="info-value highlight-value">{{ formatDate(content.dateCreated || '') }}</div>
              </div>
              <div class="info-row">
                <div class="info-label">Last Modified</div>
                <div class="info-value highlight-value">{{ formatDate(content.dateModified || '') }}</div>
              </div>
            </div>
          </div>

          <!-- Related Content Card -->
          <div class="info-card" *ngIf="relatedContent && relatedContent.length > 0">
            <div class="info-card-header">
              <h3>Related Content</h3>
            </div>
            <div class="info-card-content">
              <div class="related-item" *ngFor="let item of relatedContent">
                <a [routerLink]="['/content', item.id]" class="related-link">
                  <div class="related-title">{{ item.title }}</div>
                  <div class="related-meta">{{ item.sessionType }} | {{ formatDate(item.sessionDate || '') }}</div>
                </a>
              </div>
            </div>
          </div>

          <!-- Actions card -->
          <div class="actions-card">
            <button mat-raised-button color="primary" class="action-button">
              <mat-icon>edit</mat-icon> Edit Content
            </button>
            <button mat-stroked-button class="action-button">
              <mat-icon>published_with_changes</mat-icon> Submit for Review
            </button>
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

    .content-view-container {
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px;
      color: #202124;
    }

    .back-link {
      display: flex;
      align-items: center;
      margin-bottom: 24px;
      color: #5f6368;
      font-size: 14px;
      cursor: pointer;
    }

    .back-link button {
      margin-right: 8px;
    }

    .loading-spinner {
      display: flex;
      justify-content: center;
      padding: 80px 0;
    }

    .error-message {
      text-align: center;
      padding: 60px 0;
    }

    .error-message h2 {
      color: #d93025;
      margin-bottom: 16px;
    }

    .error-message p {
      margin-bottom: 24px;
      color: #5f6368;
    }

    .content-main {
      display: flex;
      gap: 32px;
    }

    .content-left {
      flex: 1;
      min-width: 0;
    }

    .content-right {
      width: 350px;
      flex-shrink: 0;
    }

    .content-header {
      margin-bottom: 32px;
    }

    h1 {
      font-size: 32px;
      font-weight: 400;
      line-height: 1.3;
      letter-spacing: -0.2px;
      margin: 0 0 24px 0;
      color: #202124;
      text-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    h2 {
      font-size: 20px;
      font-weight: 500;
      margin: 0 0 16px 0;
      color: #202124;
    }

    h3 {
      font-size: 16px;
      font-weight: 500;
      margin: 0;
      color: #202124;
    }

    .tags-container {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .tag {
      display: inline-flex;
      align-items: center;
      height: 28px;
      font-size: 12px;
      padding: 0 14px;
      border-radius: 14px;
      letter-spacing: 0.2px;
      font-weight: 500;
      background-color: #f1f3f4;
      color: #5f6368;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .tag:hover {
      transform: translateY(-1px);
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .tag.recommended {
      background-color: #e6f4ea;
      color: #137333;
    }

    .tag.priority {
      background-color: #fce8e6;
      color: #c5221f;
    }

    .tag.new {
      background-color: #e8f0fe;
      color: #1a73e8;
    }

    .tag.ai, .tag.ml, .tag.genai {
      background-color: #e8f0fe;
      color: #1a73e8;
    }

    .tag.cloud {
      background-color: #e6f4ea;
      color: #137333;
    }

    .tag.security {
      background-color: #fce8e6;
      color: #c5221f;
    }

    .abstract-section, .assets-section, .ai-summary-section {
      margin-bottom: 32px;
    }

    .section-content {
      background-color: #fff;
      border-radius: 12px;
      border: 1px solid #dadce0;
      padding: 28px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.05);
      transition: box-shadow 0.3s ease;
    }

    .section-content:hover {
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .abstract-text {
      font-size: 16px;
      line-height: 1.6;
      color: #3c4043;
      margin: 0;
      letter-spacing: 0.1px;
    }

    .ai-gradient {
      background: linear-gradient(to right bottom, #ffffff, #f8fbff);
      border-color: #e8f0fe;
    }

    .ai-header {
      display: flex;
      align-items: center;
      margin-bottom: 16px;
    }

    .ai-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-left: 12px;
      color: #1a73e8;
    }

    .ai-text {
      font-size: 16px;
      line-height: 1.6;
      color: #3c4043;
      margin: 0;
      font-style: italic;
      letter-spacing: 0.1px;
      position: relative;
      padding-left: 12px;
      border-left: 2px solid #e8f0fe;
    }

    .info-card {
      background-color: #fff;
      border-radius: 12px;
      border: 1px solid #dadce0;
      margin-bottom: 24px;
      overflow: hidden;
      box-shadow: 0 2px 6px rgba(0,0,0,0.05);
      transition: box-shadow 0.3s ease;
    }

    .info-card:hover {
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .info-card-header {
      padding: 16px 24px;
      border-bottom: 1px solid #dadce0;
      background-color: #f8f9fa;
    }

    .info-card-content {
      padding: 16px 24px;
    }

    .info-row {
      display: flex;
      margin-bottom: 16px;
      align-items: center;
    }

    .info-row:last-child {
      margin-bottom: 0;
    }

    .info-label {
      width: 45%;
      font-size: 14px;
      color: #5f6368;
      font-weight: 500;
    }

    .info-value {
      width: 55%;
      font-size: 14px;
      color: #202124;
      font-weight: 500;
    }

    .highlight-value {
      color: #3c4043;
      background-color: #f8f9fa;
      padding: 6px 12px;
      border-radius: 4px;
      border-left: 3px solid #1a73e8;
    }

    .status-value {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
      color: #fff;
      background-color: #9aa0a6;
    }

    .status-value.draft {
      background-color: #9aa0a6;
    }

    .status-value.pending {
      background-color: #f29900;
    }

    .status-value.approved {
      background-color: #1e8e3e;
    }

    .status-value.published {
      background-color: #1a73e8;
    }

    .presenter {
      margin-bottom: 16px;
      padding: 12px;
      border-radius: 8px;
      transition: background-color 0.2s;
    }

    .presenter:hover {
      background-color: #f8f9fa;
    }

    .presenter:last-child {
      margin-bottom: 0;
    }

    .presenter-name {
      font-size: 14px;
      font-weight: 500;
      color: #202124;
      margin-bottom: 4px;
    }

    .presenter-details {
      font-size: 12px;
      color: #5f6368;
    }

    .related-item {
      margin-bottom: 16px;
      padding: 12px;
      border-radius: 8px;
      transition: background-color 0.2s;
    }

    .related-item:hover {
      background-color: #f1f8ff;
    }

    .related-item:last-child {
      margin-bottom: 0;
    }

    .related-link {
      text-decoration: none;
      display: block;
    }

    .related-title {
      font-size: 14px;
      font-weight: 500;
      color: #1a73e8;
      margin-bottom: 4px;
    }

    .related-meta {
      font-size: 12px;
      color: #5f6368;
    }

    .actions-card {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .action-button {
      width: 100%;
      height: 44px;
      border-radius: 22px;
      font-weight: 500;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .action-button:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    .assets-table-wrapper {
      border-radius: 8px;
      overflow: hidden;
      background-color: #fff;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .assets-table {
      width: 100%;
      border-collapse: collapse;
    }

    .assets-table th {
      text-align: left;
      padding: 16px 24px;
      font-size: 14px;
      font-weight: 500;
      color: #5f6368;
      background-color: #f8f9fa;
      border-bottom: 1px solid #dadce0;
    }

    .assets-table td {
      padding: 16px 24px;
      font-size: 14px;
      color: #3c4043;
      border-bottom: 1px solid #eee;
    }

    .assets-table tr {
      transition: background-color 0.2s;
    }

    .assets-table tr:hover {
      background-color: #f8f9fa;
    }

    .assets-table tr:last-child td {
      border-bottom: none;
    }

    .asset-column {
      width: 70%;
    }

    .type-column {
      width: 20%;
    }

    .actions-column {
      width: 10%;
      text-align: right;
    }

    @media (max-width: 1024px) {
      .content-main {
        flex-direction: column;
      }

      .content-right {
        width: 100%;
      }
    }

    @media (max-width: 768px) {
      .content-view-container {
        padding: 16px;
      }

      h1 {
        font-size: 24px;
      }

      .assets-table th, .assets-table td {
        padding: 12px 16px;
      }

      .section-content {
        padding: 20px;
      }
    }
  `]
})
export class ContentViewComponent implements OnInit {
  contentId: string | null = null;
  content: Content | null = null;
  relatedContent: Content[] = [];
  loading: boolean = true;
  error: string | null = null;
  referrer: string = 'search results';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private contentService: ContentService
  ) {}

  ngOnInit(): void {
    // Get the content ID from the route parameters
    this.route.paramMap.subscribe(params => {
      this.contentId = params.get('contentId');
      if (this.contentId) {
        this.loadContent(this.contentId);
      } else {
        this.error = 'No content ID provided';
        this.loading = false;
      }
    });

    // Try to determine where the user came from
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.previousNavigation) {
      const previousUrl = navigation.previousNavigation.finalUrl?.toString() || '';
      if (previousUrl.includes('search')) {
        this.referrer = 'search results';
      } else if (previousUrl.includes('home')) {
        this.referrer = 'home';
      } else if (previousUrl.includes('content-management')) {
        this.referrer = 'content management';
      }
    }
  }

  loadContent(id: string): void {
    this.loading = true;
    this.error = null;

    this.contentService.getContent(id).subscribe({
      next: (content) => {
        this.content = content;
        this.loading = false;
        if (!content) {
          this.error = `Content with ID ${id} not found`;
        } else {
          // Load related content
          this.loadRelatedContent(content);
        }
      },
      error: (err) => {
        console.error('Error loading content:', err);
        this.error = 'Failed to load content. Please try again later.';
        this.loading = false;
      }
    });
  }

  loadRelatedContent(content: Content): void {
    // In a real app, this would be a service call with proper parameters
    // For now, we'll simulate it with dummy data
    // Implementation would use content.tags, content.track, etc. to find related items

    // Sample related content - would come from a service in a real app
    this.relatedContent = [
      {
        id: 'rel-1',
        title: 'Advanced Machine Learning on Google Cloud',
        sessionType: 'Workshop',
        sessionDate: '2025-04-16',
        tags: ['AI', 'Cloud']
      },
      {
        id: 'rel-2',
        title: 'Optimizing Cloud Applications for Scale',
        sessionType: 'Session',
        sessionDate: '2025-04-17',
        tags: ['Performance', 'Cloud']
      },
      {
        id: 'rel-3',
        title: 'Security Best Practices for Cloud Applications',
        sessionType: 'Breakout',
        sessionDate: '2025-04-15',
        tags: ['Security', 'Best Practices']
      }
    ] as any[];
  }

  goBack(): void {
    // Check if there's a previous navigation state to go back to
    if (window.history.length > 1) {
      window.history.back();
    } else {
      // Fallback to search page if there's no history
      this.router.navigate(['/search']);
    }
  }

  formatDate(dateString: string | Date): string {
    if (!dateString) return 'N/A';

    const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  getTagClass(tag: string): string {
    const tagLower = tag.toLowerCase();

    if (tagLower.includes('ai') || tagLower.includes('ml') || tagLower.includes('machine learning')) {
      return 'ai';
    } else if (tagLower.includes('cloud')) {
      return 'cloud';
    } else if (tagLower.includes('security')) {
      return 'security';
    }

    return '';
  }

  getStatusClass(status: string): string {
    const statusLower = status.toLowerCase();
    if (statusLower.includes('draft')) {
      return 'draft';
    } else if (statusLower.includes('pending') || statusLower.includes('review')) {
      return 'pending';
    } else if (statusLower.includes('approved')) {
      return 'approved';
    } else if (statusLower.includes('published')) {
      return 'published';
    }
    return 'draft';
  }

  isNewContent(content: Content): boolean {
    if (!content.dateCreated) return false;

    const createdDate = new Date(content.dateCreated);
    const now = new Date();
    const daysDiff = Math.floor((now.getTime() - createdDate.getTime()) / (1000 * 60 * 60 * 24));

    return daysDiff <= 7; // Consider content new if it's less than 7 days old
  }
}
