import { Component, signal } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink } from '@angular/router';
import { MatChipsModule } from '@angular/material/chips';
import { MatTabsModule } from '@angular/material/tabs';
import { DatePipe, NgFor, NgIf } from '@angular/common';

interface Content {
  id: string;
  title: string;
  description: string;
  track: string;
  date: Date;
  type: string;
  thumbnailUrl?: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    MatCardModule, 
    MatButtonModule, 
    MatIconModule, 
    RouterLink, 
    MatChipsModule, 
    MatTabsModule,
    NgFor,
    NgIf,
    DatePipe
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {
  recentContent = signal<Content[]>([
    {
      id: '1',
      title: 'Introduction to Angular 19',
      description: 'Learn about the new features in Angular 19',
      track: 'Web Development',
      date: new Date(2025, 3, 1),
      type: 'Presentation'
    },
    {
      id: '2',
      title: 'AI-Powered Applications',
      description: 'Building intelligent applications with AI',
      track: 'Artificial Intelligence',
      date: new Date(2025, 3, 2),
      type: 'Workshop'
    },
    {
      id: '3',
      title: 'Advanced TypeScript Patterns',
      description: 'Deep dive into TypeScript design patterns',
      track: 'Web Development',
      date: new Date(2025, 3, 3),
      type: 'Technical Session'
    }
  ]);

  tracks = signal<string[]>([
    'Web Development',
    'Artificial Intelligence',
    'Cloud Computing',
    'Mobile Development',
    'DevOps'
  ]);

  contentByTrack = signal<Record<string, Content[]>>({
    'Web Development': [
      {
        id: '1',
        title: 'Introduction to Angular 19',
        description: 'Learn about the new features in Angular 19',
        track: 'Web Development',
        date: new Date(2025, 3, 1),
        type: 'Presentation'
      },
      {
        id: '3',
        title: 'Advanced TypeScript Patterns',
        description: 'Deep dive into TypeScript design patterns',
        track: 'Web Development',
        date: new Date(2025, 3, 3),
        type: 'Technical Session'
      }
    ],
    'Artificial Intelligence': [
      {
        id: '2',
        title: 'AI-Powered Applications',
        description: 'Building intelligent applications with AI',
        track: 'Artificial Intelligence',
        date: new Date(2025, 3, 2),
        type: 'Workshop'
      },
      {
        id: '4',
        title: 'Machine Learning Fundamentals',
        description: 'Introduction to machine learning concepts',
        track: 'Artificial Intelligence',
        date: new Date(2025, 3, 4),
        type: 'Workshop'
      }
    ],
    'Cloud Computing': [
      {
        id: '5',
        title: 'Cloud-Native Applications',
        description: 'Building applications for the cloud',
        track: 'Cloud Computing',
        date: new Date(2025, 3, 5),
        type: 'Technical Session'
      }
    ],
    'Mobile Development': [
      {
        id: '6',
        title: 'Flutter Development',
        description: 'Building cross-platform mobile apps with Flutter',
        track: 'Mobile Development',
        date: new Date(2025, 3, 6),
        type: 'Workshop'
      }
    ],
    'DevOps': [
      {
        id: '7',
        title: 'CI/CD Pipelines',
        description: 'Setting up continuous integration and deployment',
        track: 'DevOps',
        date: new Date(2025, 3, 7),
        type: 'Technical Session'
      }
    ]
  });
}
