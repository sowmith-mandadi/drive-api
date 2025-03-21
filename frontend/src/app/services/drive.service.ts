import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject, of, from } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DriveService {
  private apiUrl = environment.apiUrl;
  private gapi: any;
  private tokenClient: any;
  private pickerInitialized = false;
  
  constructor(private http: HttpClient) {
    this.loadDriveApi();
  }
  
  /**
   * Load the Google Drive API
   */
  private loadDriveApi(): void {
    // Load Google API client library script
    const script = document.createElement('script');
    script.src = 'https://apis.google.com/js/api.js';
    script.onload = () => {
      // Load and initialize the auth client
      this.gapi = (window as any).gapi;
      this.gapi.load('client:auth2', this.initGapiClient.bind(this));
    };
    document.body.appendChild(script);
    
    // Load Google Identity Services script
    const gsisScript = document.createElement('script');
    gsisScript.src = 'https://accounts.google.com/gsi/client';
    gsisScript.onload = () => {
      // Create token client for authorization
      this.tokenClient = (window as any).google?.accounts.oauth2.initTokenClient({
        client_id: environment.google.clientId,
        scope: environment.google.scopes.join(' '),
        callback: () => {}
      });
    };
    document.body.appendChild(gsisScript);
  }
  
  /**
   * Initialize Google API client
   */
  private initGapiClient(): void {
    this.gapi.client.init({
      apiKey: environment.google.apiKey,
      discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/drive/v3/rest']
    });
  }
  
  /**
   * Create and open the Google Drive picker
   */
  createPicker(): Observable<any[]> {
    const result = new Subject<any[]>();
    
    // If Google API or Google Identity Services not loaded yet, return empty result
    if (!this.gapi || !this.tokenClient) {
      console.error('Google API not loaded yet');
      return of([]);
    }
    
    // Load the picker API if not loaded yet
    if (!this.pickerInitialized) {
      this.gapi.load('picker', () => {
        this.pickerInitialized = true;
        this.showPicker(result);
      });
    } else {
      this.showPicker(result);
    }
    
    return result.asObservable();
  }
  
  /**
   * Show the Google Drive picker
   */
  private showPicker(result: Subject<any[]>): void {
    // Request an access token
    this.tokenClient.callback = async (response: any) => {
      if (response.error) {
        console.error('Error getting token:', response.error);
        result.error(new Error('Failed to get access token'));
        return;
      }
      
      const accessToken = response.access_token;
      const picker = new (window as any).google.picker.PickerBuilder()
        .addView(new (window as any).google.picker.DocsView())
        .addView(new (window as any).google.picker.DocsUploadView())
        .setOAuthToken(accessToken)
        .setDeveloperKey(environment.google.apiKey)
        .setCallback((data: any) => {
          if (data.action === 'picked') {
            result.next(data.docs);
            result.complete();
          } else if (data.action === 'cancel') {
            result.next([]);
            result.complete();
          }
        })
        .build();
      picker.setVisible(true);
    };
    
    // Prompt for consent
    this.tokenClient.requestAccessToken({ prompt: 'consent' });
  }
  
  /**
   * Get metadata for a Google Drive file
   * @param fileId The Google Drive file ID
   */
  getFileMetadata(fileId: string): Observable<any> {
    // Try using Google API if available
    if (this.gapi && this.gapi.client && this.gapi.client.drive) {
      return from(this.gapi.client.drive.files.get({
        fileId: fileId,
        fields: 'id,name,mimeType,webViewLink,iconLink,thumbnailLink'
      })).pipe(
        map((response: any) => response.result),
        catchError(error => {
          console.error('Error fetching file metadata from Google Drive API:', error);
          // Fallback to our backend
          return this.http.get(`${this.apiUrl}/drive/files/${fileId}`);
        })
      );
    }
    
    // Fallback to our backend
    return this.http.get(`${this.apiUrl}/drive/files/${fileId}`).pipe(
      catchError(error => {
        console.error('Error fetching file metadata from backend:', error);
        return of({
          id: fileId,
          name: 'Unknown file',
          mimeType: 'application/octet-stream',
          webViewLink: `https://drive.google.com/file/d/${fileId}/view`
        });
      })
    );
  }
  
  /**
   * Import files from Google Drive to the system
   * @param fileIds Array of Google Drive file IDs
   * @param contentId Optional content ID to associate the files with
   */
  importDriveFiles(fileIds: string[], contentId?: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/drive/import`, { fileIds, contentId }).pipe(
      catchError(error => {
        console.error('Error importing files from Google Drive:', error);
        return of({ success: false, error: 'Failed to import files from Google Drive' });
      })
    );
  }
} 