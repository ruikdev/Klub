import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';
import { CommonModule } from '@angular/common';
import { ChatComponent } from '../chat/chat.component';

@Component({
  selector: 'app-devoirs',
  standalone: true,
  imports: [CommonModule, ChatComponent],
  templateUrl: './devoirs.component.html',
  styleUrl: './devoirs.component.css'
})
export class DevoirsComponent implements OnInit {
  devoirs: any = null;
  devoirsList: Array<{date: string, devoirs: any[], details: any}> = [];
  loading: boolean = true;
  error: string | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getDevoirs().subscribe({
      next: (data) => {
        this.devoirs = data;
        this.devoirsList = this.formatDevoirs(data);
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Erreur lors du chargement des devoirs';
        this.loading = false;
        console.error(err);
      }
    });
  }

  formatDevoirs(data: any): Array<{date: string, devoirs: any[], details: any}> {
    if (!data) return [];
    return Object.keys(data).map(date => ({
      date: date,
      devoirs: data[date].devoirs || data[date],
      details: data[date].details || null
    }));
  }
}
