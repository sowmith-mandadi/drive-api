import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';

export interface SaveFilterDialogData {
  filters: any;
  name: string;
}

@Component({
  selector: 'app-save-filter-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ],
  template: `
    <h2 mat-dialog-title>Save Filter Configuration</h2>
    <form [formGroup]="form" (ngSubmit)="saveFilter()">
      <mat-dialog-content>
        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Filter Name</mat-label>
          <input matInput formControlName="name" placeholder="My Filter">
          <mat-error *ngIf="form.get('name')?.hasError('required')">
            Filter name is required
          </mat-error>
        </mat-form-field>
        
        <div class="filter-summary">
          <h3>Filter Settings</h3>
          <div *ngFor="let entry of filterEntries" class="filter-entry">
            <span class="filter-key">{{ formatFilterKey(entry.key) }}:</span>
            <span class="filter-value">{{ formatFilterValue(entry.value) }}</span>
          </div>
        </div>
      </mat-dialog-content>
      
      <mat-dialog-actions align="end">
        <button mat-button mat-dialog-close type="button">Cancel</button>
        <button mat-raised-button color="primary" type="submit" [disabled]="!form.valid">Save</button>
      </mat-dialog-actions>
    </form>
  `,
  styles: [`
    .full-width {
      width: 100%;
    }
    
    .filter-summary {
      margin-top: 16px;
      border-top: 1px solid rgba(0, 0, 0, 0.12);
      padding-top: 8px;
    }
    
    h3 {
      font-size: 14px;
      margin-bottom: 8px;
      color: rgba(0, 0, 0, 0.6);
    }
    
    .filter-entry {
      margin-bottom: 4px;
      font-size: 14px;
    }
    
    .filter-key {
      font-weight: 500;
      margin-right: 4px;
    }
    
    .filter-value {
      color: rgba(0, 0, 0, 0.87);
    }
  `]
})
export class SaveFilterDialogComponent {
  form!: FormGroup;
  filterEntries: {key: string, value: any}[] = [];
  
  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<SaveFilterDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: SaveFilterDialogData
  ) {
    this.form = this.fb.group({
      name: [data.name || '', Validators.required]
    });
    
    // Process filter entries for display
    this.processFilters();
  }
  
  processFilters(): void {
    this.filterEntries = Object.entries(this.data.filters)
      .filter(([_, value]) => value !== undefined && value !== null && value !== '')
      .map(([key, value]) => ({ key, value }));
  }
  
  formatFilterKey(key: string): string {
    return key
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, str => str.toUpperCase())
      .replace(/([a-z])([A-Z])/g, '$1 $2')
      .replace('Search Term', 'Search')
      .replace('Sort By', 'Sort by')
      .replace('Sort Dir', 'Sort direction');
  }
  
  formatFilterValue(value: any): string {
    if (value === undefined || value === null) {
      return '';
    }
    
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No';
    }
    
    if (typeof value === 'string') {
      if (value.length > 30) {
        return value.substring(0, 30) + '...';
      }
      return value;
    }
    
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return '';
      }
      return value.join(', ');
    }
    
    if (value instanceof Date) {
      return value.toLocaleDateString();
    }
    
    return String(value);
  }
  
  saveFilter(): void {
    if (this.form.valid) {
      this.dialogRef.close({
        name: this.form.value.name,
        filters: this.data.filters
      });
    }
  }
} 