package org.ufg.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class CidadeRequestDTO {

    @NotBlank(message = "O nome da cidade é obrigatório.")
    @Size(max = 100, message = "O nome da cidade deve ter no máximo 100 caracteres.")
    private String nome;
}