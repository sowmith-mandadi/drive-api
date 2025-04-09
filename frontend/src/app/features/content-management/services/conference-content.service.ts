import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { 
  ConferenceSchema, 
  ConferenceContent, 
  ContentTypeDefinition,
  FilterConfiguration,
  ContentVersion,
  UserAction
} from '../models/conference.model';

@Injectable({
  providedIn: 'root'
})
export class ConferenceContentService {
  private apiUrl = '/api/conferences';

  constructor(private http: HttpClient) { }

  // Conference Schema Management
  getConferenceSchemas(): Observable<ConferenceSchema[]> {
    return this.http.get<ConferenceSchema[]>(`${this.apiUrl}/schemas`)
      .pipe(
        catchError(this.handleError('getConferenceSchemas', []))
      );
  }

  getConferenceSchema(id: string): Observable<ConferenceSchema> {
    return this.http.get<ConferenceSchema>(`${this.apiUrl}/schemas/${id}`)
      .pipe(
        catchError(this.handleError<ConferenceSchema>('getConferenceSchema'))
      );
  }

  createConferenceSchema(schema: Partial<ConferenceSchema>): Observable<ConferenceSchema> {
    return this.http.post<ConferenceSchema>(`${this.apiUrl}/schemas`, schema)
      .pipe(
        catchError(this.handleError<ConferenceSchema>('createConferenceSchema'))
      );
  }

  updateConferenceSchema(id: string, schema: Partial<ConferenceSchema>): Observable<ConferenceSchema> {
    return this.http.put<ConferenceSchema>(`${this.apiUrl}/schemas/${id}`, schema)
      .pipe(
        catchError(this.handleError<ConferenceSchema>('updateConferenceSchema'))
      );
  }

  cloneConferenceSchema(id: string, newYear: number, fieldsToRetain: string[]): Observable<ConferenceSchema> {
    return this.http.post<ConferenceSchema>(`${this.apiUrl}/schemas/${id}/clone`, { newYear, fieldsToRetain })
      .pipe(
        catchError(this.handleError<ConferenceSchema>('cloneConferenceSchema'))
      );
  }

  // Content Management
  getContentItems(conferenceId: string, filters?: any, page: number = 1, pageSize: number = 20): Observable<{items: ConferenceContent[], total: number}> {
    return this.http.get<{items: ConferenceContent[], total: number}>(`${this.apiUrl}/${conferenceId}/content`, {
      params: { 
        page: page.toString(), 
        pageSize: pageSize.toString(),
        ...filters
      }
    }).pipe(
      catchError(this.handleError<{items: ConferenceContent[], total: number}>('getContentItems', {items: [], total: 0}))
    );
  }

  getContentItem(conferenceId: string, contentId: string): Observable<ConferenceContent> {
    return this.http.get<ConferenceContent>(`${this.apiUrl}/${conferenceId}/content/${contentId}`)
      .pipe(
        catchError(this.handleError<ConferenceContent>('getContentItem'))
      );
  }

  createContentItem(conferenceId: string, content: Partial<ConferenceContent>): Observable<ConferenceContent> {
    return this.http.post<ConferenceContent>(`${this.apiUrl}/${conferenceId}/content`, content)
      .pipe(
        catchError(this.handleError<ConferenceContent>('createContentItem'))
      );
  }

  updateContentItem(conferenceId: string, contentId: string, content: Partial<ConferenceContent>): Observable<ConferenceContent> {
    return this.http.put<ConferenceContent>(`${this.apiUrl}/${conferenceId}/content/${contentId}`, content)
      .pipe(
        catchError(this.handleError<ConferenceContent>('updateContentItem'))
      );
  }

  deleteContentItem(conferenceId: string, contentId: string): Observable<boolean> {
    return this.http.delete<void>(`${this.apiUrl}/${conferenceId}/content/${contentId}`)
      .pipe(
        map(() => true),
        catchError(this.handleError<boolean>('deleteContentItem', false))
      );
  }

  // Batch Operations
  batchUpdateStatus(conferenceId: string, contentIds: string[], status: string): Observable<boolean> {
    return this.http.post<void>(`${this.apiUrl}/${conferenceId}/content/batch/status`, { contentIds, status })
      .pipe(
        map(() => true),
        catchError(this.handleError<boolean>('batchUpdateStatus', false))
      );
  }

  batchUpdateTags(conferenceId: string, contentIds: string[], addTags: string[], removeTags: string[]): Observable<boolean> {
    return this.http.post<void>(`${this.apiUrl}/${conferenceId}/content/batch/tags`, { contentIds, addTags, removeTags })
      .pipe(
        map(() => true),
        catchError(this.handleError<boolean>('batchUpdateTags', false))
      );
  }

  // Version Management
  getContentVersions(conferenceId: string, contentId: string): Observable<ContentVersion[]> {
    return this.http.get<ContentVersion[]>(`${this.apiUrl}/${conferenceId}/content/${contentId}/versions`)
      .pipe(
        catchError(this.handleError<ContentVersion[]>('getContentVersions', []))
      );
  }

  revertToVersion(conferenceId: string, contentId: string, versionId: string): Observable<ConferenceContent> {
    return this.http.post<ConferenceContent>(`${this.apiUrl}/${conferenceId}/content/${contentId}/revert/${versionId}`, {})
      .pipe(
        catchError(this.handleError<ConferenceContent>('revertToVersion'))
      );
  }

  // Filter Management
  getSavedFilters(userId: string): Observable<FilterConfiguration[]> {
    return this.http.get<FilterConfiguration[]>(`${this.apiUrl}/filters/${userId}`)
      .pipe(
        catchError(this.handleError<FilterConfiguration[]>('getSavedFilters', []))
      );
  }

  saveFilterConfiguration(filter: FilterConfiguration): Observable<FilterConfiguration> {
    return this.http.post<FilterConfiguration>(`${this.apiUrl}/filters`, filter)
      .pipe(
        catchError(this.handleError<FilterConfiguration>('saveFilterConfiguration'))
      );
  }

  // Audit Logs
  getUserActions(conferenceId?: string, contentId?: string, userId?: string, startDate?: Date, endDate?: Date): Observable<UserAction[]> {
    let params: any = {};
    if (conferenceId) params.conferenceId = conferenceId;
    if (contentId) params.contentId = contentId;
    if (userId) params.userId = userId;
    if (startDate) params.startDate = startDate.toISOString();
    if (endDate) params.endDate = endDate.toISOString();

    return this.http.get<UserAction[]>(`${this.apiUrl}/audit`, { params })
      .pipe(
        catchError(this.handleError<UserAction[]>('getUserActions', []))
      );
  }

  // Analytics and Reporting
  getContentStats(conferenceId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${conferenceId}/stats`)
      .pipe(
        catchError(this.handleError<any>('getContentStats', {}))
      );
  }

  // Cross-Conference Analytics
  getCrossConferenceMetrics(conferenceIds: string[], metricType: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/analytics/cross-conference`, { conferenceIds, metricType })
      .pipe(
        catchError(this.handleError<any>('getCrossConferenceMetrics', {}))
      );
  }

  // Error handling
  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {
      console.error(`${operation} failed: ${error.message}`);
      
      // Let the app keep running by returning an empty result
      return of(result as T);
    };
  }
} 