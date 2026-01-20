package org.ufg.dto;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.UUID;

@Data
public class AvisoResponseDTO {

    private UUID id;

    private UUID idEvento;
    private String nomeEvento;

    private UUID idCidade;
    private String nomeCidade; 

    private BigDecimal valor;
    private LocalDate dataGeracao;
    private LocalDate dataReferencia;
    private BigDecimal valorLimite;
    private String unidadeMedida;
    private BigDecimal diferenca;
    private LocalTime horario;
    private BigDecimal segundos;
}