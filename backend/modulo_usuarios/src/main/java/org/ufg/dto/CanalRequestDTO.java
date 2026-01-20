package org.ufg.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class CanalRequestDTO {

    @NotBlank(message = "O nome do canal é obrigatório.")
    @Size(max = 45, message = "O nome do canal deve ter no máximo 45 caracteres.")
    private String nomeCanal;
}