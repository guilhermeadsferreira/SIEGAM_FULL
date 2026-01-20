import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    RouterModule,
    MatSnackBarModule 
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit {
  form = new FormGroup({
    username: new FormControl('', [Validators.required, Validators.email]), 
    password: new FormControl('', Validators.required),
  });

  isLoading = true; 
  constructor(
    private router: Router,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {}
  ngOnInit(): void {
    this.authService.checkTokenValidity().subscribe(isValid => {
      this.isLoading = false;
      if (isValid) {
        const role = localStorage.getItem('user_role');
        if (role === 'ADMIN') {
          this.router.navigate(['/admin']);
        } else {
          this.router.navigate(['/preferences/cities']);
        }
      }
    });
  }

  onSubmit() {
    if (this.form.valid) {
      this.isLoading = true;
      
      const loginDto = {
        email: this.form.value.username || '', 
        senha: this.form.value.password || ''
      };

      this.authService.login(loginDto).subscribe({
        next: (response) => {
          console.log('Login realizado!', response);
          this.isLoading = false;
          
          const role = response.nivelAcesso; 

          if (role === 'ADMIN') {
            this.router.navigate(['/admin']);
          } else {
            this.router.navigate(['/preferences/cities']);
          }
        },
        error: (err) => {
          console.error('Erro no login:', err);
          this.isLoading = false;
          
          let msg = 'Erro ao conectar ao servidor.';

          if (err.status === 401 || err.status === 403 || err.status === 404) {
            msg = 'Usuário ou senha inválidos.';
          }

          this.snackBar.open(msg, 'Fechar', {
            duration: 4000,
            panelClass: ['error-snackbar'],
            verticalPosition: 'top',
            horizontalPosition: 'center'
          });
        }
      });
    } else {
      this.form.markAllAsTouched();
    }
  }
}