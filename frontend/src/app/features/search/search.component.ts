import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="search-container">
      <h1>Search Content</h1>
      <p>Search conference content across all years</p>
    </div>
  `,
  styles: [`
    .search-container {
      padding: 2rem;
      text-align: center;
    }
  `]
})
export class SearchComponent {} 