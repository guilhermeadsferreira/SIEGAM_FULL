package org.ufg.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UsuarioDetalhadoResponseDTO {

    private UUID id;
    private String nome;
    private String email;
    private String whatsapp;
    private LocalDateTime dataCriacao;
    private LocalDate dataUltimaEdicao;
    private String nivelAcesso;
    private UUID cidadeId;
    private String cidadeNome;
    private UUID EventoId;
    private String EventoNome;
    private BigDecimal valor;
    private Boolean personalizavel;
    private List<CanalResponseDTO> canaisPreferidos;
}