package org.ufg.entity;

import io.quarkus.hibernate.orm.panache.PanacheEntityBase;
import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.UUID;

@Entity
@Table(name = "avisos")
@Data
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = false)
public class Aviso extends PanacheEntityBase {

    @Id
    @GeneratedValue(generator = "UUID")
    public UUID id;

    @ManyToOne
    @JoinColumn(name = "id_evento", nullable = false) // FK para EVENTOS
    public Evento evento;

    @Column(name = "valor", precision = 15, scale = 6)
    public BigDecimal valor;

    @Column(name = "data_geracao", nullable = false)
    public LocalDate dataGeracao;

    @Column(name = "data_referencia", nullable = false)
    public LocalDate dataReferencia;

    @ManyToOne
    @JoinColumn(name = "id_cidade", nullable = false) // FK para CIDADES
    public Cidade cidade;

    @Column(name = "valor_limite", precision = 15, scale = 6)
    public BigDecimal valorLimite;

    @Column(name = "unidade_medida", nullable = false, length = 45)
    public String unidadeMedida;

    @Column(name = "diferenca", nullable = false, precision = 15, scale = 6)
    public BigDecimal diferenca;

    @Column(name = "horario")
    public LocalTime horario; // O script usa TIME

    @Column(name = "segundos", precision = 15, scale = 6)
    public BigDecimal segundos;
}