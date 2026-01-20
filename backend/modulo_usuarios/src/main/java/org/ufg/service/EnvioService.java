package org.ufg.service;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.NotFoundException;
import org.jboss.logging.Logger;
import org.ufg.dto.EnvioBulkRequestDTO;
import org.ufg.dto.EnvioRequestDTO;
import org.ufg.dto.EnvioResponseDTO;
import org.ufg.entity.Envio;
import org.ufg.mapper.EnvioMapper;
import org.ufg.repository.EnvioRepository;

import java.util.List;
import java.util.UUID;

@ApplicationScoped
public class EnvioService {

    private static final Logger LOG = Logger.getLogger(EnvioService.class);

    @Inject
    EnvioRepository envioRepository;

    @Inject
    EnvioMapper envioMapper;

    @Transactional
    public EnvioResponseDTO createEnvio(EnvioRequestDTO dto) {
        LOG.info("Service: Criando novo envio.");

        Envio envio = envioMapper.toEntity(dto);

        if (envio.canal == null || envio.aviso == null || envio.usuarioDestinatario == null || envio.status == null) {
            throw new NotFoundException("Uma ou mais entidades (Canal, Aviso, Usuário ou Status) não foram encontradas.");
        }

        envioRepository.persist(envio);
        return envioMapper.toResponseDTO(envio);
    }

    @Transactional
    public List<EnvioResponseDTO> createEnviosBulk(EnvioBulkRequestDTO bulkDto) {
        LOG.infof("Service: Criando %d envios em lote.", bulkDto.getEnvios().size());

        List<Envio> novosEnvios = envioMapper.toEntityList(bulkDto.getEnvios());

        for (Envio envio : novosEnvios) {
            if (envio.canal == null || envio.aviso == null || envio.usuarioDestinatario == null || envio.status == null) {
                throw new NotFoundException("Pelo menos um dos envios contém um ID de entidade (Canal, Aviso, Usuário ou Status) não encontrado.");
            }
        }

        envioRepository.persist(novosEnvios);

        return envioMapper.toResponseDTOList(novosEnvios);
    }


    public List<EnvioResponseDTO> findAllEnvios() {
        LOG.info("Service: Buscando todos os envios.");
        List<Envio> entities = envioRepository.listAll();
        return envioMapper.toResponseDTOList(entities);
    }

    public EnvioResponseDTO findEnvioById(UUID id) {
        LOG.infof("Service: Buscando envio por ID: %s", id);
        Envio envio = envioRepository.findByIdOptional(id)
                .orElseThrow(() -> new NotFoundException("Envio não encontrado com o ID: " + id));
        return envioMapper.toResponseDTO(envio);
    }
}