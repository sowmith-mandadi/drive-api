import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpEventType } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { Content, SearchResult } from '../models/content.model';

@Injectable({
  providedIn: 'root'
})
export class ContentService {
  private apiUrl = environment.apiUrl;
  
  constructor(private http: HttpClient) { }
  
  // Upload content (files and metadata)
  uploadContent(formData: FormData): Observable<any> {
    // Configure for longer timeout
    const httpOptions = {
      headers: new HttpHeaders({
        'Accept': 'application/json',
      }),
      // Increase timeout for large uploads (5 minutes)
      reportProgress: true,
      observe: 'events' as 'events'
    };
    
    return this.http.post(`${this.apiUrl}/upload`, formData, httpOptions).pipe(
      map(event => {
        // Return the final response when complete
        if (event.type === HttpEventType.Response) {
          return event.body;
        }
        return null;
      }),
      catchError(error => {
        console.error('Error uploading content:', error);
        let errorMessage = 'Failed to upload content. Please try again.';
        
        if (error.status === 413) {
          errorMessage = 'The file is too large to upload. Maximum file size is 100MB.';
        } else if (error.name === 'TimeoutError') {
          errorMessage = 'Upload timed out. Please try again with a smaller file or check your connection.';
        }
        
        return throwError(() => new Error(errorMessage));
      })
    );
  }
  
  // Import files from Google Drive
  importDriveFiles(fileIds: string[], metadata: any): Observable<any> {
    const payload = { 
      fileIds,
      metadata 
    };
    
    return this.http.post(`${this.apiUrl}/drive/import`, payload).pipe(
      catchError(error => {
        console.error('Error importing files from Google Drive:', error);
        return throwError(() => new Error('Failed to import files from Google Drive. Please try again.'));
      })
    );
  }
  
  // Create content without files (only links/metadata)
  createContentWithoutFiles(metadata: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/content`, metadata).pipe(
      catchError(error => {
        console.error('Error creating content:', error);
        return throwError(() => new Error('Failed to create content. Please try again.'));
      })
    );
  }
  
  // Get content details by ID
  getContentById(id: string): Observable<Content> {
    return this.http.get<Content>(`${this.apiUrl}/content/${id}`).pipe(
      catchError(error => {
        console.error(`Error fetching content with ID ${id}:`, error);
        return throwError(() => new Error('Failed to fetch content details. Please try again.'));
      })
    );
  }
  
  // Get multiple content items by their IDs
  getContentByIds(ids: string[]): Observable<Content[]> {
    return this.http.post<Content[]>(`${this.apiUrl}/content-by-ids`, { ids }).pipe(
      catchError(error => {
        console.error('Error fetching multiple content items:', error);
        return throwError(() => new Error('Failed to fetch content details. Please try again.'));
      })
    );
  }
  
  // Search for content
  searchContent(query: string, filters?: any, page: number = 1, pageSize: number = 10): Observable<SearchResult> {
    const searchParams = {
      query,
      filters,
      page,
      page_size: pageSize
    };
    
    return this.http.post<SearchResult>(`${this.apiUrl}/search`, searchParams).pipe(
      catchError(error => {
        console.error('Error searching content:', error);
        return throwError(() => new Error('Failed to search content. Please try again.'));
      })
    );
  }
  
  // Get recent content
  getRecentContent(page: number = 1, pageSize: number = 10): Observable<SearchResult> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
      
    return this.http.get<SearchResult>(`${this.apiUrl}/recent-content`, { params }).pipe(
      catchError(error => {
        console.error('Error fetching recent content:', error);
        return throwError(() => new Error('Failed to fetch recent content. Please try again.'));
      })
    );
  }
  
  // Get popular tags
  getPopularTags(limit: number = 20): Observable<string[]> {
    return this.http.get<string[]>(`${this.apiUrl}/popular-tags?limit=${limit}`).pipe(
      catchError(error => {
        console.error('Error fetching popular tags:', error);
        return throwError(() => new Error('Failed to fetch popular tags. Please try again.'));
      })
    );
  }
  
  // Add a comment to content
  addComment(contentId: string, comment: string, section?: string): Observable<any> {
    const commentData = {
      content_id: contentId,
      comment,
      section,
      timestamp: new Date().toISOString()
    };
    
    return this.http.post(`${this.apiUrl}/comment`, commentData).pipe(
      catchError(error => {
        console.error('Error adding comment:', error);
        return throwError(() => new Error('Failed to add comment. Please try again.'));
      })
    );
  }
  
  // Mark content as used
  markAsUsed(contentId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/mark-used`, { content_id: contentId }).pipe(
      catchError(error => {
        console.error('Error marking content as used:', error);
        return throwError(() => new Error('Failed to mark content as used. Please try again.'));
      })
    );
  }
  
  // Get track options (deprecated - use ConferenceDataService instead)
  getTrackOptions(): Observable<string[]> {
    console.warn('getTrackOptions() is deprecated. Use ConferenceDataService.getTracks() instead.');
    // This could be fetched from the API in a real implementation
    // For now, returning static options
    return new Observable(observer => {
      observer.next([
        'Development',
        'Design',
        'Marketing',
        'Business',
        'AI & Machine Learning',
        'Cloud & Infrastructure',
        'Mobile',
        'Web'
      ]);
      observer.complete();
    });
  }
  
  // Get session type options (deprecated - use ConferenceDataService instead)
  getSessionTypeOptions(): Observable<string[]> {
    console.warn('getSessionTypeOptions() is deprecated. Use ConferenceDataService.getSessionTypes() instead.');
    // This could be fetched from the API in a real implementation
    // For now, returning static options
    return new Observable(observer => {
      observer.next([
        'Keynote',
        'Breakout Session',
        'Workshop',
        'Panel',
        'Lightning Talk',
        'Demo'
      ]);
      observer.complete();
    });
  }
} 