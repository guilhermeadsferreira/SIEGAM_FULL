package org.ufg.repository;

import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import org.ufg.entity.PossivelStatus;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.Optional;
import java.util.UUID;

@ApplicationScoped
public class PossivelStatusRepository implements PanacheRepositoryBase<PossivelStatus, UUID> {
    public Optional<PossivelStatus> findByNomeAndCanal(String nome, UUID idCanal) {
        return find("nomeStatus = ?1 and canal.id = ?2", nome, idCanal).firstResultOptional();
    }

}