import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RouterLink } from '@angular/router';

interface SearchResult {
  id: string;
  title: string;
  description: string;
  track: string;
  type: string;
  date: Date;
  confidence: number;
  tags: string[];
}

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatIconModule,
    MatExpansionModule,
    MatDividerModule,
    MatProgressSpinnerModule,
    RouterLink
  ],
  templateUrl: './search.component.html',
  styleUrl: './search.component.scss'
})
export class SearchComponent {
  searchQuery = signal('');
  isSearching = signal(false);
  searchResults = signal<SearchResult[]>([]);
  showFilters = signal(false);
  appliedFilters = signal<string[]>([]);

  availableFilters = {
    tracks: [
      'Web Development',
      'Artificial Intelligence',
      'Cloud Computing',
      'Mobile Development',
      'DevOps'
    ],
    types: [
      'Presentation',
      'Workshop',
      'Technical Session',
      'Panel Discussion',
      'Demo'
    ],
    tags: [
      'Angular', 
      'TypeScript', 
      'React', 
      'Vue', 
      'Machine Learning', 
      'AI', 
      'Cloud',
      'AWS', 
      'Azure', 
      'GCP', 
      'Mobile', 
      'iOS', 
      'Android', 
      'Flutter'
    ]
  };

  search(): void {
    // For demo, we'll simulate a search with a timer
    this.isSearching.set(true);
    
    setTimeout(() => {
      this.searchResults.set([
        {
          id: '1',
          title: 'Introduction to Angular 19',
          description: 'Learn about the new features in Angular 19 including standalone components, the new reactivity system with signals, and built-in control flow.',
          track: 'Web Development',
          type: 'Presentation',
          date: new Date(2025, 3, 1),
          confidence: 0.95,
          tags: ['Angular', 'TypeScript', 'Web Development']
        },
        {
          id: '2',
          title: 'AI-Powered Applications',
          description: 'Building intelligent applications with AI. Learn how to integrate machine learning models into your web and mobile applications.',
          track: 'Artificial Intelligence',
          type: 'Workshop',
          date: new Date(2025, 3, 2),
          confidence: 0.87,
          tags: ['AI', 'Machine Learning', 'Web Development']
        },
        {
          id: '3',
          title: 'Advanced TypeScript Patterns',
          description: 'Deep dive into TypeScript design patterns that will improve your code quality and maintainability.',
          track: 'Web Development',
          type: 'Technical Session',
          date: new Date(2025, 3, 3),
          confidence: 0.82,
          tags: ['TypeScript', 'Web Development', 'Patterns']
        }
      ]);
      this.isSearching.set(false);
    }, 1000);
  }

  toggleFilters(): void {
    this.showFilters.update(value => !value);
  }

  addFilter(filter: string): void {
    if (!this.appliedFilters().includes(filter)) {
      this.appliedFilters.update(filters => [...filters, filter]);
    }
  }

  removeFilter(filter: string): void {
    this.appliedFilters.update(filters => filters.filter(f => f !== filter));
  }

  clearSearch(): void {
    this.searchQuery.set('');
    this.searchResults.set([]);
  }
} 