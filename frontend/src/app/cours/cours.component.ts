import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../api.service';
import { MarkdownPipe } from '../pipes/markdown.pipe';
import { ChatCoursComponent } from '../chat-cours/chat-cours.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-cours',
  standalone: true,
  imports: [CommonModule, MarkdownPipe, ChatCoursComponent, FormsModule],
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
  modeEdition = false;
  contenuEdition = '';
  saving = false;
  saveMessage: string | null = null;
  saveError: string | null = null;

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
    this.modeEdition = false;
    this.contenuEdition = cours?.contenu || '';
    this.saveMessage = null;
    this.saveError = null;
  }

  fermerCours() {
    this.coursSelectionne = null;
    this.matiereSelectionnee = null;
    this.chatOuvert = false;
    this.modeEdition = false;
    this.contenuEdition = '';
    this.saveMessage = null;
    this.saveError = null;
  }

  toggleEdition() {
    this.modeEdition = !this.modeEdition;
    this.saveMessage = null;
    this.saveError = null;

    if (this.modeEdition && this.coursSelectionne) {
      this.contenuEdition = this.coursSelectionne.contenu || '';
    }
  }

  mettreAJourCours() {
    if (!this.coursSelectionne || !this.matiereSelectionnee || this.saving) {
      return;
    }

    this.saving = true;
    this.saveMessage = null;
    this.saveError = null;

    this.apiService.upsertCours(
      this.matiereSelectionnee,
      this.coursSelectionne.nom,
      this.contenuEdition
    ).subscribe({
      next: (response) => {
        this.coursSelectionne.contenu = this.contenuEdition;

        const list = this.cours[this.matiereSelectionnee as string] || [];
        const index = list.findIndex((item) => item.nom === this.coursSelectionne.nom);
        if (index !== -1) {
          list[index].contenu = this.contenuEdition;
        }

        this.saveMessage = response.status === 201
          ? 'Cours créé avec succès'
          : 'Cours mis à jour avec succès';
        this.modeEdition = false;
        this.saving = false;
      },
      error: (err) => {
        this.saveError = err?.error?.error || 'Erreur lors de la mise à jour du cours';
        this.saving = false;
      }
    });
  }
}
