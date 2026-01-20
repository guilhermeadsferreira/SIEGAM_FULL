import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError, tap, map, catchError } from 'rxjs';import { Router } from '@angular/router';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient, private router: Router) { }

  login(credentials: { email: string; senha: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/usuarios/login`, credentials)
      .pipe(
        tap(response => {
          this.doLoginUser(response);
        })
      );
  }

  private doLoginUser(response: any) {
    localStorage.setItem('access_token', response.token);
    localStorage.setItem('user_id', response.id);
    localStorage.setItem('user_role', response.nivelAcesso);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_role');
    this.router.navigate(['/auth/login']);
  }
  
  register(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/usuarios`, userData);
  }

  savePreferences(preferencesPayload: any[]): Observable<any> {
    return this.http.post(`${this.apiUrl}/preferencias/lote`, preferencesPayload);
  }

  updateFullProfile(payload: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/usuarios/meu-perfil`, payload, { 
      responseType: 'text' 
    });
  }

  getUserRole(): string | null {
    return localStorage.getItem('user_role');
  }

  checkTokenValidity(): Observable<boolean> {
    const token = this.getToken();
    if (!token) {
      return of(false);
    }

    return this.http.get(`${this.apiUrl}/preferencias`).pipe(
      map(() => true),
      catchError((error) => {
        this.logout();
        return of(false);
      })
    );
  }


  getUserPreferences(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/preferencias`);
  }
}