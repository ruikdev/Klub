import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css'
})
export class ChatComponent implements OnInit {
  @Input() devoirId: number | null = null;
  @Output() closeChat = new EventEmitter<void>();

  question: string = '';
  response: string = '';
  loading: boolean = false;
  error: string | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    // Envoyer automatiquement une question d'explication au chargement si un devoir est sélectionné
    if (this.devoirId) {
      this.question = "Peux-tu m'expliquer ce devoir et me donner des conseils pour le réussir ?";
      this.sendMessage();
    }
  }

  sendMessage() {
    if (!this.question.trim()) {
      this.error = "Veuillez saisir une question";
      return;
    }

    this.loading = true;
    this.error = null;
    this.response = '';

    this.apiService.sendChatMessage(this.question, this.devoirId || undefined).subscribe({
      next: (data) => {
        this.response = data.response;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.error || 'Erreur lors de la communication avec l\'IA';
        this.loading = false;
        console.error(err);
      }
    });
  }

  onClose() {
    this.closeChat.emit();
  }
}
