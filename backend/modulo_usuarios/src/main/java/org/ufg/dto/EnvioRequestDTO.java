package org.ufg.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;
import java.util.UUID;

@Data
public class EnvioRequestDTO {

    @NotNull(message = "O ID do canal é obrigatório.")
    private UUID idCanal;

    @NotNull(message = "O ID do aviso é obrigatório.")
    private UUID idAviso;

    @NotNull(message = "O ID do usuário destinatário é obrigatório.")
    private UUID idUsuarioDestinatario;

    @NotNull(message = "O ID do status é obrigatório.")
    private UUID idStatus;
}