package org.ufg.service;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.NotFoundException;
import org.jboss.logging.Logger;
import org.ufg.dto.CanalRequestDTO;
import org.ufg.dto.CanalResponseDTO;
import org.ufg.entity.Canal;
import org.ufg.mapper.CanalMapper;
import org.ufg.repository.CanalRepository;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@ApplicationScoped
public class CanalService {

    private static final Logger LOG = Logger.getLogger(CanalService.class);

    @Inject
    CanalRepository canalRepository;

    @Inject
    CanalMapper canalMapper;

    @Transactional
    public CanalResponseDTO createCanal(CanalRequestDTO dto) {
        LOG.infof("Service: Criando novo canal com nome: %s", dto.getNomeCanal());

        if (canalRepository.findByNomeCanal(dto.getNomeCanal()).isPresent()) {
            throw new IllegalArgumentException("Canal com este nome já existe.");
        }

        Canal canal = canalMapper.toEntity(dto);
        canal.dataInclusao = LocalDate.now();

        canalRepository.persist(canal);
        return canalMapper.toResponseDTO(canal);
    }

    public List<CanalResponseDTO> findAllCanais() {
        LOG.info("Service: Buscando todos os canais.");
        List<Canal> entities = canalRepository.listAll();
        return canalMapper.toResponseDTOList(entities);
    }

    public CanalResponseDTO findCanalById(UUID id) {
        LOG.infof("Service: Buscando canal por ID: %s", id);
        Canal canal = canalRepository.findByIdOptional(id)
                .orElseThrow(() -> new NotFoundException("Canal não encontrado com o ID: " + id));
        return canalMapper.toResponseDTO(canal);
    }

    @Transactional
    public CanalResponseDTO updateCanal(UUID id, CanalRequestDTO dto) {
        LOG.infof("Service: Atualizando canal ID: %s", id);

        Canal canal = canalRepository.findByIdOptional(id)
                .orElseThrow(() -> new NotFoundException("Canal não encontrado para atualização com o ID: " + id));

        canalMapper.updateEntityFromDto(dto, canal);

        return canalMapper.toResponseDTO(canal);
    }
}