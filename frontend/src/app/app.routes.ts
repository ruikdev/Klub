import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { EventsComponent } from './events/events.component';
import { DiscoverComponent } from './discover/discover.component';
import { ProfileComponent } from './profile/profile.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'events', component: EventsComponent },
  { path: 'discover', component: DiscoverComponent },
  { path: 'profile', component: ProfileComponent },
  { path: '**', redirectTo: '' }
];
