import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
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
    return this.http.post(`${this.apiUrl}/upload`, formData).pipe(
      catchError(error => {
        console.error('Error uploading content:', error);
        return throwError(() => new Error('Failed to upload content. Please try again.'));
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