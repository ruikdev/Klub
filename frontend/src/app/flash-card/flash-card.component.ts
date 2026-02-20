import { Component } from '@angular/core';
import { ApiService } from '../api.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface Carte {
  question: string;
  reponse: string;
  flipped?: boolean;
}

interface Deck {
  nom: string;
  fichier: string;
  cartes: Carte[];
}

@Component({
  selector: 'app-flash-card',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './flash-card.component.html',
  styleUrls: ['./flash-card.component.css']
})
export class FlashCardComponent {
  flashCards: { [matiere: string]: Deck[] } = {};
  matieres: string[] = [];
  selectedMatiere: string | null = null;
  showCard = true;
  showAddCard = false;

  // Formulaire ajout
  newMatiere = '';
  newNom = '';
  newCartes: { question: string; reponse: string }[] = [{ question: '', reponse: '' }];
  successMessage = '';
  errorMessage = '';

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadFlashCards();
  }

  loadFlashCards() {
    this.apiService.getFlashCards().subscribe((response) => {
      this.flashCards = response.flashCards;
      this.matieres = Object.keys(response.flashCards);
    });
  }

  selectMatiere(matiere: string) {
    this.showCard = true;
    this.showAddCard = false;
    this.selectedMatiere = this.selectedMatiere === matiere ? null : matiere;
  }

  get decksActuels(): Deck[] {
    if (!this.selectedMatiere) return [];
    return this.flashCards[this.selectedMatiere] ?? [];
  }

  createFlashCard() {
    this.selectedMatiere = null;
    this.showAddCard = true;
    this.showCard = false;
    this.successMessage = '';
    this.errorMessage = '';
  }

  addCarte() {
    this.newCartes.push({ question: '', reponse: '' });
  }

  removeCarte(index: number) {
    if (this.newCartes.length > 1) {
      this.newCartes.splice(index, 1);
    }
  }

  submitFlashCard() {
    const cartesValides = this.newCartes.filter(c => c.question.trim() && c.reponse.trim());
    if (!this.newMatiere.trim() || !this.newNom.trim() || cartesValides.length === 0) {
      this.errorMessage = 'Matière, nom et au moins une carte sont requis.';
      return;
    }
    this.apiService.addFlashCard(this.newMatiere.trim(), this.newNom.trim(), cartesValides).subscribe({
      next: () => {
        this.successMessage = 'Flash-card ajoutée avec succès !';
        this.errorMessage = '';
        this.newMatiere = '';
        this.newNom = '';
        this.newCartes = [{ question: '', reponse: '' }];
        this.loadFlashCards();
      },
      error: (err) => {
        this.errorMessage = err.error?.error ?? "Erreur lors de l'ajout.";
      }
    });
  }

  cancelAdd() {
    this.showAddCard = false;
    this.showCard = true;
    this.successMessage = '';
    this.errorMessage = '';
    this.newCartes = [{ question: '', reponse: '' }];
  }
}
