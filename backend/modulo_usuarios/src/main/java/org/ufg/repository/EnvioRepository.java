package org.ufg.repository;

import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import org.ufg.entity.Envio;
import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.UUID;

@ApplicationScoped
public class EnvioRepository implements PanacheRepositoryBase<Envio, UUID> {

}