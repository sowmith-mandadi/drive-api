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
            <div class="header-main">
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
          </div>

          <div class="action-bar">
            <div class="action-buttons">
              <button mat-stroked-button class="action-button share-button">
                <mat-icon>share</mat-icon> Share
              </button>
              <button mat-stroked-button class="action-button feedback-button">
                <mat-icon>feedback</mat-icon> Provide Feedback
              </button>
            </div>
          </div>

          <div class="abstract-section" *ngIf="content.abstract || content.description">
            <div class="section-content">
              <h2>Abstract</h2>
              <p class="abstract-text">
                {{ abstractExpanded ? (content.abstract || content.description) : ((content.abstract || content.description) | slice:0:300) }}
                <span *ngIf="!abstractExpanded && (content.abstract || content.description).length > 300">...</span>
              </p>
              <button
                *ngIf="(content.abstract || content.description).length > 300"
                class="show-more-btn"
                (click)="abstractExpanded = !abstractExpanded">
                {{ abstractExpanded ? 'Show less' : 'Show more' }}
              </button>
            </div>
          </div>

          <div class="ai-summary-section" *ngIf="content.aiSummary">
            <div class="section-content ai-gradient">
              <div class="ai-header">
                <h2>AI Summary</h2>
                <div class="ai-controls">
                  <div class="ai-icon">
                    <mat-icon>smart_toy</mat-icon>
                  </div>
                  <button mat-icon-button class="collapse-button" (click)="toggleAiSummary()" *ngIf="showAiSummary">
                    <mat-icon>expand_less</mat-icon>
                  </button>
                  <button mat-icon-button class="collapse-button" (click)="toggleAiSummary()" *ngIf="!showAiSummary">
                    <mat-icon>expand_more</mat-icon>
                  </button>
                </div>
              </div>
              <div *ngIf="showAiSummary">
                <p class="ai-text">{{ content.aiSummary }}</p>
              </div>
              <button
                *ngIf="!showAiSummary"
                class="show-more-btn"
                (click)="toggleAiSummary()">
                Show AI Summary
              </button>
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

          <div class="notes-section">
            <div class="section-content">
              <h2>Notes/Comments</h2>
              <p class="notes-text">
                Any comments or notes put by the content creator that can help end users understand where the crucial points of the asset are, or any other piece of information that can be useful.
              </p>
              <div class="comments-container" *ngIf="content.comments && content.comments.length > 0">
                <div class="comment" *ngFor="let comment of content.comments">
                  <div class="comment-header">
                    <span class="comment-author">{{ comment.userName }}</span>
                    <span class="comment-date">{{ formatDate(comment.timestamp) }}</span>
                  </div>
                  <p class="comment-text">{{ comment.text }}</p>
                </div>
              </div>
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
                <div class="info-label">Session ID</div>
                <div class="info-value highlight-value">{{ content.id }}</div>
              </div>
              <div class="info-row" *ngIf="content.dateCreated">
                <div class="info-label">Date of Creation</div>
                <div class="info-value highlight-value">{{ formatDate(content.dateCreated) }}</div>
              </div>
              <div class="info-row">
                <div class="info-label">Track</div>
                <div class="info-value highlight-value">{{ content.track }}</div>
              </div>
              <div class="info-row" *ngIf="content.industry">
                <div class="info-label">Industry</div>
                <div class="info-value highlight-value">{{ content.industry }}</div>
              </div>
              <div class="info-row" *ngIf="content.sessionType">
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

          <div class="info-card" *ngIf="content.jobRole || content.areaOfInterest || content.topic">
            <div class="info-card-header">
              <h3>Additional Information</h3>
            </div>
            <div class="info-card-content">
              <div class="info-row" *ngIf="content.jobRole">
                <div class="info-label">Job Role</div>
                <div class="info-value highlight-value">{{ content.jobRole }}</div>
              </div>
              <div class="info-row" *ngIf="content.areaOfInterest">
                <div class="info-label">Area of Interest</div>
                <div class="info-value highlight-value">{{ content.areaOfInterest }}</div>
              </div>
              <div class="info-row" *ngIf="content.topic">
                <div class="info-label">Topic</div>
                <div class="info-value highlight-value">{{ content.topic }}</div>
              </div>
            </div>
          </div>

          <div class="info-card" *ngIf="content.assets && content.assets.length > 0">
            <div class="info-card-header">
              <h3>Resources/Supplementals</h3>
            </div>
            <div class="info-card-content">
              <div class="resource-link" *ngFor="let asset of content.assets">
                <a [href]="asset.url" target="_blank" class="resource-item">
                  <span class="resource-name">{{ asset.name }}</span>
                  <mat-icon class="resource-icon">open_in_new</mat-icon>
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
      margin-bottom: 16px;
    }

    .action-bar {
      display: flex;
      justify-content: flex-end;
      margin-bottom: 32px;
    }

    .header-main {
      flex: 1;
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

    .abstract-section, .assets-section, .ai-summary-section, .notes-section {
      margin-bottom: 32px;
    }

    .ai-summary-container {
      margin-bottom: 32px;
    }

    .ai-summary-toggle {
      height: 44px;
      padding: 0 24px;
      font-size: 14px;
      font-weight: 500;
      color: #1a73e8;
      background-color: #fff;
      border: 1px solid #dadce0;
      border-radius: 22px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin: 0 auto;
      transition: background-color 0.2s;
    }

    .ai-summary-toggle:hover {
      background-color: #f8f9fa;
    }

    .show-more-btn {
      background: none;
      border: none;
      padding: 0;
      font-size: 14px;
      font-weight: 500;
      color: #1a73e8;
      cursor: pointer;
      margin-top: 8px;
    }

    .show-more-btn:hover {
      text-decoration: underline;
    }

    .action-buttons {
      display: flex;
      gap: 12px;
    }

    .action-button {
      height: 36px;
      padding: 0 16px;
      font-weight: 500;
      font-size: 14px;
      border-radius: 18px;
      background-color: #fff;
      color: #1a73e8;
      border: 1px solid #dadce0;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .action-button:hover {
      background-color: #f8f9fa;
    }

    .action-button mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
      color: #1a73e8;
    }

    .share-button {
      color: #34a853; /* Google green */
      border-color: #34a853;
    }

    .share-button mat-icon {
      color: #34a853; /* Google green */
    }

    .feedback-button {
      color: #4285f4; /* Google blue */
      border-color: #4285f4;
    }

    .feedback-button mat-icon {
      color: #4285f4; /* Google blue */
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
      justify-content: space-between;
      margin-bottom: 16px;
    }

    .ai-controls {
      display: flex;
      align-items: center;
    }

    .ai-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 8px;
      color: #1a73e8;
    }

    .collapse-button {
      color: #5f6368;
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
      border-left: 3px solid #dadce0;
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

    .notes-text {
      font-size: 14px;
      line-height: 1.5;
      color: #5f6368;
      margin: 0 0 16px 0;
    }

    .comments-container {
      margin-top: 16px;
    }

    .comment {
      padding: 12px;
      background-color: #f8f9fa;
      border-radius: 8px;
      margin-bottom: 12px;
    }

    .comment-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
    }

    .comment-author {
      font-weight: 500;
      font-size: 14px;
      color: #202124;
    }

    .comment-date {
      font-size: 12px;
      color: #5f6368;
    }

    .comment-text {
      font-size: 14px;
      line-height: 1.5;
      color: #3c4043;
      margin: 0;
    }

    .resource-link {
      margin-bottom: 12px;
    }

    .resource-link:last-child {
      margin-bottom: 0;
    }

    .resource-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: #3c4043;
      text-decoration: none;
      padding: 8px 12px;
      border-radius: 4px;
      transition: background-color 0.2s;
    }

    .resource-item:hover {
      background-color: #f1f3f4;
    }

    .resource-name {
      font-size: 14px;
    }

    .resource-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
      color: #5f6368;
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

      .action-bar {
        margin-bottom: 24px;
      }
    }
  `]
})
export class ContentViewComponent implements OnInit {
  contentId: string | null = null;
  content: Content | null = null;
  loading: boolean = true;
  error: string | null = null;
  referrer: string = 'search results';
  abstractExpanded: boolean = false;
  showAiSummary: boolean = false;

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
        }
      },
      error: (err) => {
        console.error('Error loading content:', err);
        this.error = 'Failed to load content. Please try again later.';
        this.loading = false;
      }
    });
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

  isNewContent(content: Content): boolean {
    if (!content.dateCreated) return false;

    const createdDate = new Date(content.dateCreated);
    const now = new Date();
    const daysDiff = Math.floor((now.getTime() - createdDate.getTime()) / (1000 * 60 * 60 * 24));

    return daysDiff <= 7; // Consider content new if it's less than 7 days old
  }

  toggleAiSummary(): void {
    this.showAiSummary = !this.showAiSummary;
  }
}
