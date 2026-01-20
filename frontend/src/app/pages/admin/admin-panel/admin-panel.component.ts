import { Component, NgModule, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { Router } from '@angular/router';
import { MAT_DATE_LOCALE } from '@angular/material/core';
import { AuthService } from '../../../services/auth.service';
import { CatalogService } from '../../../services/catalog.service';
import { Aviso } from '../../../models/aviso.models';
import { Cidade, Evento } from '../../../models/catalog.models';
import { MatTableModule } from '@angular/material/table'; 
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator'; 
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner'; 
import { AvisoService } from '../../../services/aviso.service'; 

@Component({
  selector: 'app-admin-panel',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatSidenavModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatListModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatTableModule,
    MatPaginatorModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './admin-panel.component.html',
  styleUrls: ['./admin-panel.component.scss'],
//   provideNgxMask(),
  providers: [
  ],
})
export class AdminPanelComponent implements OnInit{
  selectedView: 'avisos' | 'envios' = 'avisos';
  filterForm: FormGroup;

  eventos: Evento[] = [];
  cidades: Cidade[] = [];

  avisosData: Aviso[] = [];
  totalElements = 0;
  pageSize = 10;
  pageIndex = 0;
  isLoading = false;

displayedColumns: string[] = ['data', 'evento', 'cidade', 'valor'];

  constructor(private fb: FormBuilder, 
    private router: Router,
    private authService: AuthService,
    private catalogService: CatalogService,
    private avisoService: AvisoService
  ) {
    this.filterForm = this.fb.group({
      data: [null],
      evento: [''],
      cidade: [''],
    });
  }
  ngOnInit(): void {
    this.loadCatalogs();
    this.buscarAvisos();
  }

  loadCatalogs() {
    this.catalogService.getAllEventos().subscribe({
      next: (data) => this.eventos = data,
      error: (err) => console.error('Erro ao carregar eventos', err)
    });

    this.catalogService.getAllCidades().subscribe({
      next: (data) => this.cidades = data,
      error: (err) => console.error('Erro ao carregar cidades', err)
    });
    this.catalogService.getAllEventos().subscribe(d => this.eventos = d);
    this.catalogService.getAllCidades().subscribe(d => this.cidades = d);
  }

  onFilter() {
    this.pageIndex = 0;
    this.buscarAvisos();
  }

  onPageChange(event: PageEvent) {
    this.pageIndex = event.pageIndex;
    this.pageSize = event.pageSize;
    this.buscarAvisos();
  }

  logout() {
    this.authService.logout();
  }

  buscarAvisos() {
    this.isLoading = true;
    
    const { data, evento, cidade } = this.filterForm.value;

    let dataFormatada = null;
    if (data) {
      const d = new Date(data);
      dataFormatada = d.toLocaleDateString('en-CA'); 
    }

    this.avisoService.filtrarAvisos(
      dataFormatada, 
      evento || null,
      cidade || null, 
      this.pageIndex, 
      this.pageSize
    ).subscribe({
      next: (page) => {
        this.avisosData = page.content;
        this.totalElements = page.totalElements;
        this.isLoading = false;
        console.log('Avisos carregados:', this.avisosData);
      },
      error: (err) => {
        console.error('Erro ao buscar avisos', err);
        this.isLoading = false;
      }
    });
  }

}

