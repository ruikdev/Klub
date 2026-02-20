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
    return this.http.post(`${this.API_BASE_URL}/chat_devoirs`, payload);
  }

  sendOcrImages(images: File | File[]): Observable<any> {
    const formData = new FormData();
    const files = Array.isArray(images) ? images : [images];
    files.forEach(image => formData.append('images', image));
    return this.http.post(`${this.API_BASE_URL}/ocr`, formData);
  }


  sendChatMessageCours(question: string, cours: string): Observable<any> {
    const payload = {
      question: question,
      cours: cours
    };
    return this.http.post(`${this.API_BASE_URL}/cours/chat`, payload);
  }

  getCours(): Observable<any> {
    return this.http.get(`${this.API_BASE_URL}/cours`);
  }

  getFlashCards(): Observable<any> {
    return this.http.get(`${this.API_BASE_URL}/flash-cards`);
  }

  sendChatGlobal(question: string, history: { role: string; content: string }[]): Observable<any> {
    const payload = {
      question,
      messages: history
    };
    return this.http.post(`${this.API_BASE_URL}/chat/global`, payload);
  }
}
