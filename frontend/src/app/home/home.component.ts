import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.component.html'
})
export class HomeComponent {
  events = [
    { title: 'Soirée DJ', date: '15 Feb 2026', location: 'Paris' },
    { title: 'Concert Live', date: '20 Feb 2026', location: 'Lyon' },
    { title: 'Festival d\'été', date: '1 Mar 2026', location: 'Marseille' }
  ];
}
