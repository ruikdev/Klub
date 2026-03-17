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
  // "Course" mode: provide markdown course content
  @Input() coursMd: string = '';
  // "Homework" mode: provide homework id
  @Input() devoirId: number | null = null;

  question: string = '';
  response: string = '';
  loading: boolean = false;
  error: string | null = null;

  constructor(private apiService: ApiService) {}

  ngOnChanges(changes: SimpleChanges) {
    // Reset on each homework/course change
    this.question = '';
    this.response = '';
    this.error = null;

    // If homework mode, automatically ask for an explanation
    if (this.devoirId) {
      this.question = "Can you explain this homework?";
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
        this.error = err.error?.error || "Error while talking to AI";
        this.loading = false;
      }
    });
  }
}
