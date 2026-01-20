package org.ufg.repository;

import org.ufg.entity.Cidade;
import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.Optional;
import java.util.UUID;

@ApplicationScoped
public class CidadeRepository implements PanacheRepositoryBase<Cidade, UUID> {

    public Optional<Cidade> findByNome(String nome) {
        return find("nome", nome).firstResultOptional();
    }
}