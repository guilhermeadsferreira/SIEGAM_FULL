package org.ufg.service;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.NotFoundException;
import org.jboss.logging.Logger;
import org.ufg.dto.EventoRequestDTO;
import org.ufg.dto.EventoResponseDTO;
import org.ufg.entity.Evento;
import org.ufg.mapper.EventoMapper;
import org.ufg.repository.EventoRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@ApplicationScoped
public class EventoService {

    private static final Logger LOG = Logger.getLogger(EventoService.class);

    @Inject
    EventoRepository eventoRepository;

    @Inject
    EventoMapper eventoMapper;

    @Transactional
    public EventoResponseDTO createEvento(EventoRequestDTO dto) {
        LOG.infof("Service: Criando novo evento: %s", dto.getNomeEvento());

        if (eventoRepository.findByNomeEvento(dto.getNomeEvento()).isPresent()) {
            throw new IllegalArgumentException("Evento com este nome já existe.");
        }

        Evento evento = eventoMapper.toEntity(dto);
        eventoRepository.persist(evento);
        return eventoMapper.toResponseDTO(evento);
    }

    public List<EventoResponseDTO> findAllEventos() {
        LOG.info("Service: Buscando todos os eventos.");
        List<Evento> entities = eventoRepository.listAll();
        return eventoMapper.toResponseDTOList(entities);
    }

    public EventoResponseDTO findEventoById(UUID id) {
        LOG.infof("Service: Buscando evento por ID: %s", id);
        Evento evento = eventoRepository.findByIdOptional(id)
                .orElseThrow(() -> new NotFoundException("Evento não encontrado com o ID: " + id));
        return eventoMapper.toResponseDTO(evento);
    }

    @Transactional
    public EventoResponseDTO updateEvento(UUID id, EventoRequestDTO dto) {
        LOG.infof("Service: Atualizando evento ID: %s", id);

        Evento evento = eventoRepository.findByIdOptional(id)
                .orElseThrow(() -> new NotFoundException("Evento não encontrado para atualização com o ID: " + id));

        Optional<Evento> existingByName = eventoRepository.findByNomeEvento(dto.getNomeEvento());
        if (existingByName.isPresent() && !existingByName.get().id.equals(id)) {
            throw new IllegalArgumentException("Outro evento com este nome já existe.");
        }

        eventoMapper.updateEntityFromDto(dto, evento);

        return eventoMapper.toResponseDTO(evento);
    }
}