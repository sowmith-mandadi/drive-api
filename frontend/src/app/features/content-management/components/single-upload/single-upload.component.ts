import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-single-upload',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="upload-container">
      <h1>Upload Content</h1>
      <p>Upload a single content item</p>
    </div>
  `,
  styles: [`
    .upload-container {
      padding: 2rem;
      text-align: center;
    }
  `]
})
export class SingleUploadComponent {} 