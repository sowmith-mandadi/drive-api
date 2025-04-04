import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, throwError, of } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

interface User {
  id: string;
  email: string;
  displayName: string;
  isAdmin: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  
  constructor(private http: HttpClient) {
    // Check if user is already logged in
    this.loadUserFromStorage();
  }
  
  private loadUserFromStorage(): void {
    const userData = localStorage.getItem('currentUser');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        this.currentUserSubject.next(user);
      } catch (error) {
        console.error('Error parsing user data from localStorage:', error);
        localStorage.removeItem('currentUser');
      }
    }
  }
  
  login(): void {
    // For demo purposes, we'll simulate a login
    // In a real app, this would redirect to Google OAuth
    
    // Simulate a successful login
    const demoUser: User = {
      id: 'user123',
      email: 'demo@example.com',
      displayName: 'Demo User',
      isAdmin: true
    };
    
    // Store user data
    localStorage.setItem('currentUser', JSON.stringify(demoUser));
    this.currentUserSubject.next(demoUser);
  }
  
  logout(): void {
    // Remove user data from storage
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
  }
  
  isLoggedIn(): boolean {
    return !!this.currentUserSubject.value;
  }
  
  isAdmin(): boolean {
    const user = this.currentUserSubject.value;
    return !!user && user.isAdmin;
  }
  
  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }
  
  // In a real application, we would have methods to handle OAuth flow
  // and token management. This is a simplified version for the demo.
} 