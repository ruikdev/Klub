import { Component } from '@angular/core';
import { ApiService } from '../api.service';
import { CommonModule } from '@angular/common';

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
  imports: [CommonModule],
  templateUrl: './flash-card.component.html',
  styleUrls: ['./flash-card.component.css']
})
export class FlashCardComponent {
  flashCards: { [matiere: string]: Deck[] } = {};
  matieres: string[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getFlashCards().subscribe(
      (response) => {
        this.flashCards = response.flashCards;
        this.matieres = Object.keys(response.flashCards);
      }
    );
  }
}
