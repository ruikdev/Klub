import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DevoirsComponent } from './devoirs/devoirs.component';
import { NotesComponent } from './notes/notes.component';
import { CoursComponent } from './cours/cours.component';
import { OcrComponent } from './ocr/ocr.component';
import { ChatGlobalComponent } from './chat-global/chat-global.component';
import { FlashCardComponent } from './flash-card/flash-card.component';
import { AuthComponent } from './auth/auth.component';
import { ApiService } from './api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, DevoirsComponent, NotesComponent, CoursComponent, OcrComponent, ChatGlobalComponent, FlashCardComponent, AuthComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  isMenuOpen = false;
  isAuthenticated = false;
  currentPage = 'devoirs';

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.checkSession().subscribe({
      next: () => this.isAuthenticated = true,
      error: () => this.isAuthenticated = false
    });
  }

  onLoginSuccess() {
    this.isAuthenticated = true;
  }

  toggleMenu() {
    this.isMenuOpen = !this.isMenuOpen;
  }

  togglePage(page: string) {
    this.currentPage = page.toLowerCase();
  }
}
