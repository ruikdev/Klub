import { Component, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';
import { MarkdownPipe } from '../pipes/markdown.pipe';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  loading?: boolean;
}

@Component({
  selector: 'app-chat-global',
  standalone: true,
  imports: [CommonModule, FormsModule, MarkdownPipe],
  templateUrl: './chat-global.component.html',
  styleUrl: './chat-global.component.css'
})
export class ChatGlobalComponent implements AfterViewChecked {

  @ViewChild('messagesContainer') messagesContainer!: ElementRef;

  messages: ChatMessage[] = [];
  userInput = '';
  isLoading = false;
  private shouldScrollToBottom = false;

  constructor(private api: ApiService) {}

  ngAfterViewChecked(): void {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  private scrollToBottom(): void {
    try {
      const el = this.messagesContainer.nativeElement;
      el.scrollTop = el.scrollHeight;
    } catch {}
  }

  sendMessage(): void {
    const question = this.userInput.trim();
    if (!question || this.isLoading) return;

    // Ajouter le message utilisateur
    this.messages.push({ role: 'user', content: question });
    this.userInput = '';
    this.isLoading = true;
    this.shouldScrollToBottom = true;

    // Ajouter un message de chargement
    const loadingMsg: ChatMessage = { role: 'assistant', content: '', loading: true };
    this.messages.push(loadingMsg);
    this.shouldScrollToBottom = true;

    // Construire l'historique (user + assistant uniquement, sans le loading courant)
    const history = this.messages
      .filter(m => !m.loading && m.content)
      .slice(0, -1) // exclure la question courante
      .map(m => ({ role: m.role, content: m.content }));

    this.api.sendChatGlobal(question, history).subscribe({
      next: (res: any) => {
        const idx = this.messages.indexOf(loadingMsg);
        if (idx !== -1) {
          this.messages[idx] = {
            role: 'assistant',
            content: res.response || '',
            loading: false
          };
        }
        this.isLoading = false;
        this.shouldScrollToBottom = true;
      },
      error: (err: any) => {
        const idx = this.messages.indexOf(loadingMsg);
        const errorMsg = err?.error?.error || 'Une erreur est survenue. Réessaie.';
        if (idx !== -1) {
          this.messages[idx] = {
            role: 'assistant',
            content: `⚠️ ${errorMsg}`,
            loading: false
          };
        }
        this.isLoading = false;
        this.shouldScrollToBottom = true;
      }
    });
  }

  onKeyDown(event: KeyboardEvent): void {
    if (event.ctrlKey && event.key === 'Enter') {
      event.preventDefault();
      this.sendMessage();
    }
  }

  clearConversation(): void {
    this.messages = [];
  }
}
