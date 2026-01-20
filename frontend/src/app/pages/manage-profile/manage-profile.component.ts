import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-manage-profile',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSnackBarModule
  ],
  templateUrl: './manage-profile.component.html',
  styleUrls: ['./manage-profile.component.scss'],
})
export class ManageProfileComponent {
  form = new FormGroup({
    username: new FormControl('', Validators.required),
    password: new FormControl('', Validators.required),
  });

  isLoading = false;

  constructor(
    private router: Router,
    private authService: AuthService, 
    private snackBar: MatSnackBar
  ) {}

  onEditPreferences() {
    if (this.form.valid) {
      this.isLoading = true;
      const credentials = {
        email: this.form.value.username || '',
        senha: this.form.value.password || ''
      };

      this.authService.login(credentials).subscribe({
        next: () => {
          this.isLoading = false;
          this.router.navigate(['/preferences/cities']);
        },
        error: (err) => {
          this.isLoading = false;
          this.handleError(err);
        }
      });
    }
  }

  onUnsubscribe() {
    if (this.form.valid) {
      const confirmed = window.confirm('Tem certeza que deseja cancelar todos os seus avisos?');
      
      if (confirmed) {
        this.isLoading = true;
        const credentials = {
          email: this.form.value.username || '',
          senha: this.form.value.password || ''
        };

        this.authService.login(credentials).subscribe({
          next: () => {
            const emptyPayload = {}; 

            this.authService.updateFullProfile(emptyPayload as any).subscribe({
              next: () => {
                this.isLoading = false;
                this.snackBar.open('Você foi descadastrado dos avisos com sucesso.', 'OK', { duration: 5000 });
                this.authService.logout(); 
              },
              error: (err) => {
                this.isLoading = false;
                this.snackBar.open('Erro ao descadastrar. Tente novamente.', 'Fechar', { duration: 5000 });
                console.error(err);
              }
            });
          },
          error: (err) => {
            this.isLoading = false;
            this.handleError(err);
          }
        });
      }
    }
  }

  private handleError(err: any) {
    console.error('Erro de autenticação:', err);
    let msg = 'Erro ao processar solicitação.';
    if (err.status === 401 || err.status === 403) {
      msg = 'Usuário ou senha incorretos.';
    }
    this.snackBar.open(msg, 'Fechar', {
      duration: 4000,
      panelClass: ['error-snackbar'],
      verticalPosition: "top"

    });
  }
}