import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'home',
    pathMatch: 'full'
  },
  {
    path: 'home',
    loadComponent: () => import('./features/home/home.component').then(c => c.HomeComponent)
  },
  {
    path: 'content-management',
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./features/content-management/components/dashboard/conference-dashboard.component').then(c => c.ConferenceDashboardComponent)
      },
      {
        path: 'conferences',
        loadComponent: () => import('./features/content-management/components/dashboard/conference-list.component').then(c => c.ConferenceListComponent)
      },
      {
        path: 'conferences/create',
        loadComponent: () => import('./features/content-management/components/schema/conference-schema.component').then(c => c.ConferenceSchemaComponent)
      },
      {
        path: 'conferences/:conferenceId',
        loadComponent: () => import('./features/content-management/components/dashboard/conference-dashboard.component').then(c => c.ConferenceDashboardComponent)
      },
      {
        path: 'conferences/:conferenceId/edit',
        loadComponent: () => import('./features/content-management/components/schema/conference-schema.component').then(c => c.ConferenceSchemaComponent)
      },
      {
        path: 'conferences/:conferenceId/create',
        loadComponent: () => import('./features/content-management/components/edit-content/content-editor.component').then(c => c.ContentEditorComponent)
      },
      {
        path: 'conferences/:conferenceId/content/:contentId',
        loadComponent: () => import('./features/content-management/components/edit-content/content-editor.component').then(c => c.ContentEditorComponent)
      },
      {
        path: 'upload',
        loadComponent: () => import('./features/content-management/components/single-upload/single-upload.component').then(c => c.SingleUploadComponent)
      },
      {
        path: 'bulk-upload',
        loadComponent: () => import('./features/content-management/components/bulk-upload/bulk-upload.component').then(c => c.BulkUploadComponent)
      }
    ]
  },
  {
    path: 'content-library',
    loadComponent: () => import('./features/content-library/content-library.component').then(c => c.ContentLibraryComponent)
  },
  {
    path: 'search',
    loadComponent: () => import('./features/search/search.component').then(c => c.SearchComponent)
  },
  {
    path: 'ai-features',
    loadComponent: () => import('./features/ai-features/ai-features.component').then(c => c.AIFeaturesComponent)
  },
  {
    path: '**',
    redirectTo: 'home'
  }
];
