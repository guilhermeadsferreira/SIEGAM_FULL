package org.ufg.service;

import jakarta.ws.rs.NotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.ufg.dto.CanalRequestDTO;
import org.ufg.dto.CanalResponseDTO;
import org.ufg.entity.Canal;
import org.ufg.mapper.CanalMapper;
import org.ufg.repository.CanalRepository;

import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CanalServiceTest {

    @Mock
    CanalRepository canalRepository;

    @Mock
    CanalMapper canalMapper;

    @InjectMocks
    CanalService canalService;

    private UUID canalId;
    private Canal canalEntity;
    private CanalRequestDTO canalRequestDTO;
    private CanalResponseDTO canalResponseDTO;

    @BeforeEach
    void setUp() {
        canalId = UUID.randomUUID();

        canalRequestDTO = new CanalRequestDTO();
        canalRequestDTO.setNomeCanal("WhatsApp");

        canalEntity = new Canal();
        canalEntity.id = canalId;
        canalEntity.nomeCanal = "WhatsApp";

        canalResponseDTO = new CanalResponseDTO();
        canalResponseDTO.setId(canalId);
        canalResponseDTO.setNomeCanal("WhatsApp");
    }


    @Test
    @DisplayName("Deve criar canal com sucesso quando o nome não existe")
    void createCanal_Success() {
        when(canalRepository.findByNomeCanal("WhatsApp")).thenReturn(Optional.empty());
        when(canalMapper.toEntity(canalRequestDTO)).thenReturn(canalEntity);
        when(canalMapper.toResponseDTO(canalEntity)).thenReturn(canalResponseDTO);

        CanalResponseDTO result = canalService.createCanal(canalRequestDTO);

        assertNotNull(result);
        assertEquals("WhatsApp", result.getNomeCanal());

        verify(canalRepository, times(1)).persist(canalEntity);
        assertNotNull(canalEntity.dataInclusao);
    }

    @Test
    @DisplayName("Deve lançar exceção ao tentar criar canal com nome duplicado")
    void createCanal_DuplicateName_ThrowsException() {
        when(canalRepository.findByNomeCanal("WhatsApp")).thenReturn(Optional.of(canalEntity));

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> {
            canalService.createCanal(canalRequestDTO);
        });

        assertEquals("Canal com este nome já existe.", exception.getMessage());

        verify(canalRepository, never()).persist(any(Canal.class));
    }

    @Test
    @DisplayName("Deve retornar lista de canais")
    void findAllCanais_Success() {
        List<Canal> listaEntidades = List.of(canalEntity);
        List<CanalResponseDTO> listaDtos = List.of(canalResponseDTO);

        when(canalRepository.listAll()).thenReturn(listaEntidades);
        when(canalMapper.toResponseDTOList(listaEntidades)).thenReturn(listaDtos);

        List<CanalResponseDTO> result = canalService.findAllCanais();

        assertFalse(result.isEmpty());
        assertEquals(1, result.size());
        assertEquals(canalId, result.get(0).getId());
    }

    @Test
    @DisplayName("Deve retornar lista vazia se não houver canais")
    void findAllCanais_Empty() {
        when(canalRepository.listAll()).thenReturn(Collections.emptyList());
        when(canalMapper.toResponseDTOList(Collections.emptyList())).thenReturn(Collections.emptyList());

        List<CanalResponseDTO> result = canalService.findAllCanais();

        assertTrue(result.isEmpty());
    }

    @Test
    @DisplayName("Deve retornar canal por ID com sucesso")
    void findCanalById_Success() {
        when(canalRepository.findByIdOptional(canalId)).thenReturn(Optional.of(canalEntity));
        when(canalMapper.toResponseDTO(canalEntity)).thenReturn(canalResponseDTO);

        CanalResponseDTO result = canalService.findCanalById(canalId);

        assertNotNull(result);
        assertEquals(canalId, result.getId());
    }

    @Test
    @DisplayName("Deve lançar NotFoundException ao buscar ID inexistente")
    void findCanalById_NotFound() {
        when(canalRepository.findByIdOptional(canalId)).thenReturn(Optional.empty());

        NotFoundException exception = assertThrows(NotFoundException.class, () -> {
            canalService.findCanalById(canalId);
        });

        assertTrue(exception.getMessage().contains("Canal não encontrado com o ID"));
    }


    @Test
    @DisplayName("Deve atualizar canal com sucesso")
    void updateCanal_Success() {
        when(canalRepository.findByIdOptional(canalId)).thenReturn(Optional.of(canalEntity));
        when(canalMapper.toResponseDTO(canalEntity)).thenReturn(canalResponseDTO);

        doNothing().when(canalMapper).updateEntityFromDto(canalRequestDTO, canalEntity);

        CanalResponseDTO result = canalService.updateCanal(canalId, canalRequestDTO);

        assertNotNull(result);

        verify(canalMapper, times(1)).updateEntityFromDto(canalRequestDTO, canalEntity);
    }

    @Test
    @DisplayName("Deve lançar NotFoundException ao tentar atualizar ID inexistente")
    void updateCanal_NotFound() {
        when(canalRepository.findByIdOptional(canalId)).thenReturn(Optional.empty());

        assertThrows(NotFoundException.class, () -> {
            canalService.updateCanal(canalId, canalRequestDTO);
        });

        verify(canalMapper, never()).updateEntityFromDto(any(), any());
    }
}