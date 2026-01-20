package org.ufg.service;

import jakarta.ws.rs.NotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.ufg.dto.EventoRequestDTO;
import org.ufg.dto.EventoResponseDTO;
import org.ufg.entity.Evento;
import org.ufg.mapper.EventoMapper;
import org.ufg.repository.EventoRepository;

import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class EventoServiceTest {

    @Mock
    EventoRepository eventoRepository;

    @Mock
    EventoMapper eventoMapper;

    @InjectMocks
    EventoService eventoService;

    private UUID eventoId;
    private Evento eventoEntity;
    private EventoRequestDTO eventoRequestDTO;
    private EventoResponseDTO eventoResponseDTO;

    @BeforeEach
    void setUp() {
        eventoId = UUID.randomUUID();

        eventoRequestDTO = new EventoRequestDTO();
        eventoRequestDTO.setNomeEvento("Chuva");

        eventoEntity = new Evento();
        eventoEntity.id = eventoId;
        eventoEntity.nomeEvento = "Chuva";

        eventoResponseDTO = new EventoResponseDTO();
        eventoResponseDTO.setId(eventoId);
        eventoResponseDTO.setNomeEvento("Chuva");
    }

    @Test
    @DisplayName("Deve criar evento com sucesso quando o nome não existe")
    void createEvento_Success() {
        when(eventoRepository.findByNomeEvento("Chuva")).thenReturn(Optional.empty());
        when(eventoMapper.toEntity(eventoRequestDTO)).thenReturn(eventoEntity);
        when(eventoMapper.toResponseDTO(eventoEntity)).thenReturn(eventoResponseDTO);

        EventoResponseDTO result = eventoService.createEvento(eventoRequestDTO);

        assertNotNull(result);
        assertEquals("Chuva", result.getNomeEvento());

        verify(eventoRepository, times(1)).persist(eventoEntity);
    }

    @Test
    @DisplayName("Deve lançar exceção ao tentar criar evento com nome duplicado")
    void createEvento_DuplicateName_ThrowsException() {
        when(eventoRepository.findByNomeEvento("Chuva")).thenReturn(Optional.of(eventoEntity));

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> {
            eventoService.createEvento(eventoRequestDTO);
        });

        assertEquals("Evento com este nome já existe.", exception.getMessage());

        verify(eventoRepository, never()).persist(any(Evento.class));
    }

    @Test
    @DisplayName("Deve retornar lista de eventos")
    void findAllEventos_Success() {
        List<Evento> listaEntidades = List.of(eventoEntity);
        List<EventoResponseDTO> listaDtos = List.of(eventoResponseDTO);

        when(eventoRepository.listAll()).thenReturn(listaEntidades);
        when(eventoMapper.toResponseDTOList(listaEntidades)).thenReturn(listaDtos);

        List<EventoResponseDTO> result = eventoService.findAllEventos();

        assertFalse(result.isEmpty());
        assertEquals(1, result.size());
        assertEquals(eventoId, result.get(0).getId());
    }

    @Test
    @DisplayName("Deve retornar lista vazia se não houver eventos")
    void findAllEventos_Empty() {
        when(eventoRepository.listAll()).thenReturn(Collections.emptyList());
        when(eventoMapper.toResponseDTOList(Collections.emptyList())).thenReturn(Collections.emptyList());

        List<EventoResponseDTO> result = eventoService.findAllEventos();

        assertTrue(result.isEmpty());
    }

    @Test
    @DisplayName("Deve retornar evento por ID com sucesso")
    void findEventoById_Success() {
        when(eventoRepository.findByIdOptional(eventoId)).thenReturn(Optional.of(eventoEntity));
        when(eventoMapper.toResponseDTO(eventoEntity)).thenReturn(eventoResponseDTO);

        EventoResponseDTO result = eventoService.findEventoById(eventoId);

        assertNotNull(result);
        assertEquals(eventoId, result.getId());
    }

    @Test
    @DisplayName("Deve lançar NotFoundException ao buscar ID inexistente")
    void findEventoById_NotFound() {
        when(eventoRepository.findByIdOptional(eventoId)).thenReturn(Optional.empty());

        NotFoundException exception = assertThrows(NotFoundException.class, () -> {
            eventoService.findEventoById(eventoId);
        });

        assertTrue(exception.getMessage().contains("Evento não encontrado com o ID"));
    }

    @Test
    @DisplayName("Deve atualizar evento com sucesso")
    void updateEvento_Success() {
        when(eventoRepository.findByIdOptional(eventoId)).thenReturn(Optional.of(eventoEntity));
        when(eventoRepository.findByNomeEvento(eventoRequestDTO.getNomeEvento())).thenReturn(Optional.empty());
        when(eventoMapper.toResponseDTO(eventoEntity)).thenReturn(eventoResponseDTO);

        doNothing().when(eventoMapper).updateEntityFromDto(eventoRequestDTO, eventoEntity);

        EventoResponseDTO result = eventoService.updateEvento(eventoId, eventoRequestDTO);

        assertNotNull(result);
        verify(eventoMapper, times(1)).updateEntityFromDto(eventoRequestDTO, eventoEntity);
    }

    @Test
    @DisplayName("Deve lançar NotFoundException ao tentar atualizar ID inexistente")
    void updateEvento_NotFound() {
        when(eventoRepository.findByIdOptional(eventoId)).thenReturn(Optional.empty());

        assertThrows(NotFoundException.class, () -> {
            eventoService.updateEvento(eventoId, eventoRequestDTO);
        });

        verify(eventoMapper, never()).updateEntityFromDto(any(), any());
    }

    @Test
    @DisplayName("Deve lançar exceção ao atualizar para um nome que já existe em outro evento")
    void updateEvento_DuplicateName_ThrowsException() {
        when(eventoRepository.findByIdOptional(eventoId)).thenReturn(Optional.of(eventoEntity));

        Evento outroEvento = new Evento();
        outroEvento.id = UUID.randomUUID();
        outroEvento.nomeEvento = "Chuva";

        when(eventoRepository.findByNomeEvento("Chuva")).thenReturn(Optional.of(outroEvento));

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> {
            eventoService.updateEvento(eventoId, eventoRequestDTO);
        });

        assertEquals("Outro evento com este nome já existe.", exception.getMessage());
        verify(eventoMapper, never()).updateEntityFromDto(any(), any());
    }

    @Test
    @DisplayName("Deve permitir atualizar se o nome for igual mas pertencer ao mesmo evento")
    void updateEvento_SameNameSameId_Success() {
        when(eventoRepository.findByIdOptional(eventoId)).thenReturn(Optional.of(eventoEntity));
        when(eventoRepository.findByNomeEvento("Chuva")).thenReturn(Optional.of(eventoEntity));
        when(eventoMapper.toResponseDTO(eventoEntity)).thenReturn(eventoResponseDTO);

        EventoResponseDTO result = eventoService.updateEvento(eventoId, eventoRequestDTO);

        assertNotNull(result);
        verify(eventoMapper, times(1)).updateEntityFromDto(eventoRequestDTO, eventoEntity);
    }
}