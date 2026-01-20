package org.ufg.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PossivelStatusResponseDTO {
    private UUID id;
    private String nomeStatus;
    private UUID idCanal;
}