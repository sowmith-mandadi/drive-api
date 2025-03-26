import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { DriveService } from '../../services/drive.service';

@Component({
  selector: 'app-drive-callback',
  template: `
    <div class="callback-container">
      <mat-spinner></mat-spinner>
      <p>Processing Google Drive authorization...</p>
    </div>
  `,
  styles: [`
    .callback-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      gap: 1rem;
    }
    p {
      color: rgba(0, 0, 0, 0.6);
    }
  `]
})
export class DriveCallbackComponent implements OnInit {
  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private driveService: DriveService
  ) {}

  ngOnInit() {
    // Get the authorization code from the URL
    const code = this.route.snapshot.queryParamMap.get('code');
    if (code) {
      // Handle the authorization code
      this.driveService.handleAuthCode(code).subscribe(
        () => {
          // Redirect back to the upload page or wherever the user came from
          this.router.navigate(['/upload']);
        },
        error => {
          console.error('Error handling auth code:', error);
          this.router.navigate(['/upload'], { 
            queryParams: { 
              error: 'Failed to authorize Google Drive access'
            }
          });
        }
      );
    } else {
      // No code found, redirect back with error
      this.router.navigate(['/upload'], { 
        queryParams: { 
          error: 'No authorization code received'
        }
      });
    }
  }
} 