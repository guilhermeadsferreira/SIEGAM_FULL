import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Aviso, Page } from '../models/aviso.models';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AvisoService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  filtrarAvisos(
    data: string | null, 
    idEvento: string | null, 
    idCidade: string | null, 
    page: number, 
    size: number
  ): Observable<Page<Aviso>> {
    
    let params = new HttpParams()
      .set('page', page.toString())
      .set('size', size.toString());

    if (data) {
      params = params.set('data', data);
    }
    if (idEvento) {
      params = params.set('idEvento', idEvento);
    }
    if (idCidade) {
      params = params.set('idCidade', idCidade);
    }

    return this.http.get<Page<Aviso>>(`${this.apiUrl}/avisos/filtro`, { params });
  }
}