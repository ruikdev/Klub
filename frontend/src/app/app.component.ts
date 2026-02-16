import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DevoirsComponent } from './devoirs/devoirs.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, DevoirsComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  
}
