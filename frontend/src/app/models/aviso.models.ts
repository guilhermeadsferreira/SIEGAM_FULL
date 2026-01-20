export interface Aviso {
  id: string;
  idEvento: string;
  nomeEvento: string;
  idCidade: string;
  nomeCidade: string;
  dataGeracao: string;
  dataReferencia: string;
  valor: number;
  unidadeMedida: string;
}

export interface Page<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  pageNumber: number;
  pageSize: number;
}