import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';
import { MarkdownPipe } from '../pipes/markdown.pipe';

@Component({
  selector: 'app-chat-cours',
  standalone: true,
  imports: [CommonModule, FormsModule, MarkdownPipe],
  templateUrl: './chat-cours.component.html',
  styleUrl: './chat-cours.component.css'
})
export class ChatCoursComponent {
  @Input() coursMd: string = '';

  question: string = '';
  response: string = '';
  loading: boolean = false;
  error: string | null = null;

  constructor(private apiService: ApiService) {}

  sendMessage() {
    if (!this.question.trim() || !this.coursMd) return;

    this.loading = true;
    this.error = null;
    this.response = '';

    this.apiService.sendChatMessageCours(this.question, this.coursMd).subscribe({
      next: (data) => {
        this.response = data.response;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.error || 'Erreur lors de la communication avec l\'IA';
        this.loading = false;
      }
    });
  }
}
