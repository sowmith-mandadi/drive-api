import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormArray, FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { CdkDragDrop, moveItemInArray, DragDropModule } from '@angular/cdk/drag-drop';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { ConferenceContentService } from '../../services/conference-content.service';
import {
  ConferenceSchema,
  FieldDefinition,
  ContentTypeDefinition
} from '../../models/conference.model';

@Component({
  selector: 'app-conference-schema',
  templateUrl: './conference-schema.component.html',
  styleUrls: ['./conference-schema.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    MatDialogModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatProgressSpinnerModule,
    DragDropModule
  ]
})
export class ConferenceSchemaComponent implements OnInit {
  schemaForm!: FormGroup;
  conferenceId: string | null = null;
  existingSchema: ConferenceSchema | null = null;
  isEditMode = false;
  loading = false;
  error: string | null = null;

  fieldTypes = [
    { value: 'text', label: 'Text' },
    { value: 'number', label: 'Number' },
    { value: 'date', label: 'Date' },
    { value: 'boolean', label: 'Boolean' },
    { value: 'select', label: 'Single Select' },
    { value: 'multiselect', label: 'Multi Select' },
    { value: 'rich-text', label: 'Rich Text' }
  ];

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private contentService: ConferenceContentService,
    private dialog: MatDialog
  ) { }

  ngOnInit(): void {
    this.initializeForm();

    this.route.paramMap.subscribe(params => {
      this.conferenceId = params.get('conferenceId');

      if (this.conferenceId) {
        this.isEditMode = true;
        this.loadExistingSchema();
      }
    });
  }

  private initializeForm(): void {
    this.schemaForm = this.fb.group({
      name: ['', [Validators.required]],
      year: [new Date().getFullYear(), [Validators.required, Validators.min(2000), Validators.max(2100)]],
      description: [''],
      fields: this.fb.array([]),
      contentTypes: this.fb.array([])
    });
  }

  private loadExistingSchema(): void {
    this.loading = true;

    if (this.conferenceId === null) {
      this.loading = false;
      return;
    }

    this.contentService.getConferenceSchema(this.conferenceId)
      .subscribe({
        next: (schema) => {
          this.existingSchema = schema;
          this.populateForm(schema);
          this.loading = false;
        },
        error: (err) => {
          this.error = 'Failed to load conference schema';
          this.loading = false;
        }
      });
  }

  private populateForm(schema: ConferenceSchema): void {
    this.schemaForm.patchValue({
      name: schema.name,
      year: schema.year,
      description: schema.description
    });

    // Clear existing arrays
    this.fieldsArray.clear();
    this.contentTypesArray.clear();

    // Add fields
    schema.fields.forEach(field => {
      this.addField(field);
    });

    // Add content types
    schema.contentTypes.forEach(contentType => {
      this.addContentType(contentType);
    });
  }

  get fieldsArray(): FormArray {
    return this.schemaForm.get('fields') as FormArray;
  }

  get contentTypesArray(): FormArray {
    return this.schemaForm.get('contentTypes') as FormArray;
  }

  // Helper method to get field control as FormGroup
  getFieldAsFormGroup(index: number): FormGroup {
    return this.fieldsArray.at(index) as FormGroup;
  }

  // Helper method to get content type control as FormGroup
  getContentTypeAsFormGroup(index: number): FormGroup {
    return this.contentTypesArray.at(index) as FormGroup;
  }

  createFieldFormGroup(field?: FieldDefinition): FormGroup {
    return this.fb.group({
      id: [field?.id || this.generateUniqueId(), Validators.required],
      name: [field?.name || '', [Validators.required, Validators.pattern('[a-zA-Z0-9_]*')]],
      displayName: [field?.displayName || '', Validators.required],
      type: [field?.type || 'text', Validators.required],
      required: [field?.required || false],
      defaultValue: [field?.defaultValue || ''],
      options: [field?.options?.join('\n') || ''],
      helpText: [field?.helpText || ''],
      groupName: [field?.groupName || ''],
      validation: this.fb.group({
        minLength: [field?.validation?.minLength || null],
        maxLength: [field?.validation?.maxLength || null],
        min: [field?.validation?.min || null],
        max: [field?.validation?.max || null],
        pattern: [field?.validation?.pattern || ''],
        customValidator: [field?.validation?.customValidator || '']
      })
    });
  }

  createContentTypeFormGroup(contentType?: ContentTypeDefinition): FormGroup {
    return this.fb.group({
      id: [contentType?.id || this.generateUniqueId(), Validators.required],
      name: [contentType?.name || '', [Validators.required, Validators.pattern('[a-zA-Z0-9_]*')]],
      displayName: [contentType?.displayName || '', Validators.required],
      description: [contentType?.description || ''],
      baseFields: [contentType?.baseFields || []],
      optionalFields: [contentType?.optionalFields || []],
      inheritsFrom: [contentType?.inheritsFrom || '']
    });
  }

  addField(field?: FieldDefinition): void {
    this.fieldsArray.push(this.createFieldFormGroup(field));
  }

  removeField(index: number): void {
    this.fieldsArray.removeAt(index);
  }

  addContentType(contentType?: ContentTypeDefinition): void {
    this.contentTypesArray.push(this.createContentTypeFormGroup(contentType));
  }

  removeContentType(index: number): void {
    this.contentTypesArray.removeAt(index);
  }

  onFieldDrop(event: CdkDragDrop<any[]>): void {
    moveItemInArray(this.fieldsArray.controls, event.previousIndex, event.currentIndex);
  }

  onContentTypeDrop(event: CdkDragDrop<any[]>): void {
    moveItemInArray(this.contentTypesArray.controls, event.previousIndex, event.currentIndex);
  }

  displayValidationFields(fieldType: string): boolean {
    return ['text', 'number', 'rich-text'].includes(fieldType);
  }

  displayOptionsField(fieldType: string): boolean {
    return ['select', 'multiselect'].includes(fieldType);
  }

  saveSchema(): void {
    if (this.schemaForm.invalid) {
      return;
    }

    this.loading = true;

    // Transform form data to schema model
    const formValue = this.schemaForm.value;
    const schema: Partial<ConferenceSchema> = {
      name: formValue.name,
      year: formValue.year,
      description: formValue.description,
      fields: this.transformFields(formValue.fields),
      contentTypes: this.transformContentTypes(formValue.contentTypes)
    };

    // Handle save or update
    const saveObservable = this.isEditMode && this.conferenceId
      ? this.contentService.updateConferenceSchema(this.conferenceId, schema)
      : this.contentService.createConferenceSchema(schema);

    saveObservable.subscribe({
      next: (result) => {
        this.loading = false;
        this.navigateBack(result.id);
      },
      error: (err) => {
        this.error = 'Failed to save conference schema';
        this.loading = false;
      }
    });
  }

  private transformFields(formFields: any[]): FieldDefinition[] {
    return formFields.map(field => {
      const transformedField: FieldDefinition = {
        id: field.id,
        name: field.name,
        displayName: field.displayName,
        type: field.type as 'text' | 'number' | 'date' | 'boolean' | 'select' | 'multiselect' | 'rich-text',
        required: field.required,
        helpText: field.helpText,
        groupName: field.groupName
      };

      if (field.defaultValue) {
        transformedField.defaultValue = field.defaultValue;
      }

      if (this.displayOptionsField(field.type) && field.options) {
        transformedField.options = field.options
          .split('\n')
          .map((opt: string) => opt.trim())
          .filter((opt: string) => opt);
      }

      if (this.displayValidationFields(field.type)) {
        transformedField.validation = {};

        if (field.validation.minLength) transformedField.validation.minLength = field.validation.minLength;
        if (field.validation.maxLength) transformedField.validation.maxLength = field.validation.maxLength;
        if (field.validation.min) transformedField.validation.min = field.validation.min;
        if (field.validation.max) transformedField.validation.max = field.validation.max;
        if (field.validation.pattern) transformedField.validation.pattern = field.validation.pattern;
        if (field.validation.customValidator) transformedField.validation.customValidator = field.validation.customValidator;
      }

      return transformedField;
    });
  }

  private transformContentTypes(formContentTypes: any[]): ContentTypeDefinition[] {
    return formContentTypes.map(contentType => {
      const transformedContentType: ContentTypeDefinition = {
        id: contentType.id,
        name: contentType.name,
        displayName: contentType.displayName,
        baseFields: contentType.baseFields,
        optionalFields: contentType.optionalFields
      };

      if (contentType.description) {
        transformedContentType.description = contentType.description;
      }

      if (contentType.inheritsFrom) {
        transformedContentType.inheritsFrom = contentType.inheritsFrom;
      }

      return transformedContentType;
    });
  }

  navigateBack(id?: string): void {
    if (id) {
      this.router.navigate(['/content-management/conferences', id]);
    } else {
      this.router.navigate(['/content-management/conferences']);
    }
  }

  openCloneDialog(): void {
    // TODO: Implement clone functionality
    // Open dialog to specify which fields to retain, target year, etc.
  }

  private generateUniqueId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
  }
}
