package org.ufg.dto;

import lombok.Data;
import java.util.UUID;

@Data
public class EnvioResponseDTO {
    private UUID id;
    private UUID idCanal;
    private UUID idAviso;
    private UUID idUsuarioDestinatario;
    private UUID idStatus;
}