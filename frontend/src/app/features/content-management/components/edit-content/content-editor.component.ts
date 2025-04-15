import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { ReactiveFormsModule } from '@angular/forms';

import { ConferenceContentService } from '../../services/conference-content.service';
import {
  ConferenceSchema,
  ConferenceContent,
  ContentTypeDefinition
} from '../../models/conference.model';
import { DynamicContentFormComponent } from './dynamic-content-form.component';

@Component({
  selector: 'app-content-editor',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    MatSelectModule,
    MatButtonModule,
    MatCardModule,
    MatProgressBarModule,
    MatFormFieldModule,
    MatInputModule,
    DynamicContentFormComponent
  ],
  template: `
    <div class="content-editor">
      <div class="editor-header">
        <h1>{{ isEditMode ? 'Edit' : 'Create' }} Content</h1>
        <button mat-button (click)="navigateBack()">Back</button>
      </div>

      <div class="error-message" *ngIf="error">
        <mat-error>{{ error }}</mat-error>
      </div>

      <mat-progress-bar *ngIf="loading" mode="indeterminate"></mat-progress-bar>

      <ng-container *ngIf="!loading && !error">
        <!-- Content Type Selection (only for create mode) -->
        <mat-card *ngIf="!isEditMode && conferenceSchema" class="type-selection-card">
          <mat-card-header>
            <mat-card-title>Select Content Type</mat-card-title>
          </mat-card-header>

          <mat-card-content>
            <mat-form-field appearance="fill" class="full-width">
              <mat-label>Content Type</mat-label>
              <mat-select [(value)]="selectedContentTypeId" (selectionChange)="onContentTypeChange()">
                <mat-option *ngFor="let type of conferenceSchema.contentTypes" [value]="type.id">
                  {{ type.displayName }}
                </mat-option>
              </mat-select>
            </mat-form-field>

            <p *ngIf="selectedContentType && selectedContentType.description" class="type-description">
              {{ selectedContentType.description }}
            </p>
          </mat-card-content>
        </mat-card>

        <!-- Dynamic Content Form -->
        <app-dynamic-content-form
          *ngIf="showForm"
          [conferenceSchema]="conferenceSchema"
          [contentItem]="contentItem"
          [contentTypeId]="selectedContentTypeId"
          (formSubmit)="onFormSubmit($event)">
        </app-dynamic-content-form>
      </ng-container>
    </div>
  `,
  styles: [`
    .content-editor {
      padding: 1rem;

      .editor-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;

        h1 {
          margin: 0;
          font-size: 1.8rem;
        }
      }

      .error-message {
        margin-bottom: 1rem;
      }

      .type-selection-card {
        margin-bottom: 1.5rem;
      }

      .full-width {
        width: 100%;
      }

      .type-description {
        margin-top: 0.5rem;
        color: rgba(0, 0, 0, 0.6);
      }
    }
  `]
})
export class ContentEditorComponent implements OnInit {
  conferenceId: string = '';
  contentId: string = '';
  isEditMode = false;

  conferenceSchema!: ConferenceSchema;
  contentItem?: ConferenceContent;
  selectedContentTypeId: string = '';
  selectedContentType?: ContentTypeDefinition;

  loading = true;
  error: string | null = null;
  showForm = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private contentService: ConferenceContentService
  ) { }

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const confId = params.get('conferenceId');
      const contId = params.get('contentId');
      this.conferenceId = confId !== null ? confId : '';
      this.contentId = contId !== null ? contId : '';

      this.isEditMode = !!this.contentId;

      this.loadConferenceSchema();
    });
  }

  private loadConferenceSchema(): void {
    this.loading = true;

    if (!this.conferenceId) {
      this.error = 'Conference ID is required';
      this.loading = false;
      return;
    }

    this.contentService.getConferenceSchema(this.conferenceId)
      .subscribe({
        next: (schema) => {
          this.conferenceSchema = schema;

          if (this.isEditMode) {
            this.loadContentItem();
          } else {
            this.loading = false;
          }
        },
        error: (err) => {
          this.error = 'Failed to load conference schema';
          this.loading = false;
        }
      });
  }

  private loadContentItem(): void {
    this.contentService.getContentItem(this.conferenceId, this.contentId)
      .subscribe({
        next: (content) => {
          this.contentItem = content;
          this.selectedContentTypeId = content.contentTypeId;
          this.updateSelectedContentType();
          this.showForm = true;
          this.loading = false;
        },
        error: (err) => {
          this.error = 'Failed to load content item';
          this.loading = false;
        }
      });
  }

  onContentTypeChange(): void {
    this.updateSelectedContentType();
    this.showForm = !!this.selectedContentTypeId;
  }

  private updateSelectedContentType(): void {
    if (this.conferenceSchema && this.selectedContentTypeId) {
      this.selectedContentType = this.conferenceSchema.contentTypes.find(
        type => type.id === this.selectedContentTypeId
      );
    }
  }

  onFormSubmit(content: ConferenceContent): void {
    this.loading = true;

    const saveObservable = this.isEditMode
      ? this.contentService.updateContentItem(this.conferenceId, this.contentId, content)
      : this.contentService.createContentItem(this.conferenceId, content);

    saveObservable.subscribe({
      next: (result) => {
        this.loading = false;
        this.navigateToContent(result.id);
      },
      error: (err) => {
        this.error = this.isEditMode
          ? 'Failed to update content'
          : 'Failed to create content';
        this.loading = false;
      }
    });
  }

  navigateBack(): void {
    this.router.navigate(['/content-management/conferences', this.conferenceId]);
  }

  navigateToContent(contentId: string): void {
    this.router.navigate(['/content-management/conferences', this.conferenceId, 'content', contentId]);
  }
}
