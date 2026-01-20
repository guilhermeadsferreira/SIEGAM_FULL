package org.ufg.repository;

import org.ufg.entity.Preferencia;
import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import io.quarkus.panache.common.Parameters; // ✅ IMPORT NECESSÁRIO
import jakarta.enterprise.context.ApplicationScoped;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@ApplicationScoped
public class PreferenciaRepository implements PanacheRepositoryBase<Preferencia, UUID> {
    public Optional<Preferencia> findByUsuarioEventoCidade(UUID idUsuario, UUID idEvento, UUID idCidade) {

        String query = "usuario.id = :idUsuario and evento.id = :idEvento and cidade.id = :idCidade";

        return find(query,
                Parameters.with("idUsuario", idUsuario)
                        .and("idEvento", idEvento)
                        .and("idCidade", idCidade))
                .firstResultOptional();
    }

    public List<Preferencia> findByCidadeIdAndEventoIds(UUID idCidade, List<UUID> idsEventos) {
        String hqlQuery = "FROM Preferencia p " +
                "JOIN FETCH p.usuario " +
                "JOIN FETCH p.evento " +
                "WHERE p.cidade.id = :idCidade AND p.evento.id IN :idsEventos";

        return find(hqlQuery,
                Parameters.with("idCidade", idCidade)
                        .and("idsEventos", idsEventos))
                .list();
    }
}