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
  moyenneGenerale: string = '';

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loading = true;
    this.loadingAppreciation = true;
    this.apiService.getNotes().subscribe({
      next: (data) => {
        console.log('Grades loaded:', data);
        // Keep only grades from the latest term
        const allNotes = data.notes || [];
        this.notes = this.getLastTrimesterNotes(allNotes);
        this.groupNotesByMatiere();
        this.loading = false;

      },
      error: (err) => {
        console.error('Error:', err);
        this.error = 'Unable to load grades';
        this.loading = false;
      }
    });
    this.apiService.getCommentaires().subscribe({
      next: (data) => {
        console.log('Comments loaded:', data);
        this.appreciation = data.appreciation || 'No summary available.';
        this.loadingAppreciation = false;
      },
      error: (err) => {
        console.error('Error:', err);
        this.appreciation = 'Unable to load summary.';
        this.loadingAppreciation = false;
        // Keep grades visible even if summary fails
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

      // Calculate weighted average
      const noteValue = this.getNoteValue(note.valeur);
      const noteSur = parseFloat(note.noteSur);
      const coef = parseFloat(note.coef || '1');

      if (!isNaN(noteValue) && !isNaN(noteSur) && noteSur > 0) {
        const noteNormalisee = (noteValue / noteSur) * 20; // Normalize to 20-point scale
        matiere.totalPoints += noteNormalisee * coef;
        matiere.totalCoef += coef;
      }
    });

    // Calculate final averages
    matiereMap.forEach(matiere => {
      if (matiere.totalCoef > 0) {
        matiere.moyenne = (matiere.totalPoints / matiere.totalCoef).toFixed(2);
      }
    });

    this.matieres = Array.from(matiereMap.values());
    this.calculateMoyenneGenerale();
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

  private calculateMoyenneGenerale() {
    if (this.matieres.length === 0) {
      this.moyenneGenerale = '';
      return;
    }

    let totalPoints = 0;
    let totalCoef = 0;

    this.matieres.forEach(matiere => {
      const coef = matiere.totalCoef || 0;
      const points = matiere.totalPoints || 0;
      totalPoints += points;
      totalCoef += coef;
    });

    if (totalCoef > 0) {
      this.moyenneGenerale = (totalPoints / totalCoef).toFixed(2);
    } else {
      this.moyenneGenerale = '';
    }
  }
}
