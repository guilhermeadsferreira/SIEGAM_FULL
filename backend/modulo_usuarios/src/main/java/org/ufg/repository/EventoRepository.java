package org.ufg.repository;

import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import org.ufg.entity.Evento;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.Optional;
import java.util.UUID;

@ApplicationScoped
public class EventoRepository implements PanacheRepositoryBase<Evento, UUID> {
    public long countPersonalizaveis() {
        return count("personalizavel", true);
    }
    public Optional<Evento> findByNomeEvento(String nome) {
        return find("nomeEvento", nome).firstResultOptional();
    }
}