import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { Router, RouterModule } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../../services/auth.service';
import { MatCheckboxModule } from '@angular/material/checkbox';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    RouterModule,
    MatSnackBarModule,
    MatCheckboxModule
  ],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss'],
})
export class RegisterComponent {
  form = new FormGroup({
    fullName: new FormControl('', [Validators.required]),
    email: new FormControl('', [Validators.required, Validators.email]),
    phoneNumber: new FormControl('', [Validators.required, Validators.pattern(/^\d{11}$/)]),
    password: new FormControl('', [Validators.required, Validators.minLength(6)]),
    confirmPassword: new FormControl('', [Validators.required]),
    termsAccepted: new FormControl(false, [Validators.requiredTrue])
  }, { validators: this.passwordMatchValidator });

  // Variável para controlar loading do botão
  isLoading = false;

  constructor(
    private router: Router,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {}

  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('password')?.value;
    const confirmPassword = control.get('confirmPassword')?.value;
    return password === confirmPassword ? null : { passwordMismatch: true };
  }

  onSubmit() {
    if (this.form.valid) {
      this.isLoading = true; 

      const registerPayload = {
        nome: this.form.value.fullName,
        email: this.form.value.email,
        whatsapp: this.form.value.phoneNumber,
        senha: this.form.value.password,
        nivelAcesso: 'CLIENTE'
      };

      const loginPayload = {
        email: this.form.value.email || '',
        senha: this.form.value.password || ''
      };

      this.authService.register(registerPayload).subscribe({
        next: () => {
          console.log('Cadastro realizado. Iniciando login automático...');
          
          this.snackBar.open('Cadastro realizado! Entrando no sistema...', 'OK', {
            duration: 2000,
            verticalPosition: 'top'
          });

          this.authService.login(loginPayload).subscribe({
            next: (loginResponse) => {
              this.isLoading = false;
              
              const role = loginResponse.nivelAcesso;
              
              if (role === 'ADMIN') {
                this.router.navigate(['/admin']);
              } else {
                this.router.navigate(['/preferences/cities']);
              }
            },
            error: (loginErr) => {
              console.error('Erro no auto-login:', loginErr);
              this.isLoading = false;
              this.router.navigate(['/auth/login']);
            }
          });
        },
        error: (error) => {
          console.error('Erro ao cadastrar:', error);
          this.isLoading = false;

          let errorMsg = 'Erro ao realizar cadastro. Tente novamente.';
          if (error.status === 400) {
            errorMsg = 'Dados inválidos. Verifique se o e-mail já está em uso.';
          }

          this.snackBar.open(errorMsg, 'Fechar', {
            duration: 5000,
            panelClass: ['error-snackbar'],
            verticalPosition: "top"
          });
        }
      });
    } else {
      this.form.markAllAsTouched();
    }
  }
}