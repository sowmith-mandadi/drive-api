import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-bulk-upload',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bulk-upload-container">
      <h1>Bulk Upload</h1>
      <p>Upload multiple content items at once</p>
    </div>
  `,
  styles: [`
    .bulk-upload-container {
      padding: 2rem;
      text-align: center;
    }
  `]
})
export class BulkUploadComponent {} 