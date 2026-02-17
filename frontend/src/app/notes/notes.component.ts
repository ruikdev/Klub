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
  matieres: any[] = [];
  commentaires_brut: any[] = [];
  appreciation: string = '';
  loadingAppreciation = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loading = true;
    this.loadingAppreciation = true;
    this.apiService.getNotes().subscribe({
      next: (data) => {
        console.log('Notes récupérées:', data);
        // Filtrer pour garder uniquement les notes du dernier trimestre
        const allNotes = data.notes || [];
        this.notes = this.getLastTrimesterNotes(allNotes);
        this.groupNotesByMatiere();
        this.loading = false;

      },
      error: (err) => {
        console.error('Erreur:', err);
        this.error = 'Impossible de charger les notes';
        this.loading = false;
      }
    });
    this.apiService.getCommentaires().subscribe({
      next: (data) => {
        console.log('Commentaires récupérés:', data);
        this.appreciation = data.appreciation || 'Aucune appréciation disponible.';
        this.loadingAppreciation = false;
      },
      error: (err) => {
        console.error('Erreur:', err);
        this.appreciation = 'Impossible de charger l\'appréciation.';
        this.loadingAppreciation = false;
      }
    })
  }

  private groupNotesByMatiere() {
    const matiereMap = new Map<string, any>();

    this.notes.forEach(note => {
      const key = note.codeMatiere;
      if (!matiereMap.has(key)) {
        matiereMap.set(key, {
          codeMatiere: note.codeMatiere,
          libelleMatiere: note.libelleMatiere,
          notes: [],
          moyenne: 0,
          totalPoints: 0,
          totalCoef: 0
        });
      }

      const matiere = matiereMap.get(key);
      matiere.notes.push(note);

      // Calculer la moyenne pondérée
      const noteValue = this.getNoteValue(note.valeur);
      const noteSur = parseFloat(note.noteSur);
      const coef = parseFloat(note.coef || '1');

      if (!isNaN(noteValue) && !isNaN(noteSur) && noteSur > 0) {
        const noteNormalisee = (noteValue / noteSur) * 20; // Normaliser sur 20
        matiere.totalPoints += noteNormalisee * coef;
        matiere.totalCoef += coef;
      }
    });

    // Calculer les moyennes finales
    matiereMap.forEach(matiere => {
      if (matiere.totalCoef > 0) {
        matiere.moyenne = (matiere.totalPoints / matiere.totalCoef).toFixed(2);
      }
    });

    this.matieres = Array.from(matiereMap.values());
  }

  private getLastTrimesterNotes(notes: any[]): any[] {
    if (notes.length === 0) return [];
    
    const periodes = [...new Set(notes.map(note => note.codePeriode))];
    
    const periodesTriees = periodes.sort().reverse();
    
    const dernierTrimestre = periodesTriees[0];
    
    return notes.filter(note => note.codePeriode === dernierTrimestre);
  }

  getNoteValue(valeur: string): number {
    return parseFloat(valeur.replace(',', '.'));
  }
}
