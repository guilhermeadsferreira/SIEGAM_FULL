package org.ufg.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import lombok.Data;

import java.util.List;

@Data
public class EnvioBulkRequestDTO {

    @NotEmpty(message = "A lista de envios não pode estar vazia.")
    @Valid
    private List<EnvioRequestDTO> envios;
}