import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavComponent } from './nav/nav.component';
import { HomeComponent } from './home/home.component';
import { CoursComponent } from './cours/cours.component';
import { IaComponent } from './ia/ia.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, NavComponent, HomeComponent, CoursComponent, IaComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'klub';
  currentView: string = 'home';

  onNavigate(view: string) {
    this.currentView = view;
  }
}
