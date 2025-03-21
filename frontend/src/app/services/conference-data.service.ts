import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { Track } from '../models/content.model';

@Injectable({
  providedIn: 'root'
})
export class ConferenceDataService {
  // Since we can't directly scrape Cloud Next's website in production,
  // we're providing a manually curated list of tracks and speakers based on Google Cloud Next '25
  
  constructor(private http: HttpClient) { }
  
  /**
   * Get conference tracks based on Google Cloud Next '25
   */
  getTracks(): Observable<Track[]> {
    // In a real application, this would be fetched from an API
    return of([
      {
        id: 'ai-ml',
        name: 'AI & Machine Learning',
        description: 'Explore AI-powered innovations and the latest in machine learning technologies.'
      },
      {
        id: 'app-dev',
        name: 'Application Development',
        description: 'Discover tools and practices for building modern applications.'
      },
      {
        id: 'cloud-ops',
        name: 'Cloud Operations',
        description: 'Learn about managing and operating cloud infrastructure at scale.'
      },
      {
        id: 'data-analytics',
        name: 'Data Analytics',
        description: 'Unlock insights from your data with powerful analytics tools and techniques.'
      },
      {
        id: 'databases',
        name: 'Databases',
        description: 'Explore cloud database solutions for your enterprise needs.'
      },
      {
        id: 'infrastructure',
        name: 'Infrastructure & Security',
        description: 'Build secure, scalable infrastructure for your applications.'
      },
      {
        id: 'productivity-collab',
        name: 'Productivity & Collaboration',
        description: 'Tools and solutions to enhance team productivity and collaboration.'
      },
      {
        id: 'serverless',
        name: 'Serverless',
        description: 'Build applications without managing infrastructure using serverless technologies.'
      },
      {
        id: 'sustainability',
        name: 'Sustainability',
        description: 'Creating more sustainable solutions using cloud technologies.'
      }
    ]);
  }
  
  /**
   * Get conference speakers based on Google Cloud Next '25
   */
  getSpeakers(): Observable<any[]> {
    // In a real application, this would be fetched from an API
    return of([
      {
        id: 'thomas-kurian',
        name: 'Thomas Kurian',
        title: 'CEO, Google Cloud',
        bio: 'Thomas Kurian is CEO of Google Cloud, responsible for leading the cloud division of Google.',
        photoUrl: 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Thomas-Kurian.max-1000x1000.jpg'
      },
      {
        id: 'urs-holzle',
        name: 'Urs Hölzle',
        title: 'SVP, Technical Infrastructure, Google Cloud',
        bio: 'Urs Hölzle oversees the design and operation of the servers, networks, and data centers that power Google\'s services.',
        photoUrl: 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Urs_Hoelzle.max-1000x1000.jpg'
      },
      {
        id: 'sundar-pichai',
        name: 'Sundar Pichai',
        title: 'CEO, Google and Alphabet',
        bio: 'Sundar Pichai is the CEO of Google and its parent company Alphabet, overseeing the company\'s technological innovation and business strategy.',
        photoUrl: 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Sundar_Pichai.max-1000x1000.jpg'
      },
      {
        id: 'fiona-cicconi',
        name: 'Fiona Cicconi',
        title: 'Chief People Officer, Google',
        bio: 'Fiona Cicconi leads Google\'s People Operations team, responsible for the company\'s human resources function.',
        photoUrl: 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Fiona_Cicconi.max-1000x1000.jpg'
      },
      {
        id: 'phil-venables',
        name: 'Phil Venables',
        title: 'CISO, Google Cloud',
        bio: 'Phil Venables is the Chief Information Security Officer for Google Cloud, leading security strategy, engineering, and operations.',
        photoUrl: 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Phil_Venables.max-1000x1000.jpg'
      }
    ]);
  }
  
  /**
   * Get session types based on typical conference formats
   */
  getSessionTypes(): Observable<string[]> {
    return of([
      'Keynote',
      'Session',
      'Workshop',
      'Panel',
      'Bootcamp',
      'Certification',
      'Lightning Talk',
      'Demo',
      'Case Study'
    ]);
  }
} 