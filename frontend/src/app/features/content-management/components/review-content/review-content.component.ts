import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { RouterLink } from '@angular/router';

interface ContentItem {
  id: string;
  selected?: boolean;
  title: string;
  description: string;
  track: string;
  type: string;
  status: 'published' | 'draft' | 'pending-review' | 'archived';
  dateCreated: Date;
  dateModified: Date;
  author: string;
  tags?: string[];
}

@Component({
  selector: 'app-review-content',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatTableModule,
    MatCheckboxModule,
    MatChipsModule,
    MatTooltipModule,
    MatMenuModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
    MatSnackBarModule,
    RouterLink
  ],
  template: `
    <div class="review-content-container">
      <div class="header">
        <button mat-icon-button routerLink="/content-management">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1>Content Review</h1>
      </div>
      
      <div class="actions-bar">
        <div class="selection-info" *ngIf="selectedItems().length > 0">
          {{ selectedItems().length }} item{{ selectedItems().length > 1 ? 's' : '' }} selected
        </div>
        
        <div class="search-box">
          <mat-form-field appearance="outline">
            <mat-icon matPrefix>search</mat-icon>
            <input matInput placeholder="Filter content..." (input)="applyFilter($event)">
          </mat-form-field>
        </div>
        
        <div class="action-buttons">
          <button mat-raised-button color="primary" 
                  [disabled]="selectedItems().length === 0"
                  (click)="bulkApprove()">
            <mat-icon>check</mat-icon>
            Approve
          </button>
          
          <button mat-raised-button color="accent" 
                  [disabled]="selectedItems().length === 0"
                  (click)="bulkAddTags()">
            <mat-icon>local_offer</mat-icon>
            Add Tags
          </button>
          
          <button mat-raised-button color="warn" 
                  [disabled]="selectedItems().length === 0"
                  (click)="bulkReject()">
            <mat-icon>cancel</mat-icon>
            Reject
          </button>
          
          <button mat-button [matMenuTriggerFor]="moreMenu">
            <mat-icon>more_vert</mat-icon>
          </button>
          
          <mat-menu #moreMenu="matMenu">
            <button mat-menu-item (click)="bulkArchive()" [disabled]="selectedItems().length === 0">
              <mat-icon>archive</mat-icon>
              <span>Archive</span>
            </button>
            <button mat-menu-item (click)="selectAll()">
              <mat-icon>select_all</mat-icon>
              <span>Select All</span>
            </button>
            <button mat-menu-item (click)="clearSelection()" [disabled]="selectedItems().length === 0">
              <mat-icon>clear</mat-icon>
              <span>Clear Selection</span>
            </button>
          </mat-menu>
        </div>
      </div>
      
      <div class="table-container notion-like-table">
        <table>
          <thead>
            <tr>
              <th class="checkbox-column">
                <mat-checkbox 
                  [checked]="isAllSelected()" 
                  [indeterminate]="isSomeSelected()"
                  (change)="toggleAllSelection($event)">
                </mat-checkbox>
              </th>
              <th class="title-column">Title</th>
              <th>Track</th>
              <th>Type</th>
              <th>Author</th>
              <th>Last Modified</th>
              <th>Status</th>
              <th>Tags</th>
              <th class="actions-column">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let item of filteredItems()" 
                [class.selected-row]="item.selected">
              <td class="checkbox-column">
                <mat-checkbox 
                  [(ngModel)]="item.selected"
                  (change)="updateSelectedItems()">
                </mat-checkbox>
              </td>
              <td class="title-column">
                <div class="title-cell">
                  <span class="item-title">{{ item.title }}</span>
                  <span class="item-description">{{ item.description }}</span>
                </div>
              </td>
              <td>
                <mat-form-field appearance="outline" class="inline-edit">
                  <mat-select [(ngModel)]="item.track">
                    <mat-option value="Web Development">Web Development</mat-option>
                    <mat-option value="Artificial Intelligence">Artificial Intelligence</mat-option>
                    <mat-option value="Cloud Computing">Cloud Computing</mat-option>
                    <mat-option value="DevOps">DevOps</mat-option>
                    <mat-option value="Mobile Development">Mobile Development</mat-option>
                  </mat-select>
                </mat-form-field>
              </td>
              <td>
                <mat-form-field appearance="outline" class="inline-edit">
                  <mat-select [(ngModel)]="item.type">
                    <mat-option value="Presentation">Presentation</mat-option>
                    <mat-option value="Workshop">Workshop</mat-option>
                    <mat-option value="Technical Session">Technical Session</mat-option>
                    <mat-option value="Keynote">Keynote</mat-option>
                  </mat-select>
                </mat-form-field>
              </td>
              <td>{{ item.author }}</td>
              <td>{{ item.dateModified | date:'short' }}</td>
              <td>
                <span class="status-pill" [ngClass]="getStatusClass(item.status)">
                  {{ getStatusText(item.status) }}
                </span>
              </td>
              <td>
                <div class="tags-cell">
                  <mat-chip-set>
                    <mat-chip *ngFor="let tag of item.tags">{{ tag }}</mat-chip>
                    <button mat-icon-button class="add-tag-button"
                            matTooltip="Add Tag"
                            (click)="addTag(item)">
                      <mat-icon>add</mat-icon>
                    </button>
                  </mat-chip-set>
                </div>
              </td>
              <td class="actions-column">
                <button mat-icon-button color="primary" 
                        matTooltip="Approve"
                        (click)="approveItem(item)">
                  <mat-icon>check_circle</mat-icon>
                </button>
                <button mat-icon-button color="accent" 
                        matTooltip="View Details"
                        [routerLink]="['/content-management/content', item.id]">
                  <mat-icon>visibility</mat-icon>
                </button>
                <button mat-icon-button color="warn" 
                        matTooltip="Reject"
                        (click)="rejectItem(item)">
                  <mat-icon>cancel</mat-icon>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .review-content-container {
      max-width: 1600px;
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

    .actions-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
      gap: 1rem;
    }

    .selection-info {
      font-weight: 500;
      color: var(--primary-color);
      min-width: 150px;
    }

    .search-box {
      flex-grow: 1;
      max-width: 400px;
    }

    .action-buttons {
      display: flex;
      gap: 0.5rem;
    }

    .table-container {
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
      overflow: hidden;
    }

    .notion-like-table {
      width: 100%;
      overflow-x: auto;
    }

    .notion-like-table table {
      width: 100%;
      border-collapse: collapse;
    }

    .notion-like-table th {
      background-color: #f8f9fa;
      color: #666;
      font-weight: 500;
      text-align: left;
      padding: 0.75rem 1rem;
      border-bottom: 1px solid #eee;
      position: sticky;
      top: 0;
      z-index: 1;
    }

    .notion-like-table td {
      padding: 0.75rem 1rem;
      border-bottom: 1px solid #eee;
      vertical-align: top;
    }

    .checkbox-column {
      width: 48px;
      text-align: center;
    }

    .title-column {
      min-width: 250px;
    }

    .title-cell {
      display: flex;
      flex-direction: column;
    }

    .item-title {
      font-weight: 500;
      margin-bottom: 0.25rem;
    }

    .item-description {
      font-size: 0.875rem;
      color: #666;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .actions-column {
      width: 140px;
      text-align: right;
      white-space: nowrap;
    }

    .inline-edit {
      width: 100%;
      margin: -16px 0;
    }

    .status-pill {
      display: inline-block;
      padding: 0.25rem 0.75rem;
      border-radius: 16px;
      font-size: 0.875rem;
      font-weight: 500;
    }

    .status-published {
      background-color: #e6f4ea;
      color: #137333;
    }

    .status-draft {
      background-color: #e8eaed;
      color: #5f6368;
    }

    .status-pending {
      background-color: #fef7e0;
      color: #b06000;
    }

    .status-archived {
      background-color: #f3f4f6;
      color: #5f6368;
    }

    .tags-cell {
      display: flex;
      align-items: center;
    }

    .add-tag-button {
      width: 24px;
      height: 24px;
      line-height: 24px;
    }

    .add-tag-button mat-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
      line-height: 16px;
    }

    .selected-row {
      background-color: rgba(103, 58, 183, 0.05);
    }

    @media (max-width: 1024px) {
      .notion-like-table {
        overflow-x: auto;
      }
    }
  `]
})
export class ReviewContentComponent {
  contentItems = signal<ContentItem[]>([
    {
      id: '101',
      title: 'Introduction to Angular Signals',
      description: 'Learn about the new reactivity system in Angular',
      track: 'Web Development',
      type: 'Presentation',
      status: 'pending-review',
      dateCreated: new Date(2025, 3, 1),
      dateModified: new Date(2025, 3, 2),
      author: 'Jane Smith',
      tags: ['Angular', 'Signals', 'Web Development'],
      selected: false
    },
    {
      id: '102',
      title: 'Building AI Features in Web Apps',
      description: 'How to integrate AI capabilities in modern web applications',
      track: 'Artificial Intelligence',
      type: 'Workshop',
      status: 'pending-review',
      dateCreated: new Date(2025, 3, 2),
      dateModified: new Date(2025, 3, 3),
      author: 'John Doe',
      tags: ['AI', 'Web Development', 'ChatGPT'],
      selected: false
    },
    {
      id: '103',
      title: 'Advanced React Patterns',
      description: 'In-depth analysis of React design patterns',
      track: 'Web Development',
      type: 'Technical Session',
      status: 'pending-review',
      dateCreated: new Date(2025, 3, 3),
      dateModified: new Date(2025, 3, 4),
      author: 'Sarah Johnson',
      tags: ['React', 'JavaScript', 'Patterns'],
      selected: false
    },
    {
      id: '104',
      title: 'Cloud-Native Infrastructure',
      description: 'Building scalable infrastructure for modern applications',
      track: 'Cloud Computing',
      type: 'Technical Session',
      status: 'pending-review',
      dateCreated: new Date(2025, 3, 4),
      dateModified: new Date(2025, 3, 5),
      author: 'Michael Brown',
      tags: ['Cloud', 'Kubernetes', 'Docker'],
      selected: false
    },
    {
      id: '105',
      title: 'Mobile Development with Flutter',
      description: 'Creating cross-platform mobile applications',
      track: 'Mobile Development',
      type: 'Workshop',
      status: 'pending-review',
      dateCreated: new Date(2025, 3, 5),
      dateModified: new Date(2025, 3, 6),
      author: 'Emily Wilson',
      tags: ['Flutter', 'Mobile', 'Dart'],
      selected: false
    }
  ]);

  selectedItems = signal<ContentItem[]>([]);
  filterValue = signal<string>('');
  filteredItems = signal<ContentItem[]>(this.contentItems());

  constructor(private snackBar: MatSnackBar) {}

  applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value.toLowerCase();
    this.filterValue.set(filterValue);
    
    if (!filterValue) {
      this.filteredItems.set(this.contentItems());
      return;
    }
    
    const filtered = this.contentItems().filter(item => 
      item.title.toLowerCase().includes(filterValue) || 
      item.description.toLowerCase().includes(filterValue) ||
      item.author.toLowerCase().includes(filterValue) ||
      item.tags?.some(tag => tag.toLowerCase().includes(filterValue))
    );
    
    this.filteredItems.set(filtered);
  }

  updateSelectedItems(): void {
    const selected = this.contentItems().filter(item => item.selected);
    this.selectedItems.set(selected);
  }

  isAllSelected(): boolean {
    return this.contentItems().length > 0 && 
           this.contentItems().every(item => item.selected);
  }

  isSomeSelected(): boolean {
    return this.contentItems().some(item => item.selected) && 
           !this.isAllSelected();
  }

  toggleAllSelection(event: any): void {
    const isSelected = event.checked;
    const updatedItems = this.contentItems().map(item => ({
      ...item,
      selected: isSelected
    }));
    
    this.contentItems.set(updatedItems);
    this.filteredItems.set(this.filterValue() ? 
      updatedItems.filter(item => this.matchesFilter(item)) : 
      updatedItems);
    this.updateSelectedItems();
  }

  matchesFilter(item: ContentItem): boolean {
    const filter = this.filterValue().toLowerCase();
    return item.title.toLowerCase().includes(filter) || 
           item.description.toLowerCase().includes(filter) ||
           item.author.toLowerCase().includes(filter) ||
           (item.tags?.some(tag => tag.toLowerCase().includes(filter)) ?? false);
  }

  selectAll(): void {
    const updatedItems = this.contentItems().map(item => ({
      ...item,
      selected: true
    }));
    
    this.contentItems.set(updatedItems);
    this.filteredItems.set(this.filterValue() ? 
      updatedItems.filter(item => this.matchesFilter(item)) : 
      updatedItems);
    this.updateSelectedItems();
  }

  clearSelection(): void {
    const updatedItems = this.contentItems().map(item => ({
      ...item,
      selected: false
    }));
    
    this.contentItems.set(updatedItems);
    this.filteredItems.set(this.filterValue() ? 
      updatedItems.filter(item => this.matchesFilter(item)) : 
      updatedItems);
    this.selectedItems.set([]);
  }

  approveItem(item: ContentItem): void {
    const updatedItems = this.contentItems().map(i => 
      i.id === item.id ? { ...i, status: 'published' as const } : i
    );
    
    this.contentItems.set(updatedItems);
    this.filteredItems.set(this.filterValue() ? 
      updatedItems.filter(item => this.matchesFilter(item)) : 
      updatedItems);
    this.updateSelectedItems();
    
    this.snackBar.open(`"${item.title}" has been approved`, 'Dismiss', {
      duration: 3000
    });
  }

  rejectItem(item: ContentItem): void {
    // In a real app, you might want to add a reason or send it back with comments
    const updatedItems = this.contentItems().map(i => 
      i.id === item.id ? { ...i, status: 'draft' as const } : i
    );
    
    this.contentItems.set(updatedItems);
    this.filteredItems.set(this.filterValue() ? 
      updatedItems.filter(item => this.matchesFilter(item)) : 
      updatedItems);
    this.updateSelectedItems();
    
    this.snackBar.open(`"${item.title}" has been rejected`, 'Dismiss', {
      duration: 3000
    });
  }

  bulkApprove(): void {
    if (this.selectedItems().length === 0) return;
    
    const updatedItems = this.contentItems().map(item => 
      this.selectedItems().some(selected => selected.id === item.id) 
        ? { ...item, status: 'published' as const } 
        : item
    );
    
    this.contentItems.set(updatedItems);
    this.filteredItems.set(this.filterValue() ? 
      updatedItems.filter(item => this.matchesFilter(item)) : 
      updatedItems);
    
    this.snackBar.open(`${this.selectedItems().length} items approved`, 'Dismiss', {
      duration: 3000
    });
    
    this.clearSelection();
  }

  bulkReject(): void {
    if (this.selectedItems().length === 0) return;
    
    const updatedItems = this.contentItems().map(item => 
      this.selectedItems().some(selected => selected.id === item.id) 
        ? { ...item, status: 'draft' as const } 
        : item
    );
    
    this.contentItems.set(updatedItems);
    this.filteredItems.set(this.filterValue() ? 
      updatedItems.filter(item => this.matchesFilter(item)) : 
      updatedItems);
    
    this.snackBar.open(`${this.selectedItems().length} items rejected`, 'Dismiss', {
      duration: 3000
    });
    
    this.clearSelection();
  }

  bulkArchive(): void {
    if (this.selectedItems().length === 0) return;
    
    const updatedItems = this.contentItems().map(item => 
      this.selectedItems().some(selected => selected.id === item.id) 
        ? { ...item, status: 'archived' as const } 
        : item
    );
    
    this.contentItems.set(updatedItems);
    this.filteredItems.set(this.filterValue() ? 
      updatedItems.filter(item => this.matchesFilter(item)) : 
      updatedItems);
    
    this.snackBar.open(`${this.selectedItems().length} items archived`, 'Dismiss', {
      duration: 3000
    });
    
    this.clearSelection();
  }

  bulkAddTags(): void {
    // In a real app, this would open a dialog to select tags
    if (this.selectedItems().length === 0) return;
    
    const newTag = 'Conference2025';
    
    const updatedItems = this.contentItems().map(item => {
      if (this.selectedItems().some(selected => selected.id === item.id)) {
        const currentTags = item.tags || [];
        return { 
          ...item, 
          tags: [...currentTags, newTag].filter((v, i, a) => a.indexOf(v) === i) 
        };
      }
      return item;
    });
    
    this.contentItems.set(updatedItems);
    this.filteredItems.set(this.filterValue() ? 
      updatedItems.filter(item => this.matchesFilter(item)) : 
      updatedItems);
    
    this.snackBar.open(`Tag added to ${this.selectedItems().length} items`, 'Dismiss', {
      duration: 3000
    });
  }

  addTag(item: ContentItem): void {
    // In a real app, this would open a dialog to add a tag
    const newTag = `Tag-${Math.floor(Math.random() * 100)}`;
    
    const updatedItems = this.contentItems().map(i => {
      if (i.id === item.id) {
        const currentTags = i.tags || [];
        return { 
          ...i, 
          tags: [...currentTags, newTag] 
        };
      }
      return i;
    });
    
    this.contentItems.set(updatedItems);
    this.filteredItems.set(this.filterValue() ? 
      updatedItems.filter(item => this.matchesFilter(item)) : 
      updatedItems);
  }

  getStatusClass(status: string): string {
    switch(status) {
      case 'published': return 'status-published';
      case 'draft': return 'status-draft';
      case 'pending-review': return 'status-pending';
      case 'archived': return 'status-archived';
      default: return '';
    }
  }

  getStatusText(status: string): string {
    switch(status) {
      case 'published': return 'Published';
      case 'draft': return 'Draft';
      case 'pending-review': return 'Pending Review';
      case 'archived': return 'Archived';
      default: return status;
    }
  }
} 