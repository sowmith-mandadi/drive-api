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
import { forkJoin } from 'rxjs';
import { Track } from '../../models/content.model';
import { UploadService } from '../../services/upload.service';
import { NotificationService } from '../../services/notification.service';
import { Subscription } from 'rxjs';

interface Presenter {
  id: string;
  name: string;
  title: string;
  company: string;
  photoUrl?: string;
}

interface DriveFile {
  id: string;
  name: string;
  mimeType: string;
  webViewLink: string;
  iconLink?: string;
  thumbnailLink?: string;
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
  customPresenters: string[] = [];
  selectedPresenters: string[] = [];
  
  trackOptions: any[] = [];
  sessionTypeOptions: string[] = [];
  availablePresenters: Presenter[] = [];
  
  files: File[] = [];
  driveFiles: DriveFile[] = [];
  uploading: boolean = false;
  progress: number = 0;
  
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
    private notificationService: NotificationService
  ) { }
  
  ngOnInit(): void {
    this.initForm();
    this.loadTracks();
    this.loadSessionTypes();
    this.loadPresenters();
  }
  
  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }
  
  private initForm(): void {
    this.uploadForm = this.fb.group({
      title: ['', Validators.required],
      description: [''],
      track: [''],
      session_type: [''],
      slide_url: [''],
      video_url: [''],
      resources_url: [''],
      ai_summarize: [true],
      ai_tags: [true],
      ai_index: [false]
    });
  }
  
  private loadTracks(): void {
    // Simulated data - replace with API call
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
  
  private loadSessionTypes(): void {
    // Simulated data - replace with API call
    this.sessionTypeOptions = [
      'Presentation',
      'Workshop',
      'Panel Discussion',
      'Lightning Talk',
      'Demo',
      'Roundtable',
      'Tutorial',
      'Case Study'
    ];
  }
  
  private loadPresenters(): void {
    // Simulated data - replace with API call
    this.availablePresenters = [
      {
        id: 'p1',
        name: 'Alex Johnson',
        title: 'Senior Engineer',
        company: 'TechCorp',
        photoUrl: 'assets/images/presenters/alex.jpg'
      },
      {
        id: 'p2',
        name: 'Sarah Chen',
        title: 'Product Lead',
        company: 'InnovateTech',
        photoUrl: 'assets/images/presenters/sarah.jpg'
      },
      {
        id: 'p3',
        name: 'Michael Rodriguez',
        title: 'CTO',
        company: 'DevStack',
        photoUrl: 'assets/images/presenters/michael.jpg'
      },
      {
        id: 'p4',
        name: 'Priya Patel',
        title: 'ML Research Scientist',
        company: 'AI Solutions',
        photoUrl: 'assets/images/presenters/priya.jpg'
      },
      {
        id: 'p5',
        name: 'David Kim',
        title: 'UX Designer',
        company: 'DesignHub',
        photoUrl: 'assets/images/presenters/david.jpg'
      },
      {
        id: 'p6',
        name: 'Emma Wilson',
        title: 'DevOps Lead',
        company: 'CloudScale',
        photoUrl: 'assets/images/presenters/emma.jpg'
      }
    ];
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
  
  // Custom presenter management
  addPresenter(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();
    
    if (value) {
      this.customPresenters.push(value);
    }
    
    event.chipInput!.clear();
  }
  
  removePresenter(presenter: string): void {
    const index = this.customPresenters.indexOf(presenter);
    
    if (index >= 0) {
      this.customPresenters.splice(index, 1);
    }
  }
  
  // Presenter selection
  togglePresenter(presenter: Presenter): void {
    const index = this.selectedPresenters.indexOf(presenter.id);
    
    if (index >= 0) {
      this.selectedPresenters.splice(index, 1);
    } else {
      this.selectedPresenters.push(presenter.id);
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
    // Simulated picker - replace with actual Google Drive API integration
    console.log('Opening Google Drive picker...');
    
    // Simulate adding files from Google Drive
    setTimeout(() => {
      const mockDriveFiles: DriveFile[] = [{
        id: 'drive1',
        name: 'Conference Presentation.pptx',
        mimeType: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        webViewLink: 'https://drive.google.com/file/d/example1/view',
        thumbnailLink: 'assets/icons/ppt-icon.png'
      }, {
        id: 'drive2',
        name: 'Technical Documentation.pdf',
        mimeType: 'application/pdf',
        webViewLink: 'https://drive.google.com/file/d/example2/view',
        thumbnailLink: 'assets/icons/pdf-icon.png'
      }];
      
      this.driveFiles = [...this.driveFiles, ...mockDriveFiles];
      this.showMessage('Files selected from Google Drive');
    }, 1000);
  }
  
  removeDriveFile(file: DriveFile): void {
    const index = this.driveFiles.findIndex(f => f.id === file.id);
    
    if (index >= 0) {
      this.driveFiles.splice(index, 1);
    }
  }
  
  // Helper to show messages
  private showMessage(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000
    });
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
      this.showMessage('Please fill out all required fields');
      return;
    }
    
    if (!this.hasAnyFiles() && !this.hasAnyLinks()) {
      this.showMessage('Please upload at least one file or provide a link');
      return;
    }
    
    this.uploading = true;
    this.startProgressSimulation();
    
    // Prepare form data
    const formValue = this.uploadForm.value;
    const uploadData = {
      ...formValue,
      tags: this.tags,
      presenters: this.selectedPresenters,
      custom_presenters: this.customPresenters,
      file_count: this.files.length,
      drive_file_count: this.driveFiles.length
    };
    
    console.log('Uploading content:', uploadData);
    
    // Simulate API call
    setTimeout(() => {
      this.uploading = false;
      this.showMessage('Content uploaded successfully!');
      this.router.navigate(['/content-detail', 'new-content-id']);
    }, 3000);
  }
  
  private startProgressSimulation(): void {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.floor(Math.random() * 10) + 1;
      this.progress = Math.min(progress, 100);
      
      if (this.progress >= 100 || !this.uploading) {
        clearInterval(interval);
      }
    }, 300);
  }
} 