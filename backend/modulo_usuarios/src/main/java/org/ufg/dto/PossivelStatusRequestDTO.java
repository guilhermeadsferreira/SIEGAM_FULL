package org.ufg.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;
import java.util.UUID;

@Data
public class PossivelStatusRequestDTO {

    @NotBlank(message = "O nome do status é obrigatório.")
    @Size(max = 45, message = "O nome do status deve ter no máximo 45 caracteres.")
    private String nomeStatus;

    @NotNull(message = "O ID do canal associado é obrigatório.")
    private UUID idCanal;
}