import { Routes } from '@angular/router';
import { ContentFormComponent } from './features/content-management/components/content/content-form.component';
import { ConferenceSchemaComponent } from './features/content-management/components/schema/conference-schema.component';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'home',
    pathMatch: 'full'
  },
  {
    path: 'home',
    loadComponent: () => import('./features/home/home.component').then(m => m.HomeComponent)
  },
  {
    path: 'search',
    loadComponent: () => import('./features/search/search.component').then(m => m.SearchComponent)
  },
  {
    path: 'content-management',
    children: [
      {
        path: '',
        redirectTo: 'contents',
        pathMatch: 'full'
      },
      {
        path: 'contents',
        component: ContentFormComponent
      },
      {
        path: 'content/new',
        component: ContentFormComponent
      },
      {
        path: 'content/:contentId',
        component: ContentFormComponent
      },
      {
        path: 'schemas',
        component: ConferenceSchemaComponent
      },
      {
        path: 'schema/new',
        component: ConferenceSchemaComponent
      },
      {
        path: 'schema/:conferenceId',
        component: ConferenceSchemaComponent
      },
      {
        path: 'review',
        component: ContentFormComponent
      }
    ]
  },
  {
    path: 'ai-features',
    component: ContentFormComponent
  },
  {
    path: 'analytics',
    component: ContentFormComponent
  },
  {
    path: 'settings',
    component: ContentFormComponent
  },
  {
    path: '**',
    redirectTo: 'home'
  }
];
