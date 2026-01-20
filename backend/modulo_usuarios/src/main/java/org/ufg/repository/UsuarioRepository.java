package org.ufg.repository;

import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import io.quarkus.panache.common.Parameters;
import jakarta.enterprise.context.ApplicationScoped;
import org.ufg.entity.Usuario;

import java.util.List;
import java.util.UUID;

@ApplicationScoped
public class UsuarioRepository implements PanacheRepositoryBase<Usuario, UUID> {
    public Usuario findByEmail(String email) {
        return find("email", email).firstResult();
    }
    public Usuario findByWhatsapp(String whatsapp) {
        return find("whatsapp", whatsapp).firstResult();
    }

    public List<Usuario> findByPreferenciaEventoId(UUID idEvento) {
        String hqlQuery = "SELECT DISTINCT u FROM Usuario u JOIN u.preferencias p WHERE p.evento.id = :idEvento";

        return find(hqlQuery, Parameters.with("idEvento", idEvento)).list();
    }

    public List<Usuario> findByPreferenciaEventoIdAndCidadeId(UUID idEvento, UUID idCidade) {
        String hqlQuery = "SELECT DISTINCT u FROM Usuario u JOIN u.preferencias p " +
                "WHERE p.evento.id = :idEvento AND p.cidade.id = :idCidade";

        return find(hqlQuery,
                Parameters.with("idEvento", idEvento)
                        .and("idCidade", idCidade))
                .list();
    }

    public List<Usuario> findDetalhadoByEventoAndCidade(UUID idEvento, UUID idCidade) {

        String hql = """
            SELECT DISTINCT u
            FROM Usuario u
                JOIN FETCH u.preferencias p
                JOIN FETCH p.cidade c
            WHERE p.evento.id = :idEvento
            AND p.cidade.id = :idCidade
        """;

        return find(hql,
                Parameters.with("idEvento", idEvento)
                        .and("idCidade", idCidade))
                .list();
    }


    public List<Usuario> findAllWithCanais() {
        
        return find("SELECT DISTINCT u FROM Usuario u LEFT JOIN FETCH u.canaisPreferidos").list();
    }

    public Usuario findByIdWithCanais(UUID id) {
        return find("FROM Usuario u LEFT JOIN FETCH u.canaisPreferidos WHERE u.id = :id",
                Parameters.with("id", id))
                .firstResult();
    }
}
