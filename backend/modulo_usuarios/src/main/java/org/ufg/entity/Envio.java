package org.ufg.entity;

import io.quarkus.hibernate.orm.panache.PanacheEntityBase;
import jakarta.persistence.*;
import lombok.*;
import java.util.UUID;

@Entity
@Table(name = "envios")
@Data
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = false)
public class Envio extends PanacheEntityBase {

    @Id
    @GeneratedValue(generator = "UUID")
    public UUID id;

    @ManyToOne
    @JoinColumn(name = "id_canal", nullable = false) // FK para CANAIS
    public Canal canal;

    @ManyToOne
    @JoinColumn(name = "id_aviso", nullable = false) // FK para AVISOS
    public Aviso aviso;

    @ManyToOne
    @JoinColumn(name = "id_usuario_destinatario", nullable = false) // FK para USUARIOS
    public Usuario usuarioDestinatario;

    @ManyToOne
    @JoinColumn(name = "id_status", nullable = false) // FK para POSSIVEIS_STATUS
    public PossivelStatus status;
}