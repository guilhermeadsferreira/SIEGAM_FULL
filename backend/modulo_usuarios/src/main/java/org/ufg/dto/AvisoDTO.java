package org.ufg.dto;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.UUID;
import jakarta.validation.constraints.*;
import lombok.Data;

@Data
public class AvisoDTO {

    private UUID id;

    @NotNull private UUID idEvento;

    private BigDecimal valor;

    @NotNull private LocalDate dataGeracao;

    @NotNull private LocalDate dataReferencia;

    @NotNull private UUID idCidade;

    private BigDecimal valorLimite;

    @NotBlank @Size(max = 45)
    private String unidadeMedida;

    @NotNull @DecimalMin("0.0")
    private BigDecimal diferenca;

    private LocalTime horario;

    private BigDecimal segundos;
}