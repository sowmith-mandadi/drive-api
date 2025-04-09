import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-ai-features',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="ai-features-container">
      <h1>AI Features</h1>
      <p>Explore AI-powered features for conference content</p>
    </div>
  `,
  styles: [`
    .ai-features-container {
      padding: 2rem;
      text-align: center;
    }
  `]
})
export class AIFeaturesComponent {} 