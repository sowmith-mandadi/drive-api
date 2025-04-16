import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterModule } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatStepperModule } from '@angular/material/stepper';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatCardModule } from '@angular/material/card';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
  selector: 'app-bulk-upload',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    RouterModule,
    MatButtonModule,
    MatIconModule,
    MatStepperModule,
    MatProgressBarModule,
    MatCardModule,
    MatTooltipModule
  ],
  template: `
    <div class="bulk-upload-container">
      <div class="header">
        <button mat-icon-button routerLink="/content-management">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1>Bulk Upload Content</h1>
      </div>

      <mat-card class="instructions-card">
        <mat-card-content>
          <h2>
            <mat-icon>info</mat-icon>
            Instructions
          </h2>
          <p>Upload multiple content items at once by following these steps:</p>
          <ol>
            <li>Download our Excel template</li>
            <li>Fill in the content details</li>
            <li>Upload the filled template</li>
            <li>Review and submit</li>
          </ol>
          <div class="template-actions">
            <button mat-raised-button color="primary">
              <mat-icon>download</mat-icon>
              Download Template
            </button>
          </div>
        </mat-card-content>
      </mat-card>

      <div class="upload-section">
        <p>Ready to upload your filled template? Drag and drop your file here or click to browse.</p>
        <button mat-raised-button color="accent" routerLink="/content-management/review">
          <mat-icon>upload_file</mat-icon>
          Upload Excel File
        </button>
      </div>
    </div>
  `,
  styles: [`
    .bulk-upload-container {
      @apply max-w-5xl mx-auto p-6;
    }

    .header {
      @apply flex items-center mb-6;

      h1 {
        @apply m-0 text-2xl font-semibold ml-2;
      }
    }

    .instructions-card {
      @apply mb-8;

      h2 {
        @apply flex items-center text-xl font-medium mb-4;

        mat-icon {
          @apply mr-2 text-blue-500;
        }
      }

      ol {
        @apply pl-5 my-4;

        li {
          @apply mb-2;
        }
      }
    }

    .template-actions {
      @apply mt-6;
    }

    .upload-section {
      @apply text-center p-8 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50;

      p {
        @apply mb-4;
      }
    }
  `]
})
export class BulkUploadComponent {}
