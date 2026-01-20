package org.ufg.entity;

import io.quarkus.hibernate.orm.panache.PanacheEntityBase;
import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "usuarios")
@Data
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = false)
public class Usuario extends PanacheEntityBase {

    @Id
    @GeneratedValue(generator = "UUID")
    public UUID id;

    @Column(name = "nome", nullable = false, length = 100)
    public String nome;

    @Column(name = "email", length = 45)
    public String email;

    @Column(name = "whatsapp", length = 45)
    public String whatsapp;

    @Column(name = "data_criacao", nullable = false)
    public LocalDateTime dataCriacao;

    @Column(name = "data_ultima_edicao", nullable = false)
    public LocalDate dataUltimaEdicao; // O script usa DATE

    @Column(name = "senha", nullable = false, length = 100)
    public String senha;

    @Column(name = "login_token", length = 1024)
    public String loginToken;

    @Column(name = "nivel_acesso", nullable = false, length = 45)
    public String nivelAcesso;

    @OneToMany(mappedBy = "usuario", fetch = FetchType.LAZY)
    public List<Preferencia> preferencias;

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
            name = "usuario_canais_preferidos",
            joinColumns = @JoinColumn(name = "id_usuario"),
            inverseJoinColumns = @JoinColumn(name = "id_canal")
    )
    public List<Canal> canaisPreferidos = new ArrayList<>();
}
