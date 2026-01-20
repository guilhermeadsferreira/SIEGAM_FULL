package org.ufg.dto;

import jakarta.validation.Valid;
import lombok.Data;

import java.util.List;
import java.util.UUID;

@Data
public class PerfilUsuarioDTO {
    @Valid
    private List<PreferenciaRequestDTO> preferencias;
    private List<UUID> idsCanaisPreferidos;
}
