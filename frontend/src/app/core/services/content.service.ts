import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { Content, SearchResult } from '../../shared/models/content.model';

/**
 * Service for handling content data
 * Can toggle between using local JSON files and API endpoints
 */
@Injectable({
  providedIn: 'root'
})
export class ContentService {
  private apiUrl = '/api/content';
  private useApi = false; // Toggle between JSON files and API

  constructor(private http: HttpClient) {}

  /**
   * Get a specific content item by ID
   */
  getContent(id: string): Observable<Content | null> {
    if (this.useApi) {
      return this.http.get<Content>(`${this.apiUrl}/${id}`).pipe(
        catchError(() => of(null))
      );
    } else {
      return this.http.get<Content[]>('assets/data/all-content.json').pipe(
        map(contents => contents.find(c => c.id === id) || null),
        catchError(() => of(null))
      );
    }
  }

  /**
   * Get featured content items for home page carousel
   */
  getFeaturedContent(): Observable<Content[]> {
    if (this.useApi) {
      return this.http.get<Content[]>(`${this.apiUrl}/featured`).pipe(
        catchError(() => of([]))
      );
    } else {
      return this.http.get<Content[]>('assets/data/featured-content.json').pipe(
        catchError(() => of([]))
      );
    }
  }

  /**
   * Get latest content updates for home page
   */
  getLatestUpdates(): Observable<Content[]> {
    if (this.useApi) {
      return this.http.get<Content[]>(`${this.apiUrl}/latest`).pipe(
        catchError(() => of([]))
      );
    } else {
      return this.http.get<Content[]>('assets/data/latest-updates.json').pipe(
        catchError(() => of([]))
      );
    }
  }

  /**
   * Get recommended content for home page
   */
  getRecommendedContent(): Observable<Content[]> {
    if (this.useApi) {
      return this.http.get<Content[]>(`${this.apiUrl}/recommended`).pipe(
        catchError(() => of([]))
      );
    } else {
      return this.http.get<Content[]>('assets/data/recommended-content.json').pipe(
        catchError(() => of([]))
      );
    }
  }

  /**
   * Search for content with filters, sorting, and pagination
   */
  searchContent(params: any): Observable<SearchResult> {
    if (this.useApi) {
      return this.http.post<SearchResult>(`${this.apiUrl}/search`, params).pipe(
        catchError(() => of({ items: [], total: 0 }))
      );
    } else {
      return this.http.get<Content[]>('assets/data/all-content.json').pipe(
        map(contents => {
          const filtered = this.applyFilters(contents, params);
          const sorted = this.applySorting(filtered, params.sort || 'newest');
          const paginated = this.applyPagination(sorted, params.page || 0, params.size || 10);
          
          return {
            items: paginated,
            total: filtered.length,
            page: params.page || 0,
            pageSize: params.size || 10
          };
        }),
        catchError(() => of({ items: [], total: 0 }))
      );
    }
  }

  /**
   * Apply filters to content items
   * @param contents Array of content items
   * @param params Search parameters with filters
   */
  private applyFilters(contents: Content[], params: any): Content[] {
    if (!params) return contents;
    
    return contents.filter(item => {
      // Apply text search if query exists
      if (params.query && params.query.trim() !== '') {
        const query = params.query.toLowerCase();
        const titleMatch = item.title?.toLowerCase().includes(query);
        const descMatch = item.description?.toLowerCase().includes(query);
        const abstractMatch = item.abstract?.toLowerCase().includes(query);
        const tagsMatch = item.tags?.some(tag => tag.toLowerCase().includes(query));

        if (!(titleMatch || descMatch || abstractMatch || tagsMatch)) {
          return false;
        }
      }

      // Apply track filter
      if (params.track && params.track.length > 0) {
        if (!params.track.includes(item.track)) {
          return false;
        }
      }

      // Apply session type filter
      if (params.sessionType && params.sessionType.length > 0) {
        if (!params.sessionType.includes(item.sessionType)) {
          return false;
        }
      }

      // Apply learning level filter
      if (params.learningLevel && params.learningLevel.length > 0) {
        if (!params.learningLevel.includes(item.learningLevel)) {
          return false;
        }
      }

      // Apply status filter
      if (params.status && params.status.length > 0) {
        if (!params.status.includes(item.status)) {
          return false;
        }
      }

      // Apply tags filter
      if (params.tags && params.tags.length > 0) {
        if (!item.tags?.some(tag => params.tags.includes(tag))) {
          return false;
        }
      }

      return true;
    });
  }

  /**
   * Apply sorting to content items
   * @param contents Array of content items
   * @param sortField Field to sort by
   */
  private applySorting(contents: Content[], sortField: string): Content[] {
    const items = [...contents]; // Create a copy to avoid modifying the original

    switch (sortField) {
      case 'newest':
        return items.sort((a, b) => {
          const dateA = new Date(a.dateModified || a.dateCreated).getTime();
          const dateB = new Date(b.dateModified || b.dateCreated).getTime();
          return dateB - dateA;
        });
      
      case 'oldest':
        return items.sort((a, b) => {
          const dateA = new Date(a.dateCreated).getTime();
          const dateB = new Date(b.dateCreated).getTime();
          return dateA - dateB;
        });
      
      case 'title':
        return items.sort((a, b) => a.title.localeCompare(b.title));
      
      case 'relevance':
      default:
        // For relevance, we would normally rely on backend scoring
        // For local JSON, just maintain the original order
        return items;
    }
  }

  /**
   * Apply pagination to content items
   * @param contents Array of content items
   * @param page Page number (0-based)
   * @param size Items per page
   */
  private applyPagination(contents: Content[], page: number, size: number): Content[] {
    const startIndex = page * size;
    return contents.slice(startIndex, startIndex + size);
  }
} 