import { Component, Input, OnInit, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatNativeDateModule } from '@angular/material/core';

import { 
  ConferenceSchema, 
  ConferenceContent, 
  FieldDefinition, 
  ContentTypeDefinition 
} from '../../models/conference.model';

@Component({
  selector: 'app-dynamic-content-form',
  templateUrl: './dynamic-content-form.component.html',
  styleUrls: ['./dynamic-content-form.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule,
    MatDatepickerModule,
    MatProgressBarModule,
    MatNativeDateModule
  ]
})
export class DynamicContentFormComponent implements OnInit, OnChanges {
  @Input() conferenceSchema!: ConferenceSchema;
  @Input() contentItem?: ConferenceContent;
  @Input() contentTypeId!: string;
  @Input() readOnly = false;
  @Output() formSubmit = new EventEmitter<ConferenceContent>();
  
  contentForm!: FormGroup;
  contentType!: ContentTypeDefinition;
  fields: FieldDefinition[] = [];
  fieldGroups: { [key: string]: FieldDefinition[] } = {};
  baseFields: FieldDefinition[] = [];
  loading = true;
  error: string | null = null;
  
  constructor(private fb: FormBuilder) { }

  ngOnInit(): void {
    this.initializeForm();
  }
  
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['conferenceSchema'] || changes['contentTypeId']) {
      this.initializeForm();
    }
    
    if (changes['contentItem'] && this.contentForm && this.contentItem) {
      this.patchFormValues();
    }
  }
  
  private initializeForm(): void {
    if (!this.conferenceSchema || !this.contentTypeId) {
      this.loading = false;
      return;
    }
    
    try {
      // Find the content type
      const foundContentType = this.conferenceSchema.contentTypes.find(ct => ct.id === this.contentTypeId);
      
      if (!foundContentType) {
        throw new Error(`Content type with ID ${this.contentTypeId} not found`);
      }
      
      this.contentType = foundContentType;
      
      // Get fields for this content type
      this.fields = this.getFieldsForContentType();
      
      // Group fields by group name
      this.organizeFieldsByGroup();
      
      // Create form controls
      this.createFormControls();
      
      // Patch form values if content item exists
      if (this.contentItem) {
        this.patchFormValues();
      }
      
      this.loading = false;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      this.error = errorMessage;
      this.loading = false;
    }
  }
  
  private getFieldsForContentType(): FieldDefinition[] {
    const allFields: FieldDefinition[] = [];
    
    // Start with base fields
    if (this.contentType.baseFields?.length) {
      for (const fieldId of this.contentType.baseFields) {
        const field = this.findField(fieldId);
        if (field) {
          allFields.push(field);
        }
      }
    }
    
    // Add optional fields
    if (this.contentType.optionalFields?.length) {
      for (const fieldId of this.contentType.optionalFields) {
        const field = this.findField(fieldId);
        if (field) {
          allFields.push(field);
        }
      }
    }
    
    // If this content type inherits from another, add inherited fields
    if (this.contentType.inheritsFrom) {
      const parentType = this.conferenceSchema.contentTypes.find(ct => ct.id === this.contentType.inheritsFrom);
      if (parentType) {
        // Add parent base fields if they aren't already included
        if (parentType.baseFields?.length) {
          for (const fieldId of parentType.baseFields) {
            if (!allFields.some(f => f.id === fieldId)) {
              const field = this.findField(fieldId);
              if (field) {
                allFields.push(field);
              }
            }
          }
        }
        
        // Add parent optional fields if they aren't already included
        if (parentType.optionalFields?.length) {
          for (const fieldId of parentType.optionalFields) {
            if (!allFields.some(f => f.id === fieldId)) {
              const field = this.findField(fieldId);
              if (field) {
                allFields.push(field);
              }
            }
          }
        }
      }
    }
    
    return allFields;
  }
  
  private findField(fieldId: string): FieldDefinition | undefined {
    return this.conferenceSchema.fields.find(f => f.id === fieldId);
  }
  
  private organizeFieldsByGroup(): void {
    this.fieldGroups = { 'main': [] };
    this.baseFields = [];
    
    // First, add required base fields (title is always required)
    this.baseFields = [
      {
        id: 'title',
        name: 'title',
        displayName: 'Title',
        type: 'text',
        required: true
      }
    ];
    
    // Then organize the rest by groups
    for (const field of this.fields) {
      if (!field.groupName || field.groupName === '') {
        if (!this.fieldGroups['main']) {
          this.fieldGroups['main'] = [];
        }
        this.fieldGroups['main'].push(field);
      } else {
        if (!this.fieldGroups[field.groupName]) {
          this.fieldGroups[field.groupName] = [];
        }
        this.fieldGroups[field.groupName].push(field);
      }
    }
  }
  
  private createFormControls(): void {
    // Create form group
    const formConfig: Record<string, any> = {};
    
    // Add base fields
    for (const field of this.baseFields) {
      formConfig[field.name] = [
        '', 
        field.required ? [Validators.required] : []
      ];
    }
    
    // Add properties object for dynamic fields
    formConfig['properties'] = this.fb.group({});
    
    // Create form
    this.contentForm = this.fb.group(formConfig);
    
    // Add dynamic field controls
    const propertiesGroup = this.contentForm.get('properties') as FormGroup;
    
    for (const field of this.fields) {
      const validators = [];
      
      if (field.required) {
        validators.push(Validators.required);
      }
      
      if (field.validation) {
        if (field.validation.minLength) {
          validators.push(Validators.minLength(field.validation.minLength));
        }
        
        if (field.validation.maxLength) {
          validators.push(Validators.maxLength(field.validation.maxLength));
        }
        
        if (field.validation.pattern) {
          validators.push(Validators.pattern(field.validation.pattern));
        }
        
        // Add custom validators if needed
      }
      
      propertiesGroup.addControl(
        field.name,
        this.fb.control(field.defaultValue || '', validators)
      );
    }
  }
  
  private patchFormValues(): void {
    if (!this.contentForm || !this.contentItem) {
      return;
    }
    
    // Patch base fields
    const baseValues: Record<string, any> = {};
    for (const field of this.baseFields) {
      // Handle specific fields that we know exist on the content item
      if (field.name === 'title') {
        baseValues[field.name] = this.contentItem.title;
      }
      // Add more specific fields as needed
    }
    
    this.contentForm.patchValue(baseValues);
    
    // Patch properties
    if (this.contentItem.properties) {
      const propertiesGroup = this.contentForm.get('properties') as FormGroup;
      propertiesGroup.patchValue(this.contentItem.properties);
    }
  }
  
  onSubmit(): void {
    if (this.contentForm.invalid || this.readOnly) {
      return;
    }
    
    const formValue = this.contentForm.value;
    
    // Build content item
    const updatedContent: Partial<ConferenceContent> = {
      title: formValue.title,
      contentTypeId: this.contentTypeId,
      properties: formValue.properties
    };
    
    if (this.contentItem) {
      // If updating existing item, preserve other properties
      updatedContent.id = this.contentItem.id;
      updatedContent.conferenceId = this.contentItem.conferenceId;
      updatedContent.status = this.contentItem.status;
      updatedContent.version = this.contentItem.version + 1;
      updatedContent.previousVersions = this.contentItem.previousVersions || [];
      updatedContent.previousVersions.push(this.contentItem.id);
      updatedContent.tags = this.contentItem.tags;
    }
    
    this.formSubmit.emit(updatedContent as ConferenceContent);
  }
  
  getGroupLabel(groupName: string): string {
    if (groupName === 'main') {
      return 'Main Content';
    }
    
    // Capitalize and format group name
    return groupName
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, str => str.toUpperCase());
  }
  
  getGroups(): string[] {
    return Object.keys(this.fieldGroups);
  }
  
  getControlPath(fieldName: string): string {
    return `properties.${fieldName}`;
  }
  
  getErrorMessage(fieldName: string): string {
    const control = this.contentForm.get(this.getControlPath(fieldName));
    
    if (!control || !control.errors) {
      return '';
    }
    
    if (control.errors['required']) {
      return 'This field is required';
    }
    
    if (control.errors['minlength']) {
      return `Minimum length is ${control.errors['minlength'].requiredLength} characters`;
    }
    
    if (control.errors['maxlength']) {
      return `Maximum length is ${control.errors['maxlength'].requiredLength} characters`;
    }
    
    if (control.errors['pattern']) {
      return 'Value does not match the required pattern';
    }
    
    return 'Invalid value';
  }
} 