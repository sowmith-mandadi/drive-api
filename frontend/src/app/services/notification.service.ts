import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  constructor(private snackBar: MatSnackBar) {}

  // Show a notification message
  showMessage(message: string, action: string = 'Close', duration: number = 3000): void {
    this.snackBar.open(message, action, {
      duration: duration
    });
  }

  // Show error notification
  showError(message: string, action: string = 'Close', duration: number = 5000): void {
    this.snackBar.open(message, action, {
      duration: duration,
      panelClass: ['error-notification']
    });
  }

  // Show success notification
  showSuccess(message: string, action: string = 'Close', duration: number = 3000): void {
    this.snackBar.open(message, action, {
      duration: duration,
      panelClass: ['success-notification']
    });
  }
} 