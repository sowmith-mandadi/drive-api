import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-content-library',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="content-library-container">
      <h1>Content Library</h1>
      <p>Browse the conference content library</p>
    </div>
  `,
  styles: [`
    .content-library-container {
      padding: 2rem;
      text-align: center;
    }
  `]
})
export class ContentLibraryComponent {}
