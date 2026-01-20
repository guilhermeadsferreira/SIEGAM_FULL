import { Routes } from '@angular/router';
import { LoginComponent } from './pages/auth/login/login.component';
import { RegisterComponent } from './pages/auth/register/register.component';
import { PreferencesComponent } from './pages/preferences/cities/cities-preferences.component';
import { UserPreferencesComponent } from './pages/preferences/user/user-preferences.component';
import { AdminPanelComponent } from './pages/admin/admin-panel/admin-panel.component';
import { adminGuard } from './guards/admin.guard';
import { ManageProfileComponent } from './pages/manage-profile/manage-profile.component';
export const routes: Routes = [
  {
    path: 'auth',
    children: [
      { path: 'login', component: LoginComponent },
      { path: 'register', component: RegisterComponent }, // <-- Adicione esta linha
      { path: '', redirectTo: 'login', pathMatch: 'full' }
    ]
	},
	{
		path: 'preferences', 
		children: [
			{ path: 'user', component: UserPreferencesComponent },
			{ path: 'cities', component: PreferencesComponent },
			{ path: '', redirectTo: 'cities', pathMatch: 'full' }
		]
	},
	{
		path: 'admin', 
		children: [
			{ path: 'admin-panel', component: AdminPanelComponent, canActivate: [adminGuard] },
			{ path: '', redirectTo: 'admin-panel', pathMatch: 'full' }
		]
	},
	{
		path: 'manage-profile', 
		children: [
			{ path: '', component: ManageProfileComponent },
			{ path: '', redirectTo: 'manage-profile', pathMatch: 'full' }
		]
	},
  	{ path: '', redirectTo: '/auth/register', pathMatch: 'full' },
  	{ path: '**', redirectTo: '/auth/register' }
];
