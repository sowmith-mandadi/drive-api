import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatChipInputEvent } from '@angular/material/chips';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { ContentService } from '../../services/content.service';
import { DriveService } from '../../services/drive.service';
import { RagService } from '../../services/rag.service';
import { ConferenceDataService } from '../../services/conference-data.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { Track } from '../../models/content.model';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent implements OnInit {
  uploadForm!: FormGroup;
  files: File[] = [];
  driveFiles: any[] = [];
  uploading = false;
  progress = 0;
  
  // For tags input
  readonly separatorKeysCodes = [ENTER, COMMA] as const;
  tags: string[] = [];
  customPresenters: string[] = [];
  selectedPresenters: string[] = [];
  
  // Track options
  trackOptions: Track[] = [];
  sessionTypeOptions: string[] = [];
  availablePresenters: any[] = [];
  
  constructor(
    private fb: FormBuilder,
    private contentService: ContentService,
    private driveService: DriveService,
    private ragService: RagService,
    private conferenceDataService: ConferenceDataService,
    private snackBar: MatSnackBar,
    private router: Router
  ) { }
  
  ngOnInit(): void {
    this.createForm();
    this.loadConferenceData();
  }
  
  loadConferenceData(): void {
    forkJoin({
      tracks: this.conferenceDataService.getTracks(),
      sessionTypes: this.conferenceDataService.getSessionTypes(),
      speakers: this.conferenceDataService.getSpeakers()
    }).subscribe(
      ({ tracks, sessionTypes, speakers }) => {
        this.trackOptions = tracks;
        this.sessionTypeOptions = sessionTypes;
        this.availablePresenters = speakers;
      },
      error => {
        console.error('Error loading conference data:', error);
        this.snackBar.open('Failed to load conference data. Using default values.', 'Close', {
          duration: 3000
        });
      }
    );
  }
  
  createForm(): void {
    this.uploadForm = this.fb.group({
      title: ['', [Validators.required]],
      description: [''],
      track: [''],
      session_type: [''],
      slide_url: [''],
      video_url: [''],
      resources_url: [''],
      ai_summarize: [true],
      ai_tags: [true],
      ai_index: [true]
    });
  }
  
  // For file selection
  onFileSelect(event: any): void {
    if (event.target.files.length > 0) {
      const newFiles = Array.from(event.target.files) as File[];
      
      // Check if we're exceeding the limit (50 files)
      if (this.files.length + newFiles.length > 50) {
        this.snackBar.open('You can upload a maximum of 50 files at once.', 'Close', {
          duration: 3000
        });
        return;
      }
      
      // Add the files to our array
      this.files = [...this.files, ...newFiles];
    }
  }
  
  // Handle drag and drop
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
  }
  
  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    
    if (event.dataTransfer?.files.length) {
      const newFiles = Array.from(event.dataTransfer.files) as File[];
      
      // Check if we're exceeding the limit (50 files)
      if (this.files.length + newFiles.length > 50) {
        this.snackBar.open('You can upload a maximum of 50 files at once.', 'Close', {
          duration: 3000
        });
        return;
      }
      
      // Add the files to our array
      this.files = [...this.files, ...newFiles];
    }
  }
  
  // Remove a file from selection
  removeFile(file: File): void {
    const index = this.files.indexOf(file);
    if (index >= 0) {
      this.files.splice(index, 1);
    }
  }
  
  // Google Drive integration
  openDrivePicker(): void {
    this.driveService.createPicker().subscribe(
      docs => {
        if (docs) {
          // Load metadata for each selected file
          docs.forEach((doc: any) => {
            this.driveService.getFileMetadata(doc.id).subscribe(
              metadata => {
                this.driveFiles.push(metadata);
              },
              error => {
                console.error('Error fetching file metadata:', error);
                this.snackBar.open('Failed to get file details from Google Drive.', 'Close', {
                  duration: 3000
                });
              }
            );
          });
        }
      },
      error => {
        console.error('Error opening Google Drive picker:', error);
        this.snackBar.open('Failed to connect to Google Drive. Please try again.', 'Close', {
          duration: 3000
        });
      }
    );
  }
  
  removeDriveFile(file: any): void {
    const index = this.driveFiles.indexOf(file);
    if (index >= 0) {
      this.driveFiles.splice(index, 1);
    }
  }
  
  // Add tag chip
  addTag(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();
    
    if (value) {
      this.tags.push(value);
    }
    
    // Clear the input value
    event.chipInput!.clear();
  }
  
  // Remove tag chip
  removeTag(tag: string): void {
    const index = this.tags.indexOf(tag);
    
    if (index >= 0) {
      this.tags.splice(index, 1);
    }
  }
  
  // Add presenter chip
  addPresenter(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();
    
    if (value) {
      this.customPresenters.push(value);
    }
    
    // Clear the input value
    event.chipInput!.clear();
  }
  
  // Remove presenter chip
  removePresenter(presenter: string): void {
    const index = this.customPresenters.indexOf(presenter);
    
    if (index >= 0) {
      this.customPresenters.splice(index, 1);
    }
  }
  
  // Toggle presenter selection
  togglePresenter(speaker: any): void {
    const index = this.selectedPresenters.indexOf(speaker.id);
    
    if (index >= 0) {
      // Already selected, so remove
      this.selectedPresenters.splice(index, 1);
    } else {
      // Not selected, so add
      this.selectedPresenters.push(speaker.id);
    }
  }
  
  // Check if there are any files to upload
  hasAnyFiles(): boolean {
    return this.files.length > 0 || this.driveFiles.length > 0;
  }
  
  // Check if there are any links provided
  hasAnyLinks(): boolean {
    const slideUrl = this.uploadForm.get('slide_url')?.value;
    const videoUrl = this.uploadForm.get('video_url')?.value;
    const resourcesUrl = this.uploadForm.get('resources_url')?.value;
    
    return !!slideUrl || !!videoUrl || !!resourcesUrl;
  }
  
  // Submit the form
  onSubmit(): void {
    if (this.uploadForm.valid && (this.hasAnyFiles() || this.hasAnyLinks())) {
      this.uploading = true;
      this.progress = 0;
      
      // Simulate progress updates (in a real app, this would come from the upload progress)
      const interval = setInterval(() => {
        this.progress += 5;
        if (this.progress >= 100) {
          clearInterval(interval);
        }
      }, 200);
      
      // Create form data
      const formData = new FormData();
      
      // Add form fields
      formData.append('title', this.uploadForm.get('title')?.value);
      formData.append('description', this.uploadForm.get('description')?.value);
      formData.append('track', this.uploadForm.get('track')?.value);
      formData.append('session_type', this.uploadForm.get('session_type')?.value);
      formData.append('slide_url', this.uploadForm.get('slide_url')?.value);
      formData.append('video_url', this.uploadForm.get('video_url')?.value);
      formData.append('resources_url', this.uploadForm.get('resources_url')?.value);
      
      // Add tags and presenters
      formData.append('tags', JSON.stringify(this.tags));
      formData.append('selected_presenters', JSON.stringify(this.selectedPresenters));
      formData.append('custom_presenters', JSON.stringify(this.customPresenters));
      
      // Add AI processing flags
      formData.append('ai_summarize', String(this.uploadForm.get('ai_summarize')?.value));
      formData.append('ai_tags', String(this.uploadForm.get('ai_tags')?.value));
      formData.append('ai_index', String(this.uploadForm.get('ai_index')?.value));
      
      // Add Google Drive files
      if (this.driveFiles.length > 0) {
        formData.append('drive_files', JSON.stringify(this.driveFiles));
      }
      
      // Add local files
      this.files.forEach(file => {
        formData.append('files', file);
      });
      
      // Submit to the API
      this.contentService.uploadContent(formData).subscribe(
        response => {
          this.uploading = false;
          this.progress = 100;
          
          // If AI processing was requested, wait for it to complete
          if (this.uploadForm.get('ai_summarize')?.value || 
              this.uploadForm.get('ai_tags')?.value || 
              this.uploadForm.get('ai_index')?.value) {
            
            this.snackBar.open('Content uploaded successfully! AI processing in progress...', 'Close', {
              duration: 5000
            });
            
            // Navigate to the content detail page
            this.router.navigate(['/content', response.contentId]);
          } else {
            this.snackBar.open('Content uploaded successfully!', 'Close', {
              duration: 3000
            });
            
            // Navigate to the content detail page
            this.router.navigate(['/content', response.contentId]);
          }
        },
        error => {
          this.uploading = false;
          this.progress = 0;
          
          this.snackBar.open('Error uploading content. Please try again.', 'Close', {
            duration: 3000
          });
          
          console.error('Upload error:', error);
        }
      );
    } else {
      // Mark form controls as touched to show validation errors
      Object.keys(this.uploadForm.controls).forEach(key => {
        const control = this.uploadForm.get(key);
        control?.markAsTouched();
      });
      
      if (!this.hasAnyFiles() && !this.hasAnyLinks()) {
        this.snackBar.open('Please select at least one file or provide a link.', 'Close', {
          duration: 3000
        });
      }
    }
  }
} 