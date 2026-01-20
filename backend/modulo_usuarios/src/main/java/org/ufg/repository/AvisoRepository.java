package org.ufg.repository;

import io.quarkus.hibernate.orm.panache.PanacheQuery;
import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import org.ufg.dto.EstatisticaDTO;
import org.ufg.entity.Aviso;
import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@ApplicationScoped
public class AvisoRepository implements PanacheRepositoryBase<Aviso, UUID> {
    public PanacheQuery<Aviso> buscarComFiltros(LocalDate data, UUID idEvento, UUID idCidade) {
        StringBuilder query = new StringBuilder("1=1");
        Map<String, Object> params = new HashMap<>();

        if (data != null) {
            query.append(" AND dataReferencia = :data");
            params.put("data", data);
        }

        if (idEvento != null) {
            query.append(" AND evento.id = :idEvento");
            params.put("idEvento", idEvento);
        }

        if (idCidade != null) {
            query.append(" AND cidade.id = :idCidade");
            params.put("idCidade", idCidade);
        }

        query.append(" ORDER BY dataGeracao DESC");

        return find(query.toString(), params);
    }

    public List<Aviso> listAllToday() {
        LocalDate today = LocalDate.now();
        return find("dataGeracao = ?1", today).list();
    }

    public List<EstatisticaDTO> countPorCidade() {
        return find("SELECT a.cidade.nome, COUNT(a) FROM Aviso a GROUP BY a.cidade.nome ORDER BY COUNT(a) DESC")
                .project(EstatisticaDTO.class) // O Panache mapeia direto pro DTO se o construtor bater
                .page(0, 5) // Pega só o Top 5
                .list();
    }

    public List<EstatisticaDTO> countPorEvento() {
        return find("SELECT a.evento.nomeEvento, COUNT(a) FROM Aviso a GROUP BY a.evento.nomeEvento")
                .project(EstatisticaDTO.class)
                .list();
    }

    public List<EstatisticaDTO> countUltimos7Dias() {
        return find("SELECT cast(a.dataReferencia as string), COUNT(a) FROM Aviso a " +
                        "WHERE a.dataReferencia >= ?1 GROUP BY a.dataReferencia ORDER BY a.dataReferencia ASC",
                LocalDate.now().minusDays(7))
                .project(EstatisticaDTO.class)
                .list();
    }
}