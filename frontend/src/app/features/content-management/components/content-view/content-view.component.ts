import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { MatTableModule } from '@angular/material/table';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-content-view',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatChipsModule,
    MatDividerModule,
    MatTableModule,
    RouterLink
  ],
  template: `
    <div class="content-view-container">
      <div class="back-link">
        <button mat-icon-button routerLink="/search">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <span>Back to search results</span>
      </div>

      <div class="content-main">
        <div class="content-left">
          <div class="content-header">
            <h1>AI for Banking: Streamline core banking services and personalize customer experiences</h1>

            <div class="tags-container">
              <div class="tag recommended">Recommended</div>
              <div class="tag ai">AI</div>
              <div class="tag finance">Finance</div>
              <div class="tag banking">Banking</div>
            </div>
          </div>

          <div class="abstract">
            <h2>Abstract</h2>
            <p>
              Generative AI has the potential to transform the way we live, work, bank, and invest. In
              this session, we will share Google Cloud's perspective and specific use cases that can
              boost productivity and operational efficiency in banking. The session will also feature
              customer success stories and a discussion with banking executives at the forefront of
              using generative AI.
            </p>
          </div>

          <div class="assets-section">
            <h2>Assets</h2>
            <div class="assets-table-wrapper">
              <table class="assets-table">
                <thead>
                  <tr>
                    <th class="asset-column">Asset</th>
                    <th class="format-column">Format</th>
                    <th class="type-column">Asset Type</th>
                    <th class="actions-column"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="asset-column">AIML100 Gemini at Work Summit '24</td>
                    <td class="format-column">Keynote</td>
                    <td class="type-column">Slide</td>
                    <td class="actions-column">
                      <button mat-icon-button>
                        <mat-icon>bookmark_border</mat-icon>
                      </button>
                    </td>
                  </tr>
                  <tr>
                    <td class="asset-column">AIML100_final preview</td>
                    <td class="format-column">Animation</td>
                    <td class="type-column">MP4</td>
                    <td class="actions-column">
                      <button mat-icon-button>
                        <mat-icon>bookmark_border</mat-icon>
                      </button>
                    </td>
                  </tr>
                  <tr>
                    <td class="asset-column">AI for Banking - 2024</td>
                    <td class="format-column">eBook</td>
                    <td class="type-column">PDF</td>
                    <td class="actions-column">
                      <button mat-icon-button>
                        <mat-icon>bookmark_border</mat-icon>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="notes-comments">
              <h3>Notes/Comments</h3>
              <p>
                Any comments or notes put by the content creator that can help end users understand where the crucial points of the asset are, or any other piece of information that can be useful.
              </p>
            </div>
          </div>
        </div>

        <div class="content-right">
          <div class="info-card">
            <div class="info-card-header">
              <h3>Details</h3>
            </div>
            <div class="info-card-content">
              <div class="info-row">
                <div class="info-label">Session ID</div>
                <div class="info-value">AIML100</div>
              </div>
              <div class="info-row">
                <div class="info-label">Date of Creation</div>
                <div class="info-value">Mar 10, 2025</div>
              </div>
              <div class="info-row">
                <div class="info-label">Industry</div>
                <div class="info-value">FSI</div>
              </div>
              <div class="info-row">
                <div class="info-label">Featured Products</div>
                <div class="info-value">Looker, Vertex AI, Google Ads, Workspace</div>
              </div>
              <div class="info-row">
                <div class="info-label">POC</div>
                <div class="info-value">
                  Melanie Ratchford, Andrew Colebrook
                </div>
              </div>
            </div>
          </div>

          <div class="info-card">
            <div class="info-card-header">
              <h3>Additional Information</h3>
            </div>
            <div class="info-card-content">
              <div class="info-row">
                <div class="info-label">Beat Sheet (Yes/No)</div>
                <div class="info-value">Yes</div>
              </div>
              <div class="info-row">
                <div class="info-label">Speaker Notes (Yes/No)</div>
                <div class="info-value">Yes</div>
              </div>
              <div class="info-row">
                <div class="info-label">Language</div>
                <div class="info-value">English</div>
              </div>
              <div class="info-row">
                <div class="info-label">Origination</div>
                <div class="info-value">NorthAm</div>
              </div>
              <div class="info-row">
                <div class="info-label">Applicability</div>
                <div class="info-value">Global</div>
              </div>
            </div>
          </div>

          <div class="info-card">
            <div class="info-card-header">
              <h3>Resources/Supplementals</h3>
            </div>
            <div class="info-card-content">
              <div class="resource-link">
                <a href="#" target="_blank">
                  Keynote Visuals: GAW2024
                  <mat-icon class="external-link-icon">open_in_new</mat-icon>
                </a>
              </div>
              <div class="resource-link">
                <a href="#" target="_blank">
                  ROI of Gen AI Core Asset Kit
                  <mat-icon class="external-link-icon">open_in_new</mat-icon>
                </a>
              </div>
              <div class="resource-link">
                <a href="#" target="_blank">
                  2025 AI Trends x FSI
                  <mat-icon class="external-link-icon">open_in_new</mat-icon>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
      background-color: #f8f9fa;
      min-height: 100vh;
      font-family: 'Google Sans', 'Roboto', sans-serif;
    }

    .content-view-container {
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px;
      color: #202124;
    }

    .back-link {
      display: flex;
      align-items: center;
      margin-bottom: 24px;
      color: #5f6368;
      font-size: 14px;
    }

    .back-link button {
      margin-right: 8px;
    }

    .content-main {
      display: flex;
      gap: 32px;
    }

    .content-left {
      flex: 1;
      min-width: 0;
    }

    .content-right {
      width: 350px;
      flex-shrink: 0;
    }

    .content-header {
      margin-bottom: 32px;
    }

    h1 {
      font-size: 28px;
      font-weight: 400;
      line-height: 1.3;
      letter-spacing: -0.2px;
      margin: 0 0 24px 0;
      color: #202124;
    }

    h2 {
      font-size: 18px;
      font-weight: 500;
      margin: 0 0 16px 0;
      color: #202124;
    }

    h3 {
      font-size: 16px;
      font-weight: 500;
      margin: 0;
      color: #202124;
    }

    .tags-container {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .tag {
      display: inline-flex;
      align-items: center;
      height: 24px;
      font-size: 12px;
      padding: 0 12px;
      border-radius: 12px;
      letter-spacing: 0.2px;
      font-weight: 500;
    }

    .tag.recommended {
      background-color: #e6f4ea;
      color: #137333;
    }

    .tag.ai {
      background-color: #e8f0fe;
      color: #1a73e8;
    }

    .tag.finance, .tag.banking {
      background-color: #f1f3f4;
      color: #5f6368;
    }

    .abstract {
      margin-bottom: 32px;
    }

    .abstract p {
      font-size: 16px;
      line-height: 1.5;
      color: #5f6368;
      margin: 0;
    }

    .info-card {
      background-color: #fff;
      border-radius: 8px;
      border: 1px solid #dadce0;
      margin-bottom: 24px;
      overflow: hidden;
    }

    .info-card-header {
      padding: 16px 24px;
      border-bottom: 1px solid #dadce0;
    }

    .info-card-content {
      padding: 16px 24px;
    }

    .info-row {
      display: flex;
      margin-bottom: 16px;
    }

    .info-row:last-child {
      margin-bottom: 0;
    }

    .info-label {
      width: 50%;
      font-size: 14px;
      color: #5f6368;
    }

    .info-value {
      width: 50%;
      font-size: 14px;
      color: #202124;
      font-weight: 500;
    }

    .resource-link {
      margin-bottom: 16px;
    }

    .resource-link:last-child {
      margin-bottom: 0;
    }

    .resource-link a {
      display: flex;
      align-items: center;
      text-decoration: none;
      color: #1a73e8;
      font-size: 14px;
      font-weight: 500;
    }

    .resource-link a:hover {
      text-decoration: underline;
    }

    .external-link-icon {
      font-size: 14px;
      height: 14px;
      width: 14px;
      margin-left: 4px;
    }

    .assets-section {
      margin-bottom: 32px;
    }

    .assets-table-wrapper {
      border: 1px solid #dadce0;
      border-radius: 8px;
      overflow: hidden;
      margin-bottom: 24px;
      background-color: #fff;
    }

    .assets-table {
      width: 100%;
      border-collapse: collapse;
    }

    .assets-table th {
      text-align: left;
      padding: 16px 24px;
      font-size: 14px;
      font-weight: 500;
      color: #5f6368;
      background-color: #f8f9fa;
      border-bottom: 1px solid #dadce0;
    }

    .assets-table td {
      padding: 16px 24px;
      font-size: 14px;
      color: #202124;
      border-bottom: 1px solid #eee;
    }

    .assets-table tr:last-child td {
      border-bottom: none;
    }

    .asset-column {
      width: 40%;
    }

    .format-column, .type-column {
      width: 20%;
    }

    .actions-column {
      width: 10%;
      text-align: right;
    }

    .notes-comments {
      padding: 24px;
      background-color: #fff;
      border: 1px solid #dadce0;
      border-radius: 8px;
    }

    .notes-comments p {
      font-size: 14px;
      line-height: 1.5;
      color: #5f6368;
      margin: 0;
    }

    @media (max-width: 1024px) {
      .content-main {
        flex-direction: column;
      }

      .content-right {
        width: 100%;
      }
    }

    @media (max-width: 768px) {
      .content-view-container {
        padding: 16px;
      }

      h1 {
        font-size: 24px;
      }

      .assets-table th, .assets-table td {
        padding: 12px 16px;
      }
    }
  `]
})
export class ContentViewComponent {}
