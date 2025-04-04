import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { RagResponse } from '../models/content.model';

@Injectable({
  providedIn: 'root'
})
export class RagService {
  private apiUrl = environment.vertexAIApiUrl;
  
  constructor(private http: HttpClient) { }
  
  /**
   * Ask a question and get an answer using RAG (Retrieval-Augmented Generation)
   * @param question The question to ask
   * @param contentIds Optional array of content IDs to limit the search scope
   * @param filters Optional filters to apply to the search (tracks, tags, etc.)
   */
  askQuestion(question: string, contentIds?: string[], filters?: any): Observable<RagResponse> {
    const payload = {
      question,
      contentIds,
      filters
    };
    
    return this.http.post<RagResponse>(`${this.apiUrl}/ask`, payload).pipe(
      catchError(error => {
        console.error('Error asking question using RAG:', error);
        return throwError(() => new Error('Failed to get answer. Please try again.'));
      })
    );
  }
  
  /**
   * Summarize a document using Vertex AI
   * @param contentId ID of the content to summarize
   */
  summarizeDocument(contentId: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/summarize`, { contentId }).pipe(
      catchError(error => {
        console.error('Error summarizing document:', error);
        return throwError(() => new Error('Failed to summarize document. Please try again.'));
      })
    );
  }
  
  /**
   * Generate tags for a document using Vertex AI
   * @param contentId ID of the content to generate tags for
   */
  generateTags(contentId: string): Observable<string[]> {
    return this.http.post<string[]>(`${this.apiUrl}/generate-tags`, { contentId }).pipe(
      catchError(error => {
        console.error('Error generating tags:', error);
        return throwError(() => new Error('Failed to generate tags. Please try again.'));
      })
    );
  }
  
  /**
   * Retrieve similar documents based on a query or document ID
   * @param query Text query to find similar documents
   * @param contentId Optional content ID to find similar to this document
   * @param limit Maximum number of results to return
   */
  findSimilarDocuments(query?: string, contentId?: string, limit: number = 5): Observable<any[]> {
    const payload = {
      query,
      contentId,
      limit
    };
    
    return this.http.post<any[]>(`${this.apiUrl}/similar`, payload).pipe(
      catchError(error => {
        console.error('Error finding similar documents:', error);
        return throwError(() => new Error('Failed to find similar documents. Please try again.'));
      })
    );
  }
} 