package org.ufg.dto;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

@Data
public class PreferenciaResponseDTO {
    private UUID id;
    private UUID idUsuario;
    private UUID idEvento;
    private UUID idCidade;
    private LocalDate dataCriacao;
    private LocalDate dataUltimaEdicao;
    private BigDecimal valor;
    private Boolean personalizavel;
}