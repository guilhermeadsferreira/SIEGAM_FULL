package org.ufg.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class EventoResponseDTO {
    private UUID id;
    private String nomeEvento;
    private Boolean personalizavel;
    private LocalDateTime horario;
}