export interface ConferenceSchema {
  id: string;
  name: string;
  year: number;
  description?: string;
  fields: FieldDefinition[];
  contentTypes: ContentTypeDefinition[];
  created: Date;
  updated: Date;
}

export interface FieldDefinition {
  id: string;
  name: string;
  displayName: string;
  type: 'text' | 'number' | 'date' | 'boolean' | 'select' | 'multiselect' | 'rich-text';
  required: boolean;
  defaultValue?: any;
  options?: string[]; // For select and multiselect
  validation?: FieldValidation;
  helpText?: string;
  groupName?: string;
}

export interface FieldValidation {
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  pattern?: string;
  customValidator?: string; // Name of custom validator function
}

export interface ContentTypeDefinition {
  id: string;
  name: string;
  displayName: string;
  description?: string;
  baseFields: string[]; // IDs of fields that are always present
  optionalFields: string[]; // IDs of fields that can be toggled on/off
  inheritsFrom?: string; // ID of parent content type to inherit fields from
}

export interface ConferenceContent {
  id: string;
  conferenceId: string;
  contentTypeId: string;
  title: string;
  status: 'draft' | 'review' | 'approved' | 'published' | 'rejected';
  properties: { [key: string]: any }; // Dynamic properties based on conference schema
  created: Date;
  updated: Date;
  createdBy: string;
  updatedBy: string;
  version: number;
  previousVersions?: string[]; // IDs of previous versions
  tags?: string[];
}

export interface ContentVersion {
  id: string;
  contentId: string;
  properties: { [key: string]: any };
  createdAt: Date;
  createdBy: string;
  changeDescription?: string;
}

export interface FilterConfiguration {
  id: string;
  name: string;
  userId: string;
  filters: FilterCriteria[];
  sortBy?: string;
  sortDirection?: 'asc' | 'desc';
  isDefault?: boolean;
}

export interface FilterCriteria {
  field: string; // Can be a base field or a property field
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'between' | 'in' | 'not_in';
  value: any;
}

export interface UserAction {
  id: string;
  userId: string;
  actionType: 'create' | 'update' | 'delete' | 'approve' | 'reject' | 'publish';
  contentId?: string;
  conferenceId?: string;
  schemaId?: string;
  timestamp: Date;
  details: any;
} 