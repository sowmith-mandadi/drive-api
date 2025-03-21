export interface Content {
  id?: string;
  title: string;
  description: string;
  track: string;
  tags: string[];
  sessionType: string;
  sessionDate?: string;
  learningLevel?: string;
  topic?: string;
  jobRole?: string;
  areaOfInterest?: string;
  industry?: string;
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

export interface SessionType {
  id: string;
  name: string;
}

export interface SessionDate {
  id: string;
  date: string;
}

export interface LearningLevel {
  id: string;
  name: string;
}

export interface Topic {
  id: string;
  name: string;
}

export interface JobRole {
  id: string;
  name: string;
}

export interface AreaOfInterest {
  id: string;
  name: string;
}

export interface Industry {
  id: string;
  name: string;
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