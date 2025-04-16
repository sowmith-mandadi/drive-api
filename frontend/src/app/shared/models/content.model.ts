/**
 * Content models for the application
 */

/**
 * Asset interface for any attachments to content
 */
export interface Asset {
  type: string;      // 'PDF', 'Slide', 'Video', 'YouTube', etc.
  name: string;      // Display name
  url: string;       // URL to the asset
  fileId?: string;   // Optional ID if it's a file stored in the system
}

/**
 * Presenter/Author information
 */
export interface Presenter {
  id: string;
  name: string;
  company: string;
  title?: string;
  photoUrl?: string;
  bio?: string;
  email?: string;
}

/**
 * Comment on content items
 */
export interface Comment {
  id: string;
  userId: string;
  userName: string;
  userPhotoUrl?: string;
  text: string;
  timestamp: Date;
  replies?: Comment[];
}

/**
 * Main content interface
 */
export interface Content {
  id: string;
  title: string;
  description: string;
  abstract?: string;  // Shorter description for cards/previews
  track: string;      // Main categorization
  tags: string[];     // Searchable tags
  sessionType: string; // 'Workshop', 'Keynote', 'Breakout', etc.
  sessionDate?: string; // When the session occurs/occurred
  thumbnail?: string;   // URL to thumbnail image
  learningLevel?: string; // 'Beginner', 'Intermediate', 'Advanced'
  topic?: string;        // Specific topic within track
  jobRole?: string;      // Target audience job role
  areaOfInterest?: string; // Area of interest
  industry?: string;      // Relevant industry
  
  // Metadata
  status: 'draft' | 'review' | 'approved' | 'published' | 'rejected' | 'archived';
  dateCreated: Date | string;
  dateModified: Date | string;
  createdBy?: string;    // User ID
  updatedBy?: string;    // User ID
  version?: number;
  
  // UI flags
  priority?: boolean;    // High priority content
  recommended?: boolean; // Recommended to users
  bookmarked?: boolean;  // User has bookmarked (client-side only)
  
  // Related content
  presenters: Presenter[];
  assets?: Asset[];      // Attached files
  comments?: Comment[];  // User comments
  
  // AI-generated content
  aiSummary?: string;    // AI-generated summary
  aiTags?: string[];     // AI-suggested tags
}

/**
 * Search result wrapper
 */
export interface SearchResult {
  items: Content[];
  total: number;
  page?: number;
  pageSize?: number;
}

/**
 * Content chunk for AI processing
 */
export interface ContentChunk {
  contentId: string;
  chunkId: string;
  text: string;
  slideIndex?: number;
  slideId?: string;
  slideTitle?: string;
  fileType?: string;
  presentationId?: string;
}

/**
 * Filter option for search/filtering
 */
export interface FilterOption {
  value: string;
  label: string;
  selected: boolean;
  count: number;
}

/**
 * Filter category
 */
export interface Filter {
  name: string;
  options: FilterOption[];
  expanded: boolean;
} 