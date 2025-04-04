import { Routes } from '@angular/router';
import { HOME_ROUTES } from './features/home/home.routes';

export const routes: Routes = [
  {
    path: '',
    children: HOME_ROUTES
  },
  {
    path: '**',
    redirectTo: '',
    pathMatch: 'full'
  }
];
