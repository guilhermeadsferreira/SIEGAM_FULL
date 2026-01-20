import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Cidade, Evento } from '../models/catalog.models';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CatalogService {
  private apiUrl = environment.apiUrl; 

  constructor(private http: HttpClient) { }

  getAllCidades(): Observable<Cidade[]> {
    return this.http.get<Cidade[]>(`${this.apiUrl}/cidades`);
  }

  getAllEventos(): Observable<Evento[]> {
    return this.http.get<Evento[]>(`${this.apiUrl}/eventos`);
  }
}