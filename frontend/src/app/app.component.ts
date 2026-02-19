import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DevoirsComponent } from './devoirs/devoirs.component';
import { NotesComponent } from './notes/notes.component';
import { CoursComponent } from './cours/cours.component';
import { OcrComponent } from './ocr/ocr.component';
import { ChatGlobalComponent } from './chat-global/chat-global.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, DevoirsComponent, NotesComponent, CoursComponent, OcrComponent, ChatGlobalComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  isMenuOpen = false;

  toggleMenu() {
    this.isMenuOpen = !this.isMenuOpen;
  }

  currentPage = 'devoirs';

  togglePage(page: string) {
      this.currentPage = page.toLowerCase();
  }
}
