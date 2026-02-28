import { Component } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.css'
})
export class AuthComponent {
  constructor(private apiService: ApiService) { }
}
