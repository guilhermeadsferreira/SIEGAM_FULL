package org.ufg.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class EventoRequestDTO {

    @NotBlank(message = "O nome do evento é obrigatório.")
    @Size(max = 50, message = "O nome do evento deve ter no máximo 50 caracteres.")
    private String nomeEvento;

    @NotNull(message = "O campo 'personalizavel' é obrigatório.")
    private Boolean personalizavel;

    @NotNull(message = "O horário do evento é obrigatório.")
    private LocalDateTime horario;
}