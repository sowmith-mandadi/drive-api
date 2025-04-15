import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatMenuModule } from '@angular/material/menu';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatFormFieldModule } from '@angular/material/form-field';

import { ConferenceContentService } from '../../services/conference-content.service';
import { ConferenceSchema } from '../../models/conference.model';

@Component({
  selector: 'app-conference-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatMenuModule,
    MatTableModule,
    MatSortModule,
    MatPaginatorModule,
    MatFormFieldModule
  ],
  template: `
    <div class="conference-list">
      <div class="list-header">
        <h1>Conferences</h1>

        <button mat-raised-button color="primary" [routerLink]="['/content-management/conferences/create']">
          <mat-icon>add</mat-icon> New Conference
        </button>
      </div>

      <div class="error-message" *ngIf="error">
        <mat-error>{{ error }}</mat-error>
      </div>

      <mat-progress-bar *ngIf="loading" mode="indeterminate"></mat-progress-bar>

      <div class="conference-grid" *ngIf="!loading && conferences.length > 0">
        <mat-card *ngFor="let conference of conferences" class="conference-card">
          <mat-card-header>
            <mat-card-title>{{ conference.name }}</mat-card-title>
            <mat-card-subtitle>{{ conference.year }}</mat-card-subtitle>
          </mat-card-header>

          <mat-card-content>
            <p *ngIf="conference.description">{{ conference.description }}</p>

            <div class="stats-row">
              <div class="stat">
                <span class="stat-label">Content Types</span>
                <span class="stat-value">{{ conference.contentTypes.length }}</span>
              </div>

              <div class="stat">
                <span class="stat-label">Fields</span>
                <span class="stat-value">{{ conference.fields.length }}</span>
              </div>

              <div class="stat">
                <span class="stat-label">Last Updated</span>
                <span class="stat-value">{{ conference.updated | date:'mediumDate' }}</span>
              </div>
            </div>
          </mat-card-content>

          <mat-card-actions align="end">
            <button mat-button (click)="viewConference(conference.id)">
              <mat-icon>dashboard</mat-icon> Manage Content
            </button>
            <button mat-button [matMenuTriggerFor]="menu">
              <mat-icon>more_vert</mat-icon>
            </button>

            <mat-menu #menu="matMenu">
              <button mat-menu-item (click)="editConference(conference.id)">
                <mat-icon>edit</mat-icon> Edit Schema
              </button>
              <button mat-menu-item (click)="cloneConference(conference.id)">
                <mat-icon>content_copy</mat-icon> Clone
              </button>
            </mat-menu>
          </mat-card-actions>
        </mat-card>
      </div>

      <div class="empty-state" *ngIf="!loading && conferences.length === 0">
        <mat-icon>event_note</mat-icon>
        <h2>No Conferences Available</h2>
        <p>Get started by creating your first conference schema.</p>
        <button mat-raised-button color="primary" [routerLink]="['/content-management/conferences/create']">
          Create Conference
        </button>
      </div>
    </div>
  `,
  styles: [`
    .conference-list {
      padding: 1rem;

      .list-header {
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

      .conference-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-top: 1.5rem;
      }

      .conference-card {
        height: 100%;
        display: flex;
        flex-direction: column;

        mat-card-content {
          flex-grow: 1;
        }
      }

      .stats-row {
        display: flex;
        justify-content: space-between;
        margin-top: 1rem;

        .stat {
          display: flex;
          flex-direction: column;
          align-items: center;

          .stat-label {
            font-size: 0.8rem;
            color: rgba(0, 0, 0, 0.54);
          }

          .stat-value {
            font-size: 1.2rem;
            font-weight: 500;
          }
        }
      }

      .empty-state {
        margin-top: 3rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;

        mat-icon {
          font-size: 48px;
          width: 48px;
          height: 48px;
          margin-bottom: 1rem;
          color: rgba(0, 0, 0, 0.38);
        }

        h2 {
          margin: 0 0 0.5rem;
          color: rgba(0, 0, 0, 0.87);
        }

        p {
          margin: 0 0 1.5rem;
          color: rgba(0, 0, 0, 0.6);
        }
      }
    }
  `]
})
export class ConferenceListComponent implements OnInit {
  conferences: ConferenceSchema[] = [];
  loading = true;
  error: string | null = null;

  constructor(
    private router: Router,
    private contentService: ConferenceContentService
  ) { }

  ngOnInit(): void {
    this.loadConferences();
  }

  loadConferences(): void {
    this.contentService.getConferenceSchemas()
      .subscribe({
        next: (schemas) => {
          this.conferences = schemas;
          this.loading = false;
        },
        error: (err) => {
          this.error = 'Failed to load conferences';
          this.loading = false;
        }
      });
  }

  viewConference(id: string): void {
    this.router.navigate(['/content-management/conferences', id]);
  }

  editConference(id: string): void {
    this.router.navigate(['/content-management/conferences', id, 'edit']);
  }

  cloneConference(id: string): void {
    // In a real app, this would open a dialog to configure cloning options
    this.router.navigate(['/content-management/conferences', id, 'edit']);
  }
}
