package org.ufg.entity;

import io.quarkus.hibernate.orm.panache.PanacheEntityBase;
import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "eventos")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = false)
public class Evento extends PanacheEntityBase {

    @Id
    @GeneratedValue(generator = "UUID")
    public UUID id;

    @Column(name = "nome_evento", nullable = false, length = 50)
    public String nomeEvento;

    @Column(name = "personalizavel", nullable = false)
    public Boolean personalizavel;

    @Column(name = "horario", nullable = false)
    public LocalDateTime horario; // O script usa TIMESTAMP
}