import { Component, EventEmitter, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.css'
})
export class AuthComponent {
  @Output() loginSuccess = new EventEmitter<void>();

  code: string = '';
  errorMessage: string = '';

  constructor(private apiService: ApiService) { }

  postLogin(password: string) {
    this.errorMessage = '';
    this.apiService.login(password).subscribe({
      next: () => this.loginSuccess.emit(),
      error: () => this.errorMessage = 'Invalid code'
    });
  }
}
