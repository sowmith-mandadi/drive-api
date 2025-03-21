import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

/**
 * Header component responsible for navigation and displaying authentication status
 */
@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {
  /**
   * Creates an instance of HeaderComponent
   * @param router - Angular router service for navigation
   * @param authService - Service handling authentication operations
   */
  constructor(
    private readonly router: Router,
    public readonly authService: AuthService
  ) {}

  /**
   * Navigates to a specified route
   * @param route - The route path to navigate to
   */
  public navigateTo(route: string): void {
    this.router.navigate([route]);
  }

  /**
   * Logs out the current user and redirects to home page
   */
  public logout(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }
} 