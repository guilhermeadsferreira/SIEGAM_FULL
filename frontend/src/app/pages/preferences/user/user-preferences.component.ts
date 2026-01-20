import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatRadioModule } from '@angular/material/radio';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { Router } from '@angular/router';

// Serviços e Constantes
import { AuthService } from '../../../services/auth.service';
import { EVENT_IDS, CHANNEL_IDS } from './ids.constants';

// Interface para os dados recebidos da tela anterior
interface CityPreferenceInput {
  name: string;
  preferences: {
    humidity: boolean;
    temperature: boolean;
    wind: boolean;
    heavyRain: boolean;
  };
}

@Component({
  selector: 'app-user-preferences',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatCheckboxModule,
    MatRadioModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    MatSnackBarModule,
  ],
  templateUrl: './user-preferences.component.html',
  styleUrls: ['./user-preferences.component.scss'],
})
export class UserPreferencesComponent implements OnInit, OnDestroy {
  preferencesForm: FormGroup;
  private destroy$ = new Subject<void>();
  
  citiesData: CityPreferenceInput[] = [];
  
  dynamicCityIds: { [key: string]: string } = {};

  showHumidity = false;
  showTemp = false;
  showWind = false;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {
    this.preferencesForm = this.fb.group({
      humidity: this.fb.group({
        type: ['standard'], 
      }),
      highTemp: this.fb.group({
        type: ['standard'], 
        value: [{ value: null, disabled: true }],
      }),
      lowTemp: this.fb.group({
        type: ['standard'], 
        value: [{ value: null, disabled: true }],
      }),
      wind: this.fb.group({
        type: ['critical'], 
      }),
      channels: this.fb.group({
        email: [true],
        whatsapp: [false],
      }),
    });
  }

  ngOnInit(): void {
    // 1. Recuperar dados passados via State (Router)
    const nav = this.router.getCurrentNavigation();
    
    if (nav?.extras?.state) {
      this.citiesData = nav.extras.state['citiesPreferences'];
      this.dynamicCityIds = nav.extras.state['cityMap'] || {};
    } else if (history.state.citiesPreferences) {
      this.citiesData = history.state.citiesPreferences;
      this.dynamicCityIds = history.state.cityMap || {};
    }

    if (!this.citiesData || this.citiesData.length === 0) {
      this.router.navigate(['/preferences/cities']);
      return;
    }

    this.analyzeSelectedPreferences();

    this.watchAndToggle('highTemp');
    this.watchAndToggle('lowTemp');
  }

  private analyzeSelectedPreferences() {
    this.showHumidity = this.citiesData.some(c => c.preferences.humidity);
    this.showTemp = this.citiesData.some(c => c.preferences.temperature);
    this.showWind = this.citiesData.some(c => c.preferences.wind);
  }

  private watchAndToggle(groupName: 'highTemp' | 'lowTemp'): void {
    const group = this.preferencesForm.get(groupName) as FormGroup;
    const typeCtrl = group.get('type');
    const valueCtrl = group.get('value');

    typeCtrl?.valueChanges.pipe(takeUntil(this.destroy$)).subscribe(val => {
      if (val === 'custom') {
        valueCtrl?.enable();
        valueCtrl?.setValidators([Validators.required, Validators.pattern('^[0-9]*$')]);
      } else {
        valueCtrl?.disable();
        valueCtrl?.clearValidators();
        valueCtrl?.reset();
      }
      valueCtrl?.updateValueAndValidity();
    });
  }

onBack() {
    this.router.navigate(['/preferences/cities'], {
      state: { 
        citiesPreferences: this.citiesData,
        cityMap: this.dynamicCityIds
      }
    });
  }

  logout() {
    this.authService.logout();
  }

  onSubmit() {
    if (this.preferencesForm.valid) {
      const formVal = this.preferencesForm.getRawValue();
      const preferencesPayload: any[] = [];

      this.citiesData.forEach(cityInput => {
        let targetCityIds: string[] = [];

        if (cityInput.name === 'TODAS') {
          targetCityIds = Object.values(this.dynamicCityIds).filter(id => id !== 'TODAS_ID');
        } else {
          const id = this.dynamicCityIds[cityInput.name];
          if (id) targetCityIds.push(id);
        }

        // Para cada cidade alvo (pode ser 1 ou centenas), cria as preferências
        targetCityIds.forEach(cityId => {
          
          // 1. UMIDADE
          if (cityInput.preferences.humidity) {
            const isCustom = formVal.humidity.type === 'custom';
            preferencesPayload.push({
              idEvento: EVENT_IDS.HUMIDITY,
              idCidade: cityId,
              personalizavel: isCustom,
              valor: isCustom ? 60 : null // Valor fixo 60 para risco à saúde
            });
          }

          // 2. TEMPERATURA
          if (cityInput.preferences.temperature) {
            // Alta
            const isHighCustom = formVal.highTemp.type === 'custom';
            preferencesPayload.push({
              idEvento: EVENT_IDS.HIGH_TEMP,
              idCidade: cityId,
              personalizavel: isHighCustom,
              valor: isHighCustom ? Number(formVal.highTemp.value) : null
            });
            // Baixa
            const isLowCustom = formVal.lowTemp.type === 'custom';
            preferencesPayload.push({
              idEvento: EVENT_IDS.LOW_TEMP,
              idCidade: cityId,
              personalizavel: isLowCustom,
              valor: isLowCustom ? Number(formVal.lowTemp.value) : null
            });
          }

          // 3. VENTO
          if (cityInput.preferences.wind) {
            const windType = formVal.wind.type;
            let windVal = null;
            
            // Mapeamento dos intervalos para o valor menor
            if (windType === '12-20') {
              windVal = 12;
            } else if (windType === '20-30') {
              windVal = 20;
            } else if (windType === 'critical') {
              windVal = 30;
            }

            preferencesPayload.push({
              idEvento: EVENT_IDS.WIND,
              idCidade: cityId,
              personalizavel: true, // Vento agora é sempre personalizável
              valor: windVal
            });
          }

          // 4. CHUVA (Sempre padrão)
          if (cityInput.preferences.heavyRain) {
            preferencesPayload.push({
              idEvento: EVENT_IDS.RAIN,
              idCidade: cityId,
              personalizavel: false,
              valor: null
            });
          }
        });
      });

      const channelsPayload: string[] = [];
      if (formVal.channels.email) channelsPayload.push(CHANNEL_IDS.EMAIL);
      if (formVal.channels.whatsapp) channelsPayload.push(CHANNEL_IDS.WHATSAPP);

      const finalPayload = {
        preferencias: preferencesPayload,
        idsCanaisPreferidos: channelsPayload
      };

      console.log('Enviando Payload:', finalPayload);

      this.authService.updateFullProfile(finalPayload).subscribe({
        next: () => {
          this.snackBar.open('Preferências salvas com sucesso!', 'OK', { duration: 3000, verticalPosition: "top" });
        },
        error: (err) => {
          console.error('Erro ao salvar', err);
          this.snackBar.open('Erro ao salvar preferências. Tente novamente.', 'Fechar', { duration: 5000, verticalPosition: "top" });
        }
      });
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  
}