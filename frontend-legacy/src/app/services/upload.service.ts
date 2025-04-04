import { Injectable } from '@angular/core';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { UploadResponse } from '../models/content.model';

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  private apiUrl = environment.apiUrl;
  uploadProgress = new BehaviorSubject<number>(0);
  
  constructor(private http: HttpClient) {}

  // Upload files to server
  uploadFiles(files: File[], metadata: any): Observable<UploadResponse> {
    const formData = new FormData();
    
    // Append files
    files.forEach((file, index) => {
      formData.append(`files`, file);
    });
    
    // Append metadata
    Object.keys(metadata).forEach(key => {
      if (metadata[key] !== null && metadata[key] !== undefined) {
        if (Array.isArray(metadata[key])) {
          formData.append(key, JSON.stringify(metadata[key]));
        } else {
          formData.append(key, metadata[key]);
        }
      }
    });
    
    return this.http.post<UploadResponse>(`${this.apiUrl}/upload`, formData, {
      reportProgress: true,
      observe: 'events'
    }).pipe(
      map(event => {
        switch (event.type) {
          case HttpEventType.UploadProgress:
            if (event.total) {
              const progress = Math.round(100 * event.loaded / event.total);
              this.uploadProgress.next(progress);
            }
            return { success: true } as UploadResponse;
          
          case HttpEventType.Response:
            return event.body as UploadResponse;
            
          default:
            return { success: true } as UploadResponse;
        }
      }),
      catchError(error => {
        console.error('Error uploading files:', error);
        return throwError(() => new Error('Failed to upload files. Please try again.'));
      })
    );
  }

  // Upload Google Drive files
  uploadDriveFiles(fileIds: string[], metadata: any): Observable<UploadResponse> {
    const payload = {
      fileIds,
      metadata
    };
    
    return this.http.post<UploadResponse>(`${this.apiUrl}/drive/import`, payload).pipe(
      catchError(error => {
        console.error('Error uploading Drive files:', error);
        return throwError(() => new Error('Failed to upload files from Google Drive. Please try again.'));
      })
    );
  }
  
  // Reset progress tracker
  resetProgress(): void {
    this.uploadProgress.next(0);
  }
} 