package org.ufg.repository;

import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import org.ufg.entity.Canal;
import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

import java.util.Optional;
import java.util.UUID;

@ApplicationScoped
public class CanalRepository implements PanacheRepositoryBase<Canal, UUID> {
    public Optional<Canal> findByNomeCanal(String nome) {
        return find("nomeCanal", nome).firstResultOptional();
    }
}