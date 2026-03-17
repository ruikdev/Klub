import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
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
export class ChatCoursComponent implements OnChanges {
  // Mode "cours" : fournir le contenu markdown du cours
  @Input() coursMd: string = '';
  // Mode "devoir" : fournir l'id du devoir
  @Input() devoirId: number | null = null;

  question: string = '';
  response: string = '';
  loading: boolean = false;
  error: string | null = null;

  constructor(private apiService: ApiService) {}

  ngOnChanges(changes: SimpleChanges) {
    // Réinitialiser à chaque changement de devoir/cours
    this.question = '';
    this.response = '';
    this.error = null;

    // Si mode devoir, envoyer la question d'explication automatiquement
    if (this.devoirId) {
      this.question = "Peux-tu m'expliquer ce devoir ?";
      this.sendMessage();
    }
  }

  sendMessage() {
    if (!this.question.trim()) return;
    if (!this.coursMd && !this.devoirId) return;

    this.loading = true;
    this.error = null;
    this.response = '';

    const obs = this.devoirId
      ? this.apiService.sendChatMessage(this.question, this.devoirId)
      : this.apiService.sendChatMessageCours(this.question, this.coursMd);

    obs.subscribe({
      next: (data) => {
        this.response = data.response;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.error || "Erreur lors de la communication avec l'IA";
        this.loading = false;
      }
    });
  }
}
