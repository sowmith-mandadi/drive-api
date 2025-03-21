import { Component, OnInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { MatChipInputEvent } from '@angular/material/chips';
import { ContentService } from '../../services/content.service';
import { DriveService } from '../../services/drive.service';
import { RagService } from '../../services/rag.service';
import { ConferenceDataService } from '../../services/conference-data.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { 
  Track, 
  UploadResponse, 
  SessionType, 
  SessionDate, 
  LearningLevel, 
  Topic, 
  JobRole, 
  AreaOfInterest, 
  Industry 
} from '../../models/content.model';
import { UploadService } from '../../services/upload.service';
import { NotificationService } from '../../services/notification.service';
import { Subscription, Observable } from 'rxjs';
import { switchMap, catchError, map } from 'rxjs/operators';
import { MatDialog } from '@angular/material/dialog';

interface DriveFile {
  id: string;
  name: string;
  mimeType: string;
  webViewLink: string;
  iconLink?: string;
  thumbnailLink?: string;
}

interface AiGeneratedContent {
  summary: string;
  tags: string[];
}

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent implements OnInit, OnDestroy {
  uploadForm!: FormGroup;
  separatorKeysCodes: number[] = [ENTER, COMMA];
  tags: string[] = [];
  
  trackOptions: Track[] = [];
  sessionTypeOptions: SessionType[] = [];
  sessionDateOptions: SessionDate[] = [];
  learningLevelOptions: LearningLevel[] = [];
  topicOptions: Topic[] = [];
  jobRoleOptions: JobRole[] = [];
  areaOfInterestOptions: AreaOfInterest[] = [];
  industryOptions: Industry[] = [];
  
  files: File[] = [];
  driveFiles: DriveFile[] = [];
  uploading: boolean = false;
  progress: number = 0;
  
  // New properties for displaying AI-generated content
  aiGeneratedContent: AiGeneratedContent | null = null;
  showAiContent: boolean = false;
  
  private subs = new Subscription();
  
  @ViewChild('fileInput') fileInput!: ElementRef;
  
  constructor(
    private fb: FormBuilder,
    private contentService: ContentService,
    private driveService: DriveService,
    private ragService: RagService,
    private conferenceDataService: ConferenceDataService,
    private snackBar: MatSnackBar,
    private router: Router,
    private uploadService: UploadService,
    private notificationService: NotificationService,
    private dialog: MatDialog
  ) { }
  
  ngOnInit(): void {
    this.initForm();
    this.loadMetadata();
    
    // Subscribe to upload progress
    this.subs.add(
      this.uploadService.uploadProgress.subscribe(progress => {
        this.progress = progress;
      })
    );
  }
  
  ngOnDestroy(): void {
    this.subs.unsubscribe();
    this.uploadService.resetProgress();
  }
  
  private initForm(): void {
    this.uploadForm = this.fb.group({
      title: ['', Validators.required],
      description: [''],
      track: [''],
      session_type: [''],
      session_date: [''],
      learning_level: [''],
      topic: [''],
      job_role: [''],
      area_of_interest: [''],
      industry: [''],
      slide_url: [''],
      video_url: [''],
      resources_url: [''],
      ai_summarize: [true],
      ai_tags: [true],
      ai_index: [false],
      contentId: [null]
    });
  }
  
  private loadMetadata(): void {
    // Initialize session dates
    this.sessionDateOptions = [
      { id: 'april-9', date: 'April 9' },
      { id: 'april-10', date: 'April 10' },
      { id: 'april-11', date: 'April 11' }
    ];
    
    // Initialize session types
    this.sessionTypeOptions = [
      { id: 'keynotes', name: 'Keynotes' },
      { id: 'spotlights', name: 'Spotlights' },
      { id: 'breakouts', name: 'Breakouts' },
      { id: 'cloud-talks', name: 'Cloud talks' },
      { id: 'developer-meetups', name: 'Developer Meetups' },
      { id: 'expo-experiences', name: 'Expo Experiences' },
      { id: 'learning-center-workshops', name: 'Learning Center Workshops' },
      { id: 'lightning-talks', name: 'Lightning Talks' },
      { id: 'lounge-sessions', name: 'Lounge Sessions' },
      { id: 'showcase-demos', name: 'Showcase Demos' },
      { id: 'solution-talks', name: 'Solution Talks' }
    ];
    
    // Initialize learning levels
    this.learningLevelOptions = [
      { id: 'introductory', name: 'Introductory' },
      { id: 'technical', name: 'Technical' },
      { id: 'advanced-technical', name: 'Advanced Technical' },
      { id: 'general', name: 'General' }
    ];
    
    // Initialize topics
    this.topicOptions = [
      { id: 'apis', name: 'APIs' },
      { id: 'app-dev', name: 'App Dev' },
      { id: 'applied-ai', name: 'Applied AI' },
      { id: 'architecture', name: 'Architecture' },
      { id: 'business-intelligence', name: 'Business Intelligence' },
      { id: 'chrome', name: 'Chrome' },
      { id: 'compute', name: 'Compute' },
      { id: 'cost-optimization', name: 'Cost Optimization' },
      { id: 'data-analytics', name: 'Data Analytics' },
      { id: 'databases', name: 'Databases' },
      { id: 'firebase', name: 'Firebase' },
      { id: 'gender', name: 'Gender' },
      { id: 'kaggle', name: 'Kaggle' },
      { id: 'migration', name: 'Migration' },
      { id: 'multicloud', name: 'Multicloud' },
      { id: 'networking', name: 'Networking' },
      { id: 'security', name: 'Security' },
      { id: 'serverless', name: 'Serverless' },
      { id: 'storage', name: 'Storage' },
      { id: 'vertex-ai', name: 'Vertex AI' },
      { id: 'workspace', name: 'Workspace' }
    ];
    
    // Initialize job roles
    this.jobRoleOptions = [
      { id: 'application-developers', name: 'Application Developers' },
      { id: 'data-professionals', name: 'Data Analysts, Data Scientists, Data Engineers' },
      { id: 'database-professionals', name: 'Database Professionals' },
      { id: 'devops', name: 'DevOps, IT Ops, Platform Engineers, SREs' },
      { id: 'executive', name: 'Executive' },
      { id: 'infrastructure', name: 'Infrastructure Architects & Operators' },
      { id: 'it-managers', name: 'IT Managers & Business Technology Leaders' },
      { id: 'security-professionals', name: 'Security Professionals' }
    ];
    
    // Initialize areas of interest
    this.areaOfInterestOptions = [
      { id: 'build-for-everyone', name: 'Build for Everyone' },
      { id: 'customer-story', name: 'Customer Story' },
      { id: 'developer-experiences', name: 'Developer Experiences' },
      { id: 'partner-innovation', name: 'Partner Innovation' },
      { id: 'small-it-teams', name: 'Small IT Teams' },
      { id: 'startup', name: 'Startup' },
      { id: 'sustainability', name: 'Sustainability' },
      { id: 'technology-leadership', name: 'Technology & Leadership' }
    ];
    
    // Initialize industries
    this.industryOptions = [
      { id: 'consumer-packaged-goods', name: 'Consumer & Packaged Goods' },
      { id: 'cross-industry-solutions', name: 'Cross-Industry Solutions' },
      { id: 'education', name: 'Education' },
      { id: 'financial-services', name: 'Financial Services' },
      { id: 'games', name: 'Games' },
      { id: 'government', name: 'Government' },
      { id: 'healthcare-life-sciences', name: 'Healthcare & Life Sciences' },
      { id: 'manufacturing', name: 'Manufacturing' },
      { id: 'media-entertainment', name: 'Media & Entertainment' },
      { id: 'public-sector', name: 'Public Sector' },
      { id: 'retail', name: 'Retail' },
      { id: 'supply-chain-logistics', name: 'Supply Chain & Logistics' },
      { id: 'technology', name: 'Technology' },
      { id: 'telecommunications', name: 'Telecommunications' }
    ];
    
    // Load tracks
    this.loadTracks();
  }
  
  private loadTracks(): void {
    this.subs.add(
      this.conferenceDataService.getTracks().subscribe(
        tracks => {
          this.trackOptions = tracks;
        },
        error => {
          console.error('Error loading tracks:', error);
          this.showMessage('Could not load track options');
          
          // Fallback to simulated data
          this.trackOptions = [
            { id: 'web', name: 'Web Development' },
            { id: 'mobile', name: 'Mobile Development' },
            { id: 'cloud', name: 'Cloud & DevOps' },
            { id: 'ai', name: 'AI & Machine Learning' },
            { id: 'data', name: 'Data Science & Analytics' },
            { id: 'security', name: 'Security & Privacy' },
            { id: 'design', name: 'UX & Design' },
            { id: 'career', name: 'Career & Leadership' }
          ];
        }
      )
    );
  }
  
  // Tag management
  addTag(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();
    
    if (value) {
      this.tags.push(value);
    }
    
    event.chipInput!.clear();
  }
  
  removeTag(tag: string): void {
    const index = this.tags.indexOf(tag);
    
    if (index >= 0) {
      this.tags.splice(index, 1);
    }
  }
  
  // Add AI-generated tags to user tags
  addAiTagsToUserTags(): void {
    if (this.aiGeneratedContent && this.aiGeneratedContent.tags) {
      // Filter out tags that are already in user tags
      const newTags = this.aiGeneratedContent.tags.filter(tag => !this.tags.includes(tag));
      this.tags = [...this.tags, ...newTags];
      this.showMessage(`Added ${newTags.length} AI-generated tags`);
    }
  }
  
  // File handling
  onFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    
    if (input.files) {
      for (let i = 0; i < input.files.length; i++) {
        this.files.push(input.files[i]);
      }
    }
  }
  
  removeFile(file: File): void {
    const index = this.files.indexOf(file);
    
    if (index >= 0) {
      this.files.splice(index, 1);
    }
  }
  
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
  }
  
  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    
    if (event.dataTransfer?.files) {
      for (let i = 0; i < event.dataTransfer.files.length; i++) {
        if (this.files.length < 50) { // Limit to 50 files
          this.files.push(event.dataTransfer.files[i]);
        } else {
          this.showMessage('Maximum 50 files allowed');
          break;
        }
      }
    }
  }
  
  // Google Drive integration
  openDrivePicker(): void {
    this.subs.add(
      this.driveService.createPicker().subscribe(
        (selectedFiles: any[]) => {
          if (selectedFiles && selectedFiles.length > 0) {
            // Transform Drive picker response to our DriveFile interface
            const newDriveFiles: DriveFile[] = selectedFiles.map((file: any) => ({
              id: file.id,
              name: file.name,
              mimeType: file.mimeType,
              webViewLink: file.url || `https://drive.google.com/file/d/${file.id}/view`,
              thumbnailLink: file.iconUrl || 'assets/icons/file-generic.png'
            }));
            
            this.driveFiles = [...this.driveFiles, ...newDriveFiles];
            this.showMessage(`${newDriveFiles.length} files selected from Google Drive`);
          }
        },
        (error: any) => {
          console.error('Error opening Google Drive picker:', error);
          this.showMessage('Could not open Google Drive picker');
        }
      )
    );
  }
  
  removeDriveFile(file: DriveFile): void {
    const index = this.driveFiles.findIndex(f => f.id === file.id);
    
    if (index >= 0) {
      this.driveFiles.splice(index, 1);
    }
  }
  
  // Helper to show messages
  private showMessage(message: string): void {
    this.notificationService.showMessage(message);
  }
  
  // Form submission
  hasAnyFiles(): boolean {
    return this.files.length > 0 || this.driveFiles.length > 0;
  }
  
  hasAnyLinks(): boolean {
    const form = this.uploadForm.value;
    return !!(form.slide_url || form.video_url || form.resources_url);
  }
  
  onSubmit(): void {
    if (this.uploadForm.invalid) {
      this.notificationService.showError('Please fill out all required fields');
      return;
    }
    
    if (!this.hasAnyFiles() && !this.hasAnyLinks()) {
      this.notificationService.showError('Please upload at least one file or provide a link');
      return;
    }
    
    this.uploading = true;
    
    // Clear any previous AI-generated content
    this.aiGeneratedContent = null;
    this.showAiContent = false;
    
    // Prepare form data
    const formValue = this.uploadForm.value;
    const metadata: Record<string, any> = {
      title: formValue.title,
      description: formValue.description,
      track: formValue.track,
      session_type: formValue.session_type,
      session_date: formValue.session_date,
      learning_level: formValue.learning_level,
      topic: formValue.topic,
      job_role: formValue.job_role,
      area_of_interest: formValue.area_of_interest,
      industry: formValue.industry,
      tags: this.tags,
      slide_url: formValue.slide_url,
      video_url: formValue.video_url,
      resources_url: formValue.resources_url,
      ai_summarize: formValue.ai_summarize,
      ai_tags: formValue.ai_tags,
      ai_index: formValue.ai_index
    };
    
    // Decide whether to use local files, Drive files, or both
    let uploadObservable: Observable<any> = of({ success: false, error: 'No upload method selected' });
    
    if (this.files.length > 0 && this.driveFiles.length > 0) {
      // Handle both local files and Drive files
      // First handle local file upload with the updated service
      if (this.files.length > 0) {
        const formData = new FormData();
        
        // Append files
        this.files.forEach(file => {
          formData.append('files', file);
        });
        
        // Append metadata
        Object.keys(metadata).forEach(key => {
          if (metadata[key] !== null && metadata[key] !== undefined) {
            if (Array.isArray(metadata[key])) {
              formData.append(key, JSON.stringify(metadata[key]));
            } else {
              formData.append(key, String(metadata[key]));
            }
          }
        });
        
        uploadObservable = this.contentService.uploadContent(formData).pipe(
          switchMap((result: any) => {
            if (result.type === 'progress') {
              this.progress = result.progress;
              return of(null);
            } else if (result.type === 'complete' && result.body && result.body.success && result.body.contentId) {
              // If local files uploaded successfully, also upload Drive files
              this.notificationService.showSuccess('Files uploaded successfully');
              
              if (this.driveFiles.length > 0) {
                return this.uploadService.uploadDriveFiles(
                  this.driveFiles.map(f => f.id),
                  { ...metadata, contentId: result.body.contentId }
                ).pipe(
                  map(driveResult => {
                    // Combine the results
                    return {
                      ...result.body,
                      driveFilesUploaded: driveResult.success
                    };
                  })
                );
              }
              return of(result.body);
            }
            return of(null);
          }),
          catchError(error => {
            console.error('Error in upload pipeline:', error);
            this.notificationService.showError(`Upload failed: ${error.message || 'Unknown error'}`);
            return of({ success: false, error: error.message });
          })
        );
      }
    } else if (this.files.length > 0) {
      // Only local files - use the improved content service
      const formData = new FormData();
      
      // Append files
      this.files.forEach(file => {
        formData.append('files', file);
      });
      
      // Append metadata
      Object.keys(metadata).forEach(key => {
        if (metadata[key] !== null && metadata[key] !== undefined) {
          if (Array.isArray(metadata[key])) {
            formData.append(key, JSON.stringify(metadata[key]));
          } else {
            formData.append(key, String(metadata[key]));
          }
        }
      });
      
      uploadObservable = this.contentService.uploadContent(formData);
    } else if (this.driveFiles.length > 0) {
      // Only Drive files
      uploadObservable = this.uploadService.uploadDriveFiles(
        this.driveFiles.map(f => f.id),
        metadata
      );
    } else {
      // Only links, no files
      uploadObservable = this.contentService.createContentWithoutFiles(metadata);
    }
    
    this.subs.add(
      uploadObservable.subscribe(
        (result: any) => {
          // Check if this is a progress event
          if (result && result.type === 'progress') {
            this.progress = result.progress;
            return;  // Don't complete the upload on progress events
          }
          
          // Get the final result
          const finalResult = result && result.type === 'complete' ? result.body : result;
          
          // Skip null results (from progress events)
          if (finalResult === null) {
            return;
          }
          
          this.uploading = false;
          this.progress = 0;
          
          if (finalResult && finalResult.success) {
            this.notificationService.showSuccess('Content uploaded successfully!');
            
            if (finalResult.contentId) {
              // Check if AI content was generated
              if ((formValue.ai_summarize || formValue.ai_tags) && finalResult.aiContent) {
                this.aiGeneratedContent = {
                  summary: finalResult.aiContent.summary || 'No summary available',
                  tags: finalResult.aiContent.tags || []
                };
                this.showAiContent = true;
                
                // Show toast messages for AI-generated content
                if (formValue.ai_summarize && finalResult.aiContent.summary) {
                  this.notificationService.showSuccess('AI summary generated successfully');
                }
                
                if (formValue.ai_tags && finalResult.aiContent.tags && finalResult.aiContent.tags.length > 0) {
                  this.notificationService.showSuccess(`${finalResult.aiContent.tags.length} AI tags generated`);
                }
                
                // Store the contentId for later navigation
                this.uploadForm.patchValue({ contentId: finalResult.contentId });
              } else {
                // Navigate to content view page if no AI content to display
                this.router.navigate(['/content', finalResult.contentId]);
              }
            } else {
              this.router.navigate(['/search']);
            }
          } else {
            this.notificationService.showError(`Upload failed: ${finalResult && finalResult.error ? finalResult.error : 'Unknown error'}`);
          }
        },
        (error: any) => {
          this.uploading = false;
          this.progress = 0;
          console.error('Upload error:', error);
          this.notificationService.showError(`Upload failed: ${error.message || 'Unknown error'}`);
        }
      )
    );
  }

  // Add a method to navigate to search page
  goToSearch(): void {
    this.router.navigate(['/search']);
  }

  // Add a method to manually handle upload cancellation
  cancelUpload(): void {
    // Implement cancellation logic here if needed
    this.uploading = false;
    this.progress = 0;
    this.notificationService.showMessage('Upload cancelled');
  }
} 