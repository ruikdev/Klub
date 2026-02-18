import { Component } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-cours',
  standalone: true,
  imports: [],
  templateUrl: './cours.component.html',
  styleUrls: ['./cours.component.css']
})
export class CoursComponent {
  cours: any[] = [];
  loading = false;  
  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loading = true;
    this.apiService.getCours().subscribe({
      next: (data) => {
        this.cours = data.cours || [];
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur:', err);
        this.loading = false;
      }
    });
  }
}
