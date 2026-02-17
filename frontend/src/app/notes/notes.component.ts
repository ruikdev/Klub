import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-notes',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notes.component.html',
  styleUrl: './notes.component.css'
})
export class NotesComponent implements OnInit {
  notes: any[] = [];
  loading = false;
  error: string | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loading = true;
    this.apiService.getNotes().subscribe({
      next: (data) => {
        console.log('Notes récupérées:', data);
        // Filtrer pour garder uniquement les notes du dernier trimestre
        const allNotes = data.notes || [];
        this.notes = this.getLastTrimesterNotes(allNotes);
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur:', err);
        this.error = 'Impossible de charger les notes';
        this.loading = false;
      }
    });
  }

  private getLastTrimesterNotes(notes: any[]): any[] {
    if (notes.length === 0) return [];
    
    // Trouver tous les codes de périodes uniques
    const periodes = [...new Set(notes.map(note => note.codePeriode))];
    
    // Trier les périodes (A001, A002, A003, etc.)
    const periodesTriees = periodes.sort().reverse();
    
    // Prendre le dernier trimestre (le plus récent)
    const dernierTrimestre = periodesTriees[0];
    
    // Filtrer les notes du dernier trimestre
    return notes.filter(note => note.codePeriode === dernierTrimestre);
  }

  getNoteValue(valeur: string): number {
    return parseFloat(valeur.replace(',', '.'));
  }


}
