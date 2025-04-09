import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-edit-content',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    RouterLink
  ],
  template: `
    <div class="edit-content-container">
      <div class="header">
        <button mat-icon-button routerLink="/content-management">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1>Edit Content</h1>
      </div>
      
      <mat-card>
        <mat-card-content>
          <p>This is a placeholder for the edit content component.</p>
          <p>This would contain a form for editing metadata and content details.</p>
        </mat-card-content>
        <mat-card-actions>
          <button mat-button routerLink="/content-management">Return to Dashboard</button>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [`
    .edit-content-container {
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
  `]
})
export class EditContentComponent {} 