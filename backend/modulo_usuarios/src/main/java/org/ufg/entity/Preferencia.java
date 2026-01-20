package org.ufg.entity;

import io.quarkus.hibernate.orm.panache.PanacheEntityBase;
import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

@Entity
@Table(name = "preferencias", indexes = {
        @Index(name = "idx_pref_evento_cidade", columnList = "id_evento, id_cidade"),
        @Index(name = "idx_pref_usuario", columnList = "id_usuario"),
        @Index(name = "idx_pref_evento", columnList = "id_evento"),
        @Index(name = "idx_pref_cidade", columnList = "id_cidade"),
        @Index(name = "idx_pref_canal", columnList = "id_canal")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = false)
public class Preferencia extends PanacheEntityBase {

    @Id
    @GeneratedValue(generator = "UUID")
    public UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "id_usuario", nullable = false) // FK para USUARIOS
    public Usuario usuario;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "id_evento", nullable = false) // FK para EVENTOS
    public Evento evento;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "id_cidade", nullable = false) // FK para CIDADES
    public Cidade cidade;

    @Column(name = "data_criacao", nullable = false)
    public LocalDate dataCriacao;

    @Column(name = "data_ultima_edicao", nullable = false)
    public LocalDate dataUltimaEdicao;

    @Column(name = "valor", precision = 15, scale = 6)
    public BigDecimal valor;

    @Column(name = "personalizavel")
    public Boolean personalizavel;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "id_canal", nullable = true) // FK para CANAIS
    public Canal canal;
}