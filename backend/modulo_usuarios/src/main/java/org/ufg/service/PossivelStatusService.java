package org.ufg.service;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.NotFoundException;
import org.jboss.logging.Logger;
import org.ufg.dto.PossivelStatusRequestDTO;
import org.ufg.dto.PossivelStatusResponseDTO;
import org.ufg.entity.PossivelStatus;
import org.ufg.mapper.PossivelStatusMapper;
import org.ufg.repository.PossivelStatusRepository;

import java.util.List;
import java.util.UUID;

@ApplicationScoped
public class PossivelStatusService {

    private static final Logger LOG = Logger.getLogger(PossivelStatusService.class);

    @Inject
    PossivelStatusRepository statusRepository;

    @Inject
    PossivelStatusMapper statusMapper;

    @Transactional
    public PossivelStatusResponseDTO createStatus(PossivelStatusRequestDTO dto) {
        LOG.infof("Service: Criando novo status '%s' para Canal ID: %s", dto.getNomeStatus(), dto.getIdCanal());

        PossivelStatus status = statusMapper.toEntity(dto);

        if (status.canal == null) {
            throw new NotFoundException("Canal não encontrado com o ID: " + dto.getIdCanal());
        }

        if (statusRepository.findByNomeAndCanal(dto.getNomeStatus(), dto.getIdCanal()).isPresent()) {
            throw new IllegalArgumentException(
                    String.format("Status '%s' já existe para o Canal ID: %s.", dto.getNomeStatus(), dto.getIdCanal())
            );
        }

        statusRepository.persist(status);
        return statusMapper.toResponseDTO(status);
    }

    public List<PossivelStatusResponseDTO> findAllStatus() {
        LOG.info("Service: Buscando todos os possíveis status.");
        List<PossivelStatus> entities = statusRepository.listAll();
        return statusMapper.toResponseDTOList(entities);
    }

    public PossivelStatusResponseDTO findStatusById(UUID id) {
        LOG.infof("Service: Buscando status por ID: %s", id);
        PossivelStatus status = statusRepository.findByIdOptional(id)
                .orElseThrow(() -> new NotFoundException("Status não encontrado com o ID: " + id));
        return statusMapper.toResponseDTO(status);
    }
}