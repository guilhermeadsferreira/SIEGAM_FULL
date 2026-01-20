package org.ufg.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;
import java.math.BigDecimal;
import java.util.UUID;

@Data
public class PreferenciaRequestDTO {

    @NotNull(message = "O ID do evento é obrigatório.")
    private UUID idEvento;

    @NotNull(message = "O ID da cidade é obrigatório.")
    private UUID idCidade;

    private BigDecimal valor;

    private Boolean personalizavel;
}