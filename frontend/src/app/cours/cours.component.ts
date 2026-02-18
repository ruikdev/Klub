import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../api.service';
import { MarkdownPipe } from '../pipes/markdown.pipe';
import { ChatCoursComponent } from '../chat-cours/chat-cours.component';

@Component({
  selector: 'app-cours',
  standalone: true,
  imports: [CommonModule, MarkdownPipe, ChatCoursComponent],
  templateUrl: './cours.component.html',
  styleUrls: ['./cours.component.css']
})
export class CoursComponent implements OnInit {
  // { matiere: [ { nom, fichier, contenu } ] }
  cours: { [matiere: string]: any[] } = {};
  matieres: string[] = [];
  loading = false;
  error: string | null = null;

  coursSelectionne: any | null = null;
  matiereSelectionnee: string | null = null;
  chatOuvert = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loading = true;
    this.apiService.getCours().subscribe({
      next: (data) => {
        this.cours = data.cours || {};
        this.matieres = Object.keys(this.cours);
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur:', err);
        this.error = 'Impossible de charger les cours';
        this.loading = false;
      }
    });
  }

  ouvrirCours(matiere: string, cours: any) {
    this.matiereSelectionnee = matiere;
    this.coursSelectionne = cours;
    this.chatOuvert = false;
  }

  fermerCours() {
    this.coursSelectionne = null;
    this.matiereSelectionnee = null;
    this.chatOuvert = false;
  }
}
