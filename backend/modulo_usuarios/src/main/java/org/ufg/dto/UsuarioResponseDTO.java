package org.ufg.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UsuarioResponseDTO {

    private UUID id;
    private String nome;
    private String email;
    private String whatsapp;
    private LocalDateTime dataCriacao;
    private LocalDate dataUltimaEdicao;
    private String nivelAcesso;
    private List<CanalResponseDTO> canaisPreferidos;
}