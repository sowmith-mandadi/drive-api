import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatTabsModule } from '@angular/material/tabs';
import { COMMA, ENTER } from '@angular/cdk/keycodes';

import { Content, Presenter } from '../../models/conference.model';
import { ConferenceContentService } from '../../services/conference-content.service';

@Component({
  selector: 'app-content-form',
  templateUrl: './content-form.component.html',
  styleUrls: ['./content-form.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    MatDialogModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatChipsModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatProgressSpinnerModule,
    MatDividerModule,
    MatExpansionModule,
    MatAutocompleteModule,
    MatTabsModule
  ]
})
export class ContentFormComponent implements OnInit {
  contentForm!: FormGroup;
  isEditMode = false;
  contentId: string | null = null;
  loading = false;
  error: string | null = null;
  separatorKeysCodes: number[] = [ENTER, COMMA];

  sessionTypes = [
    'Keynote',
    'Session',
    'Workshop',
    'Panel',
    'Breakout',
    'Lightning Talk',
    'Demo'
  ];

  tracks = [
    'Application Development',
    'Cloud Infrastructure',
    'Data Analytics',
    'AI & Machine Learning',
    'Security',
    'Modernization',
    'Productivity & Collaboration',
    'Networking'
  ];

  learningLevels = [
    'Beginner',
    'Intermediate',
    'Advanced',
    'Expert'
  ];

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private contentService: ConferenceContentService,
    private dialog: MatDialog
  ) { }

  ngOnInit(): void {
    this.initializeForm();

    this.route.paramMap.subscribe(params => {
      this.contentId = params.get('contentId');

      if (this.contentId) {
        this.isEditMode = true;
        this.loadExistingContent();
      }
    });
  }

  private initializeForm(): void {
    this.contentForm = this.fb.group({
      title: ['', [Validators.required]],
      description: ['', [Validators.required]],
      track: ['', [Validators.required]],
      tags: [[]],
      sessionType: ['', [Validators.required]],
      sessionDate: [null],
      learningLevel: [''],
      topic: [''],
      jobRole: [''],
      areaOfInterest: [''],
      industry: [''],
      presenters: this.fb.array([this.createPresenterFormGroup()]),
      fileUrls: [[]],
      driveUrls: [[]],
      aiSummary: [''],
      aiTags: [[]]
    });
  }

  private createPresenterFormGroup(presenter?: Presenter): FormGroup {
    return this.fb.group({
      id: [presenter?.id || null],
      name: [presenter?.name || '', [Validators.required]],
      company: [presenter?.company || '', [Validators.required]],
      title: [presenter?.title || ''],
      bio: [presenter?.bio || ''],
      photoUrl: [presenter?.photoUrl || ''],
      email: [presenter?.email || '', [Validators.email]]
    });
  }

  get presentersArray(): FormArray {
    return this.contentForm.get('presenters') as FormArray;
  }

  getPresenterAsFormGroup(index: number): FormGroup {
    return this.presentersArray.at(index) as FormGroup;
  }

  addPresenter(): void {
    this.presentersArray.push(this.createPresenterFormGroup());
  }

  removePresenter(index: number): void {
    this.presentersArray.removeAt(index);
  }

  private loadExistingContent(): void {
    this.loading = true;

    // In a real application, this would fetch from a real endpoint
    // For this demo, we'll simulate a delay and populate with dummy data
    setTimeout(() => {
      const dummyContent: Content = {
        id: 'content-123',
        title: 'Building High-Performance Cloud Applications',
        description: 'Learn how to optimize your applications for the cloud environment',
        track: 'Cloud Infrastructure',
        tags: ['performance', 'optimization', 'cloud-native'],
        sessionType: 'Session',
        sessionDate: '2025-04-15',
        learningLevel: 'Intermediate',
        topic: 'Performance Optimization',
        jobRole: 'Developer',
        areaOfInterest: 'Application Performance',
        industry: 'Technology',
        presenters: [
          {
            id: 'presenter-1',
            name: 'Alex Johnson',
            company: 'Google',
            title: 'Cloud Architect',
            bio: 'Alex is a cloud architect with 10+ years experience',
            photoUrl: '',
            email: 'alex@example.com'
          }
        ],
        fileUrls: ['presentation.pdf', 'demo.zip'],
        driveUrls: ['https://drive.google.com/file/123'],
        aiSummary: 'This session covers cloud application performance optimization techniques',
        aiTags: ['cloud', 'performance', 'optimization']
      };

      this.populateForm(dummyContent);
      this.loading = false;
    }, 1000);
  }

  private populateForm(content: Content): void {
    this.contentForm.patchValue({
      title: content.title,
      description: content.description,
      track: content.track,
      tags: content.tags,
      sessionType: content.sessionType,
      sessionDate: content.sessionDate,
      learningLevel: content.learningLevel,
      topic: content.topic,
      jobRole: content.jobRole,
      areaOfInterest: content.areaOfInterest,
      industry: content.industry,
      fileUrls: content.fileUrls,
      driveUrls: content.driveUrls,
      aiSummary: content.aiSummary,
      aiTags: content.aiTags
    });

    // Clear existing presenters
    this.presentersArray.clear();

    // Add presenters
    content.presenters.forEach(presenter => {
      this.presentersArray.push(this.createPresenterFormGroup(presenter));
    });
  }

  saveContent(): void {
    if (this.contentForm.invalid) {
      return;
    }

    this.loading = true;

    // For this demo, we'll simulate a save operation
    setTimeout(() => {
      console.log('Content saved:', this.contentForm.value);
      this.loading = false;
      this.navigateBack();
    }, 1000);
  }

  navigateBack(): void {
    this.router.navigate(['/content-management/contents']);
  }

  addTag(event: any): void {
    const value = (event.value || '').trim();
    const currentTags = this.contentForm.get('tags')?.value || [];

    if (value && !currentTags.includes(value)) {
      currentTags.push(value);
      this.contentForm.patchValue({ tags: currentTags });
    }

    // Clear the input
    if (event.input) {
      event.input.value = '';
    }
  }

  removeTag(tag: string): void {
    const currentTags = this.contentForm.get('tags')?.value || [];
    const index = currentTags.indexOf(tag);

    if (index >= 0) {
      currentTags.splice(index, 1);
      this.contentForm.patchValue({ tags: currentTags });
    }
  }

  // For AI tags
  addAiTag(event: any): void {
    const value = (event.value || '').trim();
    const currentAiTags = this.contentForm.get('aiTags')?.value || [];

    if (value && !currentAiTags.includes(value)) {
      currentAiTags.push(value);
      this.contentForm.patchValue({ aiTags: currentAiTags });
    }

    // Clear the input
    if (event.input) {
      event.input.value = '';
    }
  }

  removeAiTag(tag: string): void {
    const currentAiTags = this.contentForm.get('aiTags')?.value || [];
    const index = currentAiTags.indexOf(tag);

    if (index >= 0) {
      currentAiTags.splice(index, 1);
      this.contentForm.patchValue({ aiTags: currentAiTags });
    }
  }

  // For file/drive URLs
  addFileUrl(event: any): void {
    const value = (event.value || '').trim();
    const currentFileUrls = this.contentForm.get('fileUrls')?.value || [];

    if (value && !currentFileUrls.includes(value)) {
      currentFileUrls.push(value);
      this.contentForm.patchValue({ fileUrls: currentFileUrls });
    }

    // Clear the input
    if (event.input) {
      event.input.value = '';
    }
  }

  removeFileUrl(url: string): void {
    const currentFileUrls = this.contentForm.get('fileUrls')?.value || [];
    const index = currentFileUrls.indexOf(url);

    if (index >= 0) {
      currentFileUrls.splice(index, 1);
      this.contentForm.patchValue({ fileUrls: currentFileUrls });
    }
  }

  addDriveUrl(event: any): void {
    const value = (event.value || '').trim();
    const currentDriveUrls = this.contentForm.get('driveUrls')?.value || [];

    if (value && !currentDriveUrls.includes(value)) {
      currentDriveUrls.push(value);
      this.contentForm.patchValue({ driveUrls: currentDriveUrls });
    }

    // Clear the input
    if (event.input) {
      event.input.value = '';
    }
  }

  removeDriveUrl(url: string): void {
    const currentDriveUrls = this.contentForm.get('driveUrls')?.value || [];
    const index = currentDriveUrls.indexOf(url);

    if (index >= 0) {
      currentDriveUrls.splice(index, 1);
      this.contentForm.patchValue({ driveUrls: currentDriveUrls });
    }
  }
}
