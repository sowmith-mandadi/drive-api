export interface Content {
  id?: string;
  title: string;
  description: string;
  track: string;
  tags: string[];
  sessionType: string;
  presenters: Presenter[];
  dateCreated?: Date;
  dateModified?: Date;
  fileUrls?: string[];
  driveUrls?: string[];
  aiSummary?: string;
  comments?: Comment[];
  used?: boolean;
  aiTags?: string[];
}

export interface Presenter {
  id?: string;
  name: string;
  bio?: string;
  company?: string;
  photoUrl?: string;
}

export interface Comment {
  id?: string;
  contentId: string;
  text: string;
  userId: string;
  userName: string;
  timestamp: Date;
  section?: string;
}

export interface Track {
  id: string;
  name: string;
  description?: string;
}

export interface SearchResult {
  content: Content[];
  totalCount: number;
  page: number;
  pageSize: number;
}

export interface UploadResponse {
  success: boolean;
  contentId?: string;
  error?: string;
}

export interface RagResponse {
  answer: string;
  passages: RagPassage[];
  contentScore: number;
  relevanceScore: number;
  groundingScore: number;
}

export interface RagPassage {
  text: string;
  source: string;
  score: number;
} 