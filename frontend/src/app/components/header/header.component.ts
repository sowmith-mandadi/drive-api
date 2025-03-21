import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {
  constructor(
    private router: Router,
    public authService: AuthService
  ) {}

  // Navigate to different sections
  navigateTo(route: string): void {
    this.router.navigate([route]);
  }

  // Logout user
  logout(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }
} 