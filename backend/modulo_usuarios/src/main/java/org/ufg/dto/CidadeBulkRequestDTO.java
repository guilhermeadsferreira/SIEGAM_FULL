package org.ufg.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import lombok.Data;

import java.util.List;

@Data
public class CidadeBulkRequestDTO {

    @NotEmpty(message = "A lista de cidades não pode estar vazia.")

    @Valid
    private List<CidadeRequestDTO> cidades;
}