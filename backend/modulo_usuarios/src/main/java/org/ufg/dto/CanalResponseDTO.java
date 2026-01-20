package org.ufg.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDate;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CanalResponseDTO {
    private UUID id;
    private String nomeCanal;
    private LocalDate dataInclusao;
}