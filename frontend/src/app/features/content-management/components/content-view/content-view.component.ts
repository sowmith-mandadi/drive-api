import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatTabsModule } from '@angular/material/tabs';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-content-view',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatChipsModule,
    MatTabsModule,
    MatFormFieldModule,
    MatInputModule,
    RouterLink
  ],
  template: `
    <div class="content-view-container">
      <div class="header">
        <button mat-icon-button routerLink="/">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1>Content Details</h1>
      </div>
      
      <mat-card class="content-details">
        <mat-card-header>
          <mat-card-title>Introduction to Angular 19</mat-card-title>
          <mat-card-subtitle>Web Development • Presentation</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <p class="description">
            Learn about the new features in Angular 19 including standalone components, 
            the new reactivity system with signals, and built-in control flow.
          </p>
          
          <div class="metadata">
            <div class="metadata-item">
              <span class="label">Author:</span>
              <span class="value">Jane Smith</span>
            </div>
            <div class="metadata-item">
              <span class="label">Date:</span>
              <span class="value">April 1, 2025</span>
            </div>
            <div class="metadata-item">
              <span class="label">Tags:</span>
              <mat-chip-set>
                <mat-chip>Angular</mat-chip>
                <mat-chip>TypeScript</mat-chip>
                <mat-chip>Web Development</mat-chip>
              </mat-chip-set>
            </div>
          </div>
          
          <mat-tab-group>
            <mat-tab label="Content">
              <div class="content-preview">
                <p>This is a placeholder for the actual content preview.</p>
                <p>In a real application, this would display a PDF viewer, video player, 
                  or other appropriate content viewer based on the file type.</p>
              </div>
            </mat-tab>
            <mat-tab label="AI Summary">
              <div class="ai-summary">
                <p>This presentation introduces Angular 19, focusing on three major features:</p>
                <ol>
                  <li><strong>Standalone Components</strong>: Simplified component architecture that 
                    eliminates the need for NgModules, making components more portable and 
                    reducing boilerplate.</li>
                  <li><strong>Signals</strong>: A new reactive primitive that provides fine-grained 
                    reactivity, better developer experience, and improved performance over 
                    traditional RxJS observables for component state.</li>
                  <li><strong>Built-in Control Flow</strong>: New template syntax that replaces 
                    NgIf/NgFor with native Angular control flow blocks, resulting in better 
                    type safety and performance.</li>
                </ol>
                <p>The presentation includes code examples and performance comparisons with 
                  previous Angular versions.</p>
              </div>
            </mat-tab>
            <mat-tab label="Q&A">
              <div class="qa-section">
                <p>Ask a question about this content:</p>
                <mat-form-field class="full-width">
                  <input matInput placeholder="What is the advantage of signals over observables?">
                </mat-form-field>
                <button mat-raised-button color="primary">Ask</button>
                
                <div class="qa-placeholder">
                  <p>This section would allow users to ask questions about the content 
                    and receive AI-generated answers based on the content.</p>
                </div>
              </div>
            </mat-tab>
          </mat-tab-group>
        </mat-card-content>
        <mat-card-actions>
          <button mat-raised-button color="primary">
            <mat-icon>download</mat-icon>
            Download
          </button>
          <button mat-button>
            <mat-icon>comment</mat-icon>
            Add Comment
          </button>
          <button mat-button>
            <mat-icon>share</mat-icon>
            Share
          </button>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [`
    .content-view-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
    }
    
    .header {
      display: flex;
      align-items: center;
      margin-bottom: 2rem;
    }
    
    h1 {
      margin: 0;
      font-size: 2rem;
      margin-left: 1rem;
    }
    
    .content-details {
      margin-bottom: 2rem;
    }
    
    .description {
      font-size: 1.1rem;
      line-height: 1.5;
      margin-bottom: 2rem;
    }
    
    .metadata {
      margin-bottom: 2rem;
    }
    
    .metadata-item {
      margin-bottom: 1rem;
      display: flex;
      align-items: flex-start;
      
      .label {
        font-weight: 500;
        min-width: 80px;
      }
    }
    
    mat-tab-group {
      margin-bottom: 2rem;
    }
    
    .content-preview, .ai-summary, .qa-section {
      padding: 1.5rem 0;
    }
    
    .full-width {
      width: 100%;
    }
    
    .qa-placeholder {
      margin-top: 2rem;
      padding: 1rem;
      background-color: #f5f5f5;
      border-radius: 4px;
    }
    
    mat-card-actions {
      padding: 16px;
    }
  `]
})
export class ContentViewComponent {} 