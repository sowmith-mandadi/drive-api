import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { SelectionModel } from '@angular/cdk/collections';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatMenuModule } from '@angular/material/menu';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatNativeDateModule } from '@angular/material/core';
import { MatTableModule } from '@angular/material/table';

import { ConferenceContentService } from '../../services/conference-content.service';
import { 
  ConferenceSchema, 
  ConferenceContent, 
  FilterConfiguration, 
  FilterCriteria 
} from '../../models/conference.model';

@Component({
  selector: 'app-conference-dashboard',
  templateUrl: './conference-dashboard.component.html',
  styleUrls: ['./conference-dashboard.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    MatButtonModule,
    MatCheckboxModule,
    MatChipsModule,
    MatDatepickerModule,
    MatDialogModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatMenuModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatSortModule,
    MatTableModule,
    MatNativeDateModule
  ]
})
export class ConferenceDashboardComponent implements OnInit {
  conferenceId: string = '';
  conferenceSchema!: ConferenceSchema;
  dataSource = new MatTableDataSource<ConferenceContent>([]);
  selection = new SelectionModel<ConferenceContent>(true, []);
  displayedColumns: string[] = ['select', 'title', 'status', 'updatedBy', 'updated', 'actions'];
  customColumns: string[] = [];
  totalItems = 0;
  pageSize = 20;
  pageSizeOptions = [10, 20, 50, 100];
  
  filterForm!: FormGroup;
  savedFilters: FilterConfiguration[] = [];
  activeFilter: FilterConfiguration | null = null;

  loading = true;
  error: string | null = null;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private contentService: ConferenceContentService,
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private dialog: MatDialog
  ) { }

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const conferenceId = params.get('conferenceId');
      this.conferenceId = conferenceId !== null ? conferenceId : '';
      this.initializeComponent();
    });

    // Initialize the filter form
    this.filterForm = this.fb.group({
      searchTerm: [''],
      status: [''],
      dateFrom: [null],
      dateTo: [null],
      tags: [[]]
    });

    // Listen for filter changes
    this.filterForm.valueChanges
      .pipe(
        debounceTime(300),
        distinctUntilChanged()
      )
      .subscribe(() => {
        this.loadContentItems(1);
      });
  }

  // Add missing methods from template errors
  getContentTypeName(contentTypeId: string): string {
    if (!this.conferenceSchema) return '';
    const contentType = this.conferenceSchema.contentTypes.find(ct => ct.id === contentTypeId);
    return contentType ? contentType.displayName : '';
  }

  getFieldDisplayName(fieldName: string): string {
    if (!this.conferenceSchema) return fieldName;
    const field = this.conferenceSchema.fields.find(f => f.name === fieldName);
    return field ? field.displayName : fieldName;
  }

  addTag(event: any): void {
    if (event.value) {
      const value = event.value.trim();
      if (value) {
        const tags = this.filterForm.get('tags')?.value || [];
        if (!tags.includes(value)) {
          this.filterForm.get('tags')?.setValue([...tags, value]);
        }
      }
      // Clear the input value
      if (event.input) {
        event.input.value = '';
      }
    }
  }

  removeTag(tag: string): void {
    const tags = this.filterForm.get('tags')?.value || [];
    const index = tags.indexOf(tag);
    if (index >= 0) {
      const newTags = [...tags];
      newTags.splice(index, 1);
      this.filterForm.get('tags')?.setValue(newTags);
    }
  }

  publishContent(item: ConferenceContent): void {
    const updatedItem: Partial<ConferenceContent> = { 
      status: 'published' as 'draft' | 'review' | 'approved' | 'published' | 'rejected'
    };
    this.contentService.updateContentItem(this.conferenceId, item.id, updatedItem)
      .subscribe({
        next: () => {
          this.loadContentItems(this.paginator?.pageIndex + 1 || 1);
        }
      });
  }

  private initializeComponent(): void {
    this.loading = true;

    if (!this.conferenceId) {
      this.error = 'Conference ID is required';
      this.loading = false;
      return;
    }

    // Load conference schema
    this.contentService.getConferenceSchema(this.conferenceId)
      .subscribe({
        next: (schema) => {
          this.conferenceSchema = schema;
          this.setupCustomColumns();
          this.loadContentItems(1);
          this.loadSavedFilters();
        },
        error: (err) => {
          this.error = 'Failed to load conference schema';
          this.loading = false;
        }
      });
  }

  setupCustomColumns(): void {
    // Add custom columns based on schema fields
    // Start with base columns
    this.displayedColumns = ['select', 'title', 'contentType'];
    
    // Add up to 3 key fields from the schema as columns
    const keyFields = this.conferenceSchema.fields
      .filter(field => !field.groupName || field.groupName === 'main')
      .slice(0, 3);
      
    this.customColumns = keyFields.map(field => field.name);
    this.displayedColumns = [...this.displayedColumns, ...this.customColumns, 'status', 'updated', 'actions'];
  }

  loadContentItems(page: number): void {
    this.loading = true;
    const filters = this.buildFilters();
    
    this.contentService.getContentItems(
      this.conferenceId, 
      filters, 
      page, 
      this.pageSize
    ).subscribe({
      next: (result) => {
        this.dataSource.data = result.items;
        this.totalItems = result.total;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load content items';
        this.loading = false;
      }
    });
  }

  loadSavedFilters(): void {
    // This would use the actual user ID in a real application
    const userId = 'current-user';
    
    this.contentService.getSavedFilters(userId)
      .subscribe(filters => {
        this.savedFilters = filters;
      });
  }

  applyFilter(filter: FilterConfiguration): void {
    this.activeFilter = filter;
    
    // Apply the filter criteria to the form
    const formValues: any = {};
    
    filter.filters.forEach(criteria => {
      // Map filter criteria to form controls
      if (criteria.field === 'title' || criteria.field === 'properties.content') {
        formValues.searchTerm = criteria.value;
      } else if (criteria.field === 'status') {
        formValues.status = criteria.value;
      } else if (criteria.field === 'tags') {
        formValues.tags = criteria.value;
      }
      // Add more mappings as needed
    });
    
    this.filterForm.patchValue(formValues, { emitEvent: false });
    this.loadContentItems(1);
  }

  clearFilters(): void {
    this.activeFilter = null;
    this.filterForm.reset({}, { emitEvent: false });
    this.loadContentItems(1);
  }

  openSaveFilterDialog(): void {
    // For now, create a simple solution without the dialog
    const filterName = window.prompt('Enter a name for this filter:', this.activeFilter?.name || '');
    
    if (filterName) {
      const filterConfig: FilterConfiguration = {
        id: this.activeFilter?.id || '',
        name: filterName,
        userId: 'current-user',
        filters: this.convertToFilterCriteria(this.buildFilters()),
        sortBy: this.sort?.active,
        sortDirection: this.sort?.direction as 'asc' | 'desc'
      };
      
      this.contentService.saveFilterConfiguration(filterConfig)
        .subscribe(savedFilter => {
          this.loadSavedFilters();
          this.activeFilter = savedFilter;
        });
    }
  }

  private buildFilters(): any {
    const formValues = this.filterForm.value;
    const filters: any = {};
    
    if (formValues.searchTerm) {
      filters.searchTerm = formValues.searchTerm;
    }
    
    if (formValues.status) {
      filters.status = formValues.status;
    }

    if (formValues.tags && formValues.tags.length) {
      filters.tags = formValues.tags.join(',');
    }
    
    if (formValues.dateFrom) {
      filters.dateFrom = formValues.dateFrom.toISOString();
    }
    
    if (formValues.dateTo) {
      filters.dateTo = formValues.dateTo.toISOString();
    }
    
    // Add sort parameters if available
    if (this.sort?.active) {
      filters.sortBy = this.sort.active;
      filters.sortDir = this.sort.direction;
    }
    
    return filters;
  }

  private convertToFilterCriteria(filters: any): FilterCriteria[] {
    const criteria: FilterCriteria[] = [];
    
    Object.keys(filters).forEach(key => {
      if (filters[key]) {
        // Map form fields to filter criteria
        if (key === 'searchTerm') {
          criteria.push({
            field: 'title',
            operator: 'contains',
            value: filters[key]
          });
        } else if (key === 'status') {
          criteria.push({
            field: 'status',
            operator: 'equals',
            value: filters[key]
          });
        } else if (key === 'tags') {
          criteria.push({
            field: 'tags',
            operator: 'in',
            value: filters[key]
          });
        } else if (key === 'dateFrom') {
          criteria.push({
            field: 'updated',
            operator: 'greater_than',
            value: filters[key]
          });
        } else if (key === 'dateTo') {
          criteria.push({
            field: 'updated',
            operator: 'less_than',
            value: filters[key]
          });
        }
      }
    });
    
    return criteria;
  }

  // Bulk actions
  isAllSelected() {
    const numSelected = this.selection.selected.length;
    const numRows = this.dataSource.data.length;
    return numSelected === numRows;
  }

  toggleAllRows() {
    if (this.isAllSelected()) {
      this.selection.clear();
      return;
    }
    this.selection.select(...this.dataSource.data);
  }

  batchApprove() {
    if (this.selection.selected.length === 0) return;
    
    const contentIds = this.selection.selected.map(item => item.id);
    this.contentService.batchUpdateStatus(this.conferenceId, contentIds, 'approved')
      .subscribe({
        next: (success) => {
          if (success) {
            this.loadContentItems(this.paginator?.pageIndex + 1 || 1);
            this.selection.clear();
          }
        }
      });
  }

  batchPublish() {
    if (this.selection.selected.length === 0) return;
    
    const contentIds = this.selection.selected.map(item => item.id);
    this.contentService.batchUpdateStatus(this.conferenceId, contentIds, 'published')
      .subscribe({
        next: (success) => {
          if (success) {
            this.loadContentItems(this.paginator?.pageIndex + 1 || 1);
            this.selection.clear();
          }
        }
      });
  }

  batchAddTag(tag: string) {
    if (this.selection.selected.length === 0 || !tag) return;
    
    const contentIds = this.selection.selected.map(item => item.id);
    this.contentService.batchUpdateTags(this.conferenceId, contentIds, [tag], [])
      .subscribe({
        next: (success) => {
          if (success) {
            this.loadContentItems(this.paginator?.pageIndex + 1 || 1);
          }
        }
      });
  }

  // Pagination and sorting
  onPageChange(event: any): void {
    this.pageSize = event.pageSize;
    this.loadContentItems(event.pageIndex + 1);
  }

  onSortChange(): void {
    this.loadContentItems(this.paginator?.pageIndex + 1 || 1);
  }

  // Field value display helpers
  getFieldValue(item: ConferenceContent, fieldName: string): any {
    return item.properties[fieldName] || '';
  }

  // Handle keyboard shortcuts
  handleKeyboardShortcut(event: KeyboardEvent, item?: ConferenceContent): void {
    // Implement keyboard shortcuts (Ctrl+E, Ctrl+S, etc.)
    if (event.ctrlKey && event.key === 'e' && item) {
      event.preventDefault();
      this.editContent(item);
    } else if (event.altKey && event.key === 'a' && item) {
      event.preventDefault();
      this.approveContent(item);
    } else if (event.ctrlKey && event.key === 'a') {
      event.preventDefault();
      this.toggleAllRows();
    }
  }

  editContent(item: ConferenceContent): void {
    // Navigate to edit page or open edit dialog
    console.log('Edit content', item.id);
  }

  viewContent(item: ConferenceContent): void {
    // Navigate to view page or open view dialog
    console.log('View content', item.id);
  }

  approveContent(item: ConferenceContent): void {
    const updatedItem: Partial<ConferenceContent> = { 
      status: 'approved' as 'draft' | 'review' | 'approved' | 'published' | 'rejected'
    };
    this.contentService.updateContentItem(this.conferenceId, item.id, updatedItem)
      .subscribe({
        next: () => {
          this.loadContentItems(this.paginator?.pageIndex + 1 || 1);
        }
      });
  }
} 