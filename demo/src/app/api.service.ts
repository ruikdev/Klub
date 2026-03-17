import { Injectable } from '@angular/core';
import { Observable, delay, of, throwError } from 'rxjs';

interface DemoFlashCard {
  question: string;
  reponse: string;
}

interface DemoDeck {
  nom: string;
  fichier: string;
  cartes: DemoFlashCard[];
}

interface DemoCourse {
  nom: string;
  fichier: string;
  contenu: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly responseDelayMs = 250;
  private readonly sessionStorageKey = 'klub-demo-session';
  private readonly flashCardsStorageKey = 'klub-demo-flashcards';

  private sessionActive = true;

  private readonly devoirsData = this.getDefaultDevoirs();
  private readonly notesData = this.getDefaultNotes();
  private coursData = this.getDefaultCours();
  private flashCardsData = this.getDefaultFlashCards();

  constructor() {
    this.sessionActive = this.readSessionState();
    this.flashCardsData = this.readFlashCardsState();
  }

  getCommentaires(): Observable<any> {
    return this.mockResponse({
      appreciation: 'Strong and consistent term. Core concepts are well understood, especially in mathematics and physics. Keep explaining your reasoning clearly in writing and maintain this pace.'
    });
  }

  getDevoirs(): Observable<any> {
    return this.mockResponse(this.devoirsData, 350);
  }

  getNotes(): Observable<any> {
    return this.mockResponse({ notes: this.notesData }, 300);
  }

  sendChatMessage(question: string, idDevoir?: number): Observable<any> {
    const contexte = this.getDevoirContext(idDevoir);
    const matiere = contexte?.devoir?.matiere ?? 'this homework';
    const detail = contexte?.detail
      ? this.stripHtml(contexte.detail)
      : 'Read the prompt carefully, identify key concepts, and solve step by step.';

    const response = `Here’s an explanation for **${matiere}**:

${detail}

### Suggested plan
1. Rephrase the goal of the homework in your own words.
2. Do a short first attempt (5 to 10 minutes).
3. Check your result and fix mistakes.

If you want, I can also give you a simpler 3-sentence version.`;

    return this.mockResponse({ response }, 450);
  }

  sendOcrImages(images: File | File[]): Observable<any> {
    const files = Array.isArray(images) ? images : [images];
    if (!files.length) {
      return throwError(() => ({ error: { error: 'No image provided.' } }));
    }

    const matiere = this.detectMatiereFromFiles(files);
    const nomCours = `Imported course - ${new Date().toLocaleDateString('en-GB')}`;
    const fichier = `${this.slugify(nomCours)}.md`;

    const texte = `## Reconstructed course (demo)

This content was generated from **${files.length} image(s)**:

${files.map((file, index) => `- Page ${index + 1} : ${file.name}`).join('\n')}

### Summary
- Key definitions identified
- Example application
- Revision takeaways`;

    const nouveauCours: DemoCourse = {
      nom: nomCours,
      fichier,
      contenu: texte
    };

    if (!this.coursData[matiere]) {
      this.coursData[matiere] = [];
    }
    this.coursData[matiere] = [nouveauCours, ...this.coursData[matiere]];

    return this.mockResponse(
      {
        matiere,
        nom_cours: nomCours,
        fichier,
        texte
      },
      700
    );
  }


  sendChatMessageCours(question: string, cours: string): Observable<any> {
    const extrait = cours
      .replace(/[#>*`]/g, '')
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .slice(0, 3)
      .join(' ');

    const response = `Great question: **${question}**

### Key points from the course
${extrait || 'This course includes the main ideas to master before exercises.'}

### Study tip
Make a very short cheat sheet: definition, formula/rule, and one example.`;

    return this.mockResponse({ response }, 400);
  }

  getCours(): Observable<any> {
    return this.mockResponse({ cours: this.coursData }, 280);
  }

  getFlashCards(): Observable<any> {
    return this.mockResponse({ flashCards: this.flashCardsData }, 220);
  }

  addFlashCard(matiere: string, nom: string, cartes: { question: string; reponse: string }[]): Observable<any> {
    const key = matiere.trim().toLowerCase();

    if (!key || !nom.trim() || cartes.length === 0) {
      return throwError(() => ({ error: { error: 'Invalid flash-card data.' } }));
    }

    const nouveauDeck: DemoDeck = {
      nom: nom.trim(),
      fichier: `${this.slugify(nom)}.json`,
      cartes: cartes.map((carte) => ({
        question: carte.question.trim(),
        reponse: carte.reponse.trim()
      }))
    };

    const decksExistants = this.flashCardsData[key] ?? [];
    this.flashCardsData[key] = [nouveauDeck, ...decksExistants];
    this.writeFlashCardsState(this.flashCardsData);

    return this.mockResponse({ success: true }, 250);
  }

  sendChatGlobal(question: string, history: { role: string; content: string }[]): Observable<any> {
    const q = question.toLowerCase();
    let response = 'I can help with homework, grades, courses and flash cards in this demo.';

    if (q.includes('homework') || q.includes('devoir')) {
      response = `You have **${this.getTotalDevoirs()} homework items** scheduled in sample data. Open the *Homework* tab for details by date.`;
    } else if (q.includes('grade') || q.includes('note')) {
      response = 'In the demo grades, the overall average is around **14.5 / 20**. Open the *Grades* tab for subject details.';
    } else if (q.includes('course') || q.includes('cours')) {
      const matieres = Object.keys(this.coursData).slice(0, 4).join(', ');
      response = `Demo courses are available in **${matieres}**. You can open a course and ask Klub AI questions about it.`;
    } else if (q.includes('flash card') || q.includes('flashcard') || q.includes('flash')) {
      response = 'You can revise with existing decks or create new ones in the *Flash Cards* tab.';
    }

    if (history.length > 0) {
      response += '\n\n_I kept context from our previous messages._';
    }

    return this.mockResponse({ response }, 350);
  }

  login(password: string): Observable<any> {
    if (!password.trim()) {
      return throwError(() => ({ error: { error: 'Invalid code' } }));
    }

    this.sessionActive = true;
    this.writeSessionState(true);
    return this.mockResponse({ success: true }, 180);
  }

  logout(): Observable<any> {
    this.sessionActive = false;
    this.writeSessionState(false);
    return this.mockResponse({ success: true }, 120);
  }

  checkSession(): Observable<any> {
    if (this.sessionActive) {
      return this.mockResponse({ authenticated: true }, 120);
    }
    return throwError(() => ({ error: { error: 'Session expired' } }));
  }

  private mockResponse<T>(data: T, delayMs = this.responseDelayMs): Observable<T> {
    return of(this.clone(data)).pipe(delay(delayMs));
  }

  private clone<T>(value: T): T {
    if (value === null || value === undefined) {
      return value;
    }
    return JSON.parse(JSON.stringify(value)) as T;
  }

  private stripHtml(html: string): string {
    return html
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  private getTotalDevoirs(): number {
    return Object.values(this.devoirsData).reduce((total, day: any) => {
      const devoirs = day?.devoirs ?? [];
      return total + devoirs.length;
    }, 0);
  }

  private getDevoirContext(idDevoir?: number): { devoir: any; detail: string | null } | null {
    if (!idDevoir) {
      return null;
    }

    for (const jour of Object.values(this.devoirsData) as any[]) {
      const devoir = (jour?.devoirs ?? []).find((item: any) => item.idDevoir === idDevoir);
      if (!devoir) {
        continue;
      }

      const details = (jour?.details?.matieres ?? []).find((item: any) => item.id === idDevoir);
      return {
        devoir,
        detail: details?.aFaire?.contenu_decode ?? null
      };
    }

    return null;
  }

  private detectMatiereFromFiles(files: File[]): string {
    const texte = files.map((file) => file.name.toLowerCase()).join(' ');

    if (/(math|algebra|thal[eè]s|function)/.test(texte)) return 'mathematics';
    if (/(french|essay|literature|reading|francais|roman)/.test(texte)) return 'french';
    if (/(physics|chemistry|wave|mole|ion|physique|chimie)/.test(texte)) return 'physics-chemistry';
    if (/(history|war|revolution|histoire|guerre)/.test(texte)) return 'history';

    return 'other';
  }

  private slugify(value: string): string {
    return value
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .replace(/-{2,}/g, '-');
  }

  private isBrowser(): boolean {
    return typeof window !== 'undefined' && typeof localStorage !== 'undefined';
  }

  private readSessionState(): boolean {
    if (!this.isBrowser()) {
      return true;
    }

    const stored = localStorage.getItem(this.sessionStorageKey);
    if (stored === null) {
      localStorage.setItem(this.sessionStorageKey, 'true');
      return true;
    }

    return stored === 'true';
  }

  private writeSessionState(value: boolean): void {
    if (!this.isBrowser()) {
      return;
    }
    localStorage.setItem(this.sessionStorageKey, value ? 'true' : 'false');
  }

  private readFlashCardsState(): Record<string, DemoDeck[]> {
    const fallback = this.getDefaultFlashCards();
    if (!this.isBrowser()) {
      return fallback;
    }

    const stored = localStorage.getItem(this.flashCardsStorageKey);
    if (!stored) {
      this.writeFlashCardsState(fallback);
      return fallback;
    }

    try {
      const parsed = JSON.parse(stored) as Record<string, DemoDeck[]>;
      if (!parsed || typeof parsed !== 'object') {
        throw new Error('Invalid format');
      }
      return parsed;
    } catch {
      this.writeFlashCardsState(fallback);
      return fallback;
    }
  }

  private writeFlashCardsState(data: Record<string, DemoDeck[]>): void {
    if (!this.isBrowser()) {
      return;
    }
    localStorage.setItem(this.flashCardsStorageKey, JSON.stringify(data));
  }

  private getDefaultDevoirs() {
    return {
      'Monday, March 16, 2026': {
        devoirs: [
          { idDevoir: 101, matiere: 'Mathematics', interrogation: false, donneLe: '03/14/2026' },
          { idDevoir: 102, matiere: 'French', interrogation: true, donneLe: '03/15/2026' }
        ],
        details: {
          matieres: [
            {
              id: 101,
              aFaire: {
                contenu_decode: '<p>Complete exercises 3 to 6 on page 148 (quadratic equations) and write the method used for each question.</p>'
              }
            },
            {
              id: 102,
              aFaire: {
                contenu_decode: '<p>Prepare a short argument (about 10 lines) on the topic: <em>freedom of the press</em>.</p>'
              }
            }
          ]
        }
      },
      'Wednesday, March 18, 2026': {
        devoirs: [
          { idDevoir: 201, matiere: 'Physics-Chemistry', interrogation: false, donneLe: '03/16/2026' },
          { idDevoir: 202, matiere: 'Biology', interrogation: false, donneLe: '03/16/2026' }
        ],
        details: {
          matieres: [
            {
              id: 201,
              aFaire: {
                contenu_decode: '<p>Review ions and pH. Complete the table of chemical species covered in class.</p>'
              }
            },
            {
              id: 202,
              aFaire: {
                contenu_decode: '<p>Reread the photosynthesis chapter and learn the simplified diagram.</p>'
              }
            }
          ]
        }
      },
      'Friday, March 20, 2026': {
        devoirs: [
          { idDevoir: 301, matiere: 'History', interrogation: true, donneLe: '03/17/2026' }
        ],
        details: {
          matieres: [
            {
              id: 301,
              aFaire: {
                contenu_decode: '<p>Create a revision sheet on the Cold War: key dates, blocs, and major crises.</p>'
              }
            }
          ]
        }
      }
    };
  }

  private getDefaultNotes() {
    return [
      {
        codeMatiere: 'MAT',
        libelleMatiere: 'Mathematics',
        codePeriode: 'T3',
        devoir: 'Test: quadratic equations',
        valeur: '16',
        noteSur: '20',
        coef: '2',
        date: '05/03/2026',
        moyenneClasse: '12.4',
        minClasse: '4',
        maxClasse: '19',
        commentaire: 'Very good reasoning.'
      },
      {
        codeMatiere: 'MAT',
        libelleMatiere: 'Mathematics',
        codePeriode: 'T3',
        devoir: 'Quiz: Thales theorem',
        valeur: '13,5',
        noteSur: '20',
        coef: '1',
        date: '12/03/2026',
        moyenneClasse: '11.2',
        minClasse: '5',
        maxClasse: '18'
      },
      {
        codeMatiere: 'FRA',
        libelleMatiere: 'French',
        codePeriode: 'T3',
        devoir: 'Text commentary',
        valeur: '14',
        noteSur: '20',
        coef: '2',
        date: '08/03/2026',
        moyenneClasse: '12.1',
        minClasse: '6',
        maxClasse: '18',
        commentaire: 'Clear writing, arguments can be deeper.'
      },
      {
        codeMatiere: 'HIS',
        libelleMatiere: 'History',
        codePeriode: 'T3',
        devoir: 'Cold War multiple-choice quiz',
        valeur: '15',
        noteSur: '20',
        coef: '1',
        date: '10/03/2026',
        moyenneClasse: '13.0',
        minClasse: '7',
        maxClasse: '19'
      },
      {
        codeMatiere: 'PHY',
        libelleMatiere: 'Physics-Chemistry',
        codePeriode: 'T3',
        devoir: 'Lab: ions and pH',
        valeur: '17',
        noteSur: '20',
        coef: '2',
        date: '14/03/2026',
        moyenneClasse: '12.7',
        minClasse: '5',
        maxClasse: '18'
      },
      {
        codeMatiere: 'FRA',
        libelleMatiere: 'French',
        codePeriode: 'T2',
        devoir: 'Independent reading',
        valeur: '11',
        noteSur: '20',
        coef: '1',
        date: '15/01/2026',
        moyenneClasse: '11.8',
        minClasse: '4',
        maxClasse: '17'
      }
    ];
  }

  private getDefaultCours(): Record<string, DemoCourse[]> {
    return {
      mathematics: [
        {
          nom: 'Quadratic equations',
          fichier: 'quadratic-equations.md',
          contenu: `# Quadratic equations

## General form
A quadratic equation is written as:
\(ax^2 + bx + c = 0\), with \(a \neq 0\).

## Method
1. Compute the discriminant \(\Delta = b^2 - 4ac\)
2. Study its sign
3. Deduce the solutions`
        },
        {
          nom: 'Thales theorem',
          fichier: 'thales-theorem.md',
          contenu: `# Thales theorem

In a triangle, if a line is parallel to one side, it cuts the other two sides proportionally.

Always write proportions in the same order.`
        }
      ],
      french: [
        {
          nom: 'Figures of speech',
          fichier: 'figures-of-speech.md',
          contenu: `# Figures of speech

## Must-know
- Metaphor
- Simile
- Hyperbole
- Personification

Always provide an example to justify your answer.`
        }
      ],
      history: [
        {
          nom: 'The Cold War',
          fichier: 'cold-war.md',
          contenu: `# The Cold War

An ideological conflict between the United States and the USSR after 1945.

## Key dates
- 1947: Truman Doctrine
- 1961: Berlin Wall
- 1991: End of the USSR`
        }
      ],
      'physics-chemistry': [
        {
          nom: 'Ions and pH',
          fichier: 'ions-ph.md',
          contenu: `# Ions and pH

The pH indicates how acidic a solution is:
- pH < 7: acidic
- pH = 7: neutral
- pH > 7: basic`
        }
      ]
    };
  }

  private getDefaultFlashCards(): Record<string, DemoDeck[]> {
    return {
      mathematics: [
        {
          nom: 'Quadratic equations',
          fichier: 'quadratic-equations.json',
          cartes: [
            {
              question: 'What is the discriminant formula?',
              reponse: 'Δ = b² - 4ac'
            },
            {
              question: 'What does Δ > 0 mean?',
              reponse: 'There are two distinct real solutions.'
            }
          ]
        }
      ],
      french: [
        {
          nom: 'Figures of speech',
          fichier: 'figures-style.json',
          cartes: [
            {
              question: 'What is a metaphor?',
              reponse: 'An implicit comparison without using a linking word.'
            },
            {
              question: 'What is a hyperbole?',
              reponse: 'An exaggeration used for emphasis.'
            }
          ]
        }
      ],
      history: [
        {
          nom: 'Cold War',
          fichier: 'cold-war.json',
          cartes: [
            {
              question: 'When did the Berlin Wall fall?',
              reponse: '1989'
            }
          ]
        }
      ]
    };
  }
}
