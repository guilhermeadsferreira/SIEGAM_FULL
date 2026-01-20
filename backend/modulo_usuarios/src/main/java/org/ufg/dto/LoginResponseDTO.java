package org.ufg.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Data
@AllArgsConstructor
public class LoginResponseDTO {
    private String token;
    private UUID id;
    private String nivelAcesso;
}