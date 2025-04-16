import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterModule } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';

@Component({
  selector: 'app-single-upload',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    RouterModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatProgressBarModule
  ],
  template: `
    <div class="upload-container">
      <div class="header">
        <button mat-icon-button routerLink="/content-management">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1>Upload Content</h1>
      </div>

      <mat-card class="upload-form-card">
        <mat-card-content>
          <form [formGroup]="uploadForm">
            <div class="form-section">
              <h2>Content Information</h2>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Title</mat-label>
                <input matInput formControlName="title" placeholder="Enter content title">
                <mat-error *ngIf="uploadForm.get('title')?.hasError('required')">
                  Title is required
                </mat-error>
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Description</mat-label>
                <textarea matInput formControlName="description" placeholder="Enter content description" rows="4"></textarea>
              </mat-form-field>

              <div class="form-row">
                <mat-form-field appearance="outline">
                  <mat-label>Type</mat-label>
                  <mat-select formControlName="type">
                    <mat-option value="presentation">Presentation</mat-option>
                    <mat-option value="document">Document</mat-option>
                    <mat-option value="video">Video</mat-option>
                    <mat-option value="audio">Audio</mat-option>
                  </mat-select>
                  <mat-error *ngIf="uploadForm.get('type')?.hasError('required')">
                    Type is required
                  </mat-error>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Track</mat-label>
                  <mat-select formControlName="track">
                    <mat-option value="infrastructure">Infrastructure</mat-option>
                    <mat-option value="data-analytics">Data & Analytics</mat-option>
                    <mat-option value="ai-ml">AI & Machine Learning</mat-option>
                    <mat-option value="security">Security</mat-option>
                    <mat-option value="app-dev">Application Development</mat-option>
                  </mat-select>
                </mat-form-field>
              </div>
            </div>

            <div class="form-section">
              <h2>File Upload</h2>
              <div class="file-drop-area">
                <div class="drop-message">
                  <mat-icon class="upload-icon">cloud_upload</mat-icon>
                  <p>Drag and drop files here or click to browse</p>
                  <button mat-raised-button color="primary" type="button">
                    <mat-icon>attach_file</mat-icon>
                    Choose File
                  </button>
                </div>
              </div>
            </div>

            <div class="form-actions">
              <button mat-button routerLink="/content-management">Cancel</button>
              <button mat-raised-button color="primary" type="submit" [disabled]="uploadForm.invalid">
                <mat-icon>cloud_upload</mat-icon>
                Upload Content
              </button>
            </div>
          </form>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .upload-container {
      @apply max-w-4xl mx-auto p-6;
    }

    .header {
      @apply flex items-center mb-6;

      h1 {
        @apply m-0 text-2xl font-semibold ml-2;
      }
    }

    .upload-form-card {
      @apply mb-8;
    }

    .form-section {
      @apply mb-8;

      h2 {
        @apply text-xl font-medium mb-4 pb-2 border-b border-gray-200;
      }
    }

    .full-width {
      @apply w-full;
    }

    .form-row {
      @apply grid grid-cols-1 md:grid-cols-2 gap-4;
    }

    .file-drop-area {
      @apply border-2 border-dashed border-gray-300 rounded-lg p-8 mb-6 bg-gray-50 flex justify-center items-center;
      min-height: 200px;
    }

    .drop-message {
      @apply text-center;

      .upload-icon {
        @apply text-5xl text-gray-400 mb-4;
        font-size: 64px;
        width: 64px;
        height: 64px;
      }

      p {
        @apply mb-4 text-gray-600;
      }
    }

    .form-actions {
      @apply flex justify-end gap-4;
    }
  `]
})
export class SingleUploadComponent {
  uploadForm: FormGroup;

  constructor(private fb: FormBuilder) {
    this.uploadForm = this.fb.group({
      title: ['', Validators.required],
      description: [''],
      type: ['presentation', Validators.required],
      track: ['infrastructure'],
      file: [null]
    });
  }
}
