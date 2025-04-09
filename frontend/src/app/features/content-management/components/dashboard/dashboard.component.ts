import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatBadgeModule } from '@angular/material/badge';
import { RouterLink } from '@angular/router';

interface ContentItem {
  id: string;
  title: string;
  description: string;
  track: string;
  type: string;
  status: 'published' | 'draft' | 'pending-review' | 'archived';
  dateCreated: Date;
  dateModified: Date;
  author: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatTabsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatBadgeModule,
    RouterLink
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent {
  pendingReview = signal<ContentItem[]>([
    {
      id: '101',
      title: 'Introduction to Angular Signals',
      description: 'Learn about the new reactivity system in Angular',
      track: 'Web Development',
      type: 'Presentation',
      status: 'pending-review',
      dateCreated: new Date(2025, 3, 1),
      dateModified: new Date(2025, 3, 2),
      author: 'Jane Smith'
    },
    {
      id: '102',
      title: 'Building AI Features in Web Apps',
      description: 'How to integrate AI capabilities in modern web applications',
      track: 'Artificial Intelligence',
      type: 'Workshop',
      status: 'pending-review',
      dateCreated: new Date(2025, 3, 2),
      dateModified: new Date(2025, 3, 3),
      author: 'John Doe'
    }
  ]);

  drafts = signal<ContentItem[]>([
    {
      id: '103',
      title: 'Advanced React Patterns',
      description: 'In-depth analysis of React design patterns',
      track: 'Web Development',
      type: 'Technical Session',
      status: 'draft',
      dateCreated: new Date(2025, 3, 3),
      dateModified: new Date(2025, 3, 4),
      author: 'Sarah Johnson'
    }
  ]);

  published = signal<ContentItem[]>([
    {
      id: '104',
      title: 'Cloud-Native Infrastructure',
      description: 'Building scalable infrastructure for modern applications',
      track: 'Cloud Computing',
      type: 'Technical Session',
      status: 'published',
      dateCreated: new Date(2025, 3, 4),
      dateModified: new Date(2025, 3, 5),
      author: 'Michael Brown'
    },
    {
      id: '105',
      title: 'Mobile Development with Flutter',
      description: 'Creating cross-platform mobile applications',
      track: 'Mobile Development',
      type: 'Workshop',
      status: 'published',
      dateCreated: new Date(2025, 3, 5),
      dateModified: new Date(2025, 3, 6),
      author: 'Emily Wilson'
    }
  ]);

  archived = signal<ContentItem[]>([
    {
      id: '106',
      title: 'Legacy JavaScript Frameworks',
      description: 'A look at older JavaScript frameworks and their impact',
      track: 'Web Development',
      type: 'Presentation',
      status: 'archived',
      dateCreated: new Date(2025, 2, 5),
      dateModified: new Date(2025, 2, 6),
      author: 'David Lee'
    }
  ]);

  getStatusClass(status: string): string {
    switch(status) {
      case 'published': return 'status-published';
      case 'draft': return 'status-draft';
      case 'pending-review': return 'status-pending';
      case 'archived': return 'status-archived';
      default: return '';
    }
  }

  getStatusText(status: string): string {
    switch(status) {
      case 'published': return 'Published';
      case 'draft': return 'Draft';
      case 'pending-review': return 'Pending Review';
      case 'archived': return 'Archived';
      default: return status;
    }
  }

  getHighlightClass(track: string): string {
    switch(track) {
      case 'Web Development': return 'highlight-web';
      case 'Artificial Intelligence': return 'highlight-ai';
      case 'Cloud Computing': return 'highlight-cloud';
      case 'Mobile Development': return 'highlight-mobile';
      case 'DevOps': return 'highlight-devops';
      default: return 'highlight-web';
    }
  }
} 