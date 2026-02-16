import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private readonly API_BASE_URL = '/api';

  constructor(private http: HttpClient) { }

  getDevoirs(): Observable<any> {
    return this.http.get(`${this.API_BASE_URL}/devoirs`);
  }
}
