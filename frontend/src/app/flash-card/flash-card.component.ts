import { Component } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-flash-card',
  standalone: true,
  imports: [],
  templateUrl: './flash-card.component.html',
  styleUrl: './flash-card.component.css'
})
export class FlashCardComponent {
  flashCards: any[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getFlashCards().subscribe(
      (response) => {
        this.flashCards = response.flashCards;
      }
    )
  }
}
