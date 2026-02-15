import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-events',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './events.component.html'
})
export class EventsComponent {
  filters = [
    { name: 'Tous', active: true },
    { name: 'Musique', active: false },
    { name: 'Sport', active: false },
    { name: 'Culture', active: false },
    { name: 'Food', active: false }
  ];
}
