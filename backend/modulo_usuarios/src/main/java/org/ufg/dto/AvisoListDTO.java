package org.ufg.dto;

import java.util.List;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import lombok.Data;

@Data
public class AvisoListDTO {


    @NotEmpty(message = "A lista de avisos não pode ser vazia.")
    @Valid
    private List<AvisoDTO> avisos;

    public AvisoListDTO() {
    }

    public AvisoListDTO(List<AvisoDTO> avisos) {
        this.avisos = avisos;
    }
}