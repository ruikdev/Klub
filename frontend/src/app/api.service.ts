import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private readonly API_BASE_URL = '/api';

  constructor(private http: HttpClient) { }

  getCommentaires(): Observable<any> {
    return this.http.get(`${this.API_BASE_URL}/notes/commentaire`);
  }

  getDevoirs(): Observable<any> {
    return this.http.get(`${this.API_BASE_URL}/devoirs`);
  }

  getNotes(): Observable<any> {
    return this.http.get(`${this.API_BASE_URL}/notes`);
  }

  sendChatMessage(question: string, idDevoir?: number): Observable<any> {
    const payload = {
      question: question,
      id: idDevoir || null
    };
    return this.http.post(`${this.API_BASE_URL}/chat`, payload);
  }
}
