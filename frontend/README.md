# SIGEDAM – Frontend  
Aplicação web desenvolvida em **Angular 18**, responsável pela interface visual do projeto **SIGEDAM**.  
Este frontend fornece acesso às funcionalidades para **usuários** e **administradores**, incluindo autenticação, preferências, gestão de perfil e painel administrativo.

---

## Visão Geral

O frontend do **SIGEDAM** é uma SPA (Single Page Application) construída com **Angular 18**, **Angular Material** e **TypeScript**.  
Ele se comunica com a API do SIGEDAM para autenticação, carregamento de catálogos, gerenciamento de avisos e demais operações do sistema.

### Perfis disponíveis:
- **Usuário comum**  
  Login, registro, gerenciamento de perfil, configurações e preferências.

- **Administrador**  
  Acesso ao **painel administrativo** para visualizar e gerenciar operações avançadas.

---

## Tecnologias Utilizadas

| Tecnologia | Versão | Descrição |
|-----------|--------|-----------|
| **Angular** | 18.x | Framework principal da aplicação |
| **Angular CLI** | 18.1.0 | Geração e execução do projeto |
| **TypeScript** | 5.5.x | Linguagem da aplicação |
| **Angular Material** | 18.x | Componentes de UI |
| **RxJS** | 7.8.x | Programação reativa |
| **SCSS** | — | Estilização principal |

---

## Requisitos para Desenvolvimento

Instale as dependências essenciais:

- **Node.js 18+**
- **NPM 9+**
- **Angular CLI 18+**
  ```bash
  npm install -g @angular/cli

Certifique-se de ter acesso à API do SIGEDAM (URL configurada nos arquivos environment).


## Preparação do Ambiente

Instale os pacotes:
```
npm install
```

Configure os ambientes em:

```
src/environments/environment.ts
src/environments/environment.development.ts
```

Exemplo:
```
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000/api'
};
```
## Executando a Aplicação
Modo de Desenvolvimento
```
npm start
# ou
ng serve
```

Acesse:
http://localhost:4200/

## Build de Produção
```
npm run build
# ou
ng build
```

Arquivos gerados em:
```
dist/frontend/
```
## Testes Unitários
```
npm test
```


Estrutura do Projeto
```
src
├── app
│   ├── guards                # Autorização e controle de rotas
│   ├── models                # Modelos de dados
│   ├── services              # Serviços e interceptors
│   ├── pages
│   │   ├── auth              # Login e registro
│   │   ├── admin             # Painel administrativo
│   │   ├── manage-profile    # Edição de perfil
│   │   └── preferences       # Preferências do usuário
│   ├── app.routes.ts         # Configuração de rotas
│   ├── app.config.ts         # Configuração inicial da aplicação
│   └── app.component.*       # Componente raiz
│
├── assets                    # Arquivos estáticos
├── environments              # Configurações de ambiente
├── main.ts                   # Entrada da aplicação
└── styles.scss               # Estilos globais

```
## Funcionalidades Principais
## Autenticação

- Login

- Registro

- Guardião de rotas administrativas (admin.guard.ts)

- Interceptor de autenticação (auth.interceptor.ts)

- Armazenamento seguro de token

## Gestão de Perfil

- Atualização de dados do usuário

- Preferências individuais

- Gerenciamento de cidades

## Painel Administrativo

- Acesso exclusivo a administradores

- Visualização e gerenciamento de recursos do sistema

## Serviços

- auth.service.ts

- aviso.service.ts

- catalog.service.ts

Todos conectados ao backend do SIGEDAM.

## Scripts Disponíveis
|Comando|	Descrição|
|----------|----------|
|npm start|	Executa o projeto em dev|
|npm run build|	Gera o build para produção|
|npm run watch|	Build contínuo em desenvolvimento|
|npm test|	Executa testes unitários|

## Observações

- O projeto utiliza SCSS como padrão de estilos.
- Atualize os ambientes conforme URLs do backend.
- Mantenha consistência com os módulos utilizados do Angular Material.