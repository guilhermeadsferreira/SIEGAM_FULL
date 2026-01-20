package org.ufg.service;

import jakarta.ws.rs.NotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.ufg.dto.CidadeBulkRequestDTO;
import org.ufg.dto.CidadeRequestDTO;
import org.ufg.dto.CidadeResponseDTO;
import org.ufg.entity.Cidade;
import org.ufg.mapper.CidadeMapper;
import org.ufg.repository.CidadeRepository;

import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CidadeServiceTest {

    @Mock
    CidadeRepository cidadeRepository;

    @Mock
    CidadeMapper cidadeMapper;

    @InjectMocks
    CidadeService cidadeService;

    private UUID cidadeId;
    private Cidade cidadeEntity;
    private CidadeRequestDTO cidadeRequestDTO;
    private CidadeResponseDTO cidadeResponseDTO;

    @BeforeEach
    void setUp() {
        cidadeId = UUID.randomUUID();

        cidadeRequestDTO = new CidadeRequestDTO();
        cidadeRequestDTO.setNome("Goiânia");

        cidadeEntity = new Cidade();
        cidadeEntity.id = cidadeId;
        cidadeEntity.nome = "Goiânia";

        cidadeResponseDTO = new CidadeResponseDTO();
        cidadeResponseDTO.setId(cidadeId);
        cidadeResponseDTO.setNome("Goiânia");
    }

    @Test
    @DisplayName("Deve criar cidade com sucesso quando o nome não existe")
    void createCidade_Success() {
        when(cidadeRepository.findByNome("Goiânia")).thenReturn(Optional.empty());
        when(cidadeMapper.toEntity(cidadeRequestDTO)).thenReturn(cidadeEntity);
        when(cidadeMapper.toResponseDTO(cidadeEntity)).thenReturn(cidadeResponseDTO);

        CidadeResponseDTO result = cidadeService.createCidade(cidadeRequestDTO);

        assertNotNull(result);
        assertEquals("Goiânia", result.getNome());

        verify(cidadeRepository, times(1)).persist(cidadeEntity);
    }

    @Test
    @DisplayName("Deve lançar exceção ao tentar criar cidade com nome duplicado")
    void createCidade_DuplicateName_ThrowsException() {
        when(cidadeRepository.findByNome("Goiânia")).thenReturn(Optional.of(cidadeEntity));

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> {
            cidadeService.createCidade(cidadeRequestDTO);
        });

        assertEquals("Cidade com este nome já existe.", exception.getMessage());

        verify(cidadeRepository, never()).persist(any(Cidade.class));
    }

    @Test
    @DisplayName("Deve criar cidades em lote com sucesso")
    void createCidadesBulk_Success() {
        CidadeBulkRequestDTO bulkDto = new CidadeBulkRequestDTO();
        bulkDto.setCidades(List.of(cidadeRequestDTO));

        List<Cidade> listaEntidades = List.of(cidadeEntity);
        List<CidadeResponseDTO> listaResponse = List.of(cidadeResponseDTO);

        when(cidadeMapper.toEntityList(bulkDto.getCidades())).thenReturn(listaEntidades);
        when(cidadeRepository.findByNome("Goiânia")).thenReturn(Optional.empty());
        when(cidadeMapper.toResponseDTOList(listaEntidades)).thenReturn(listaResponse);

        List<CidadeResponseDTO> result = cidadeService.createCidadesBulk(bulkDto);

        assertNotNull(result);
        assertEquals(1, result.size());
        verify(cidadeRepository, times(1)).persist(listaEntidades);
    }

    @Test
    @DisplayName("Deve lançar exceção se uma cidade do lote já existir")
    void createCidadesBulk_Duplicate_ThrowsException() {
        CidadeBulkRequestDTO bulkDto = new CidadeBulkRequestDTO();
        bulkDto.setCidades(List.of(cidadeRequestDTO));

        List<Cidade> listaEntidades = List.of(cidadeEntity);

        when(cidadeMapper.toEntityList(bulkDto.getCidades())).thenReturn(listaEntidades);
        when(cidadeRepository.findByNome("Goiânia")).thenReturn(Optional.of(cidadeEntity));

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> {
            cidadeService.createCidadesBulk(bulkDto);
        });

        assertTrue(exception.getMessage().contains("As seguintes cidades já existem"));
        verify(cidadeRepository, never()).persist(any(List.class));
    }

    @Test
    @DisplayName("Deve retornar lista de cidades")
    void findAllCidades_Success() {
        List<Cidade> listaEntidades = List.of(cidadeEntity);
        List<CidadeResponseDTO> listaDtos = List.of(cidadeResponseDTO);

        when(cidadeRepository.listAll()).thenReturn(listaEntidades);
        when(cidadeMapper.toResponseDTOList(listaEntidades)).thenReturn(listaDtos);

        List<CidadeResponseDTO> result = cidadeService.findAllCidades();

        assertFalse(result.isEmpty());
        assertEquals(1, result.size());
    }

    @Test
    @DisplayName("Deve retornar cidade por ID com sucesso")
    void findCidadeById_Success() {
        when(cidadeRepository.findByIdOptional(cidadeId)).thenReturn(Optional.of(cidadeEntity));
        when(cidadeMapper.toResponseDTO(cidadeEntity)).thenReturn(cidadeResponseDTO);

        CidadeResponseDTO result = cidadeService.findCidadeById(cidadeId);

        assertNotNull(result);
        assertEquals(cidadeId, result.getId());
    }

    @Test
    @DisplayName("Deve lançar NotFoundException ao buscar ID inexistente")
    void findCidadeById_NotFound() {
        when(cidadeRepository.findByIdOptional(cidadeId)).thenReturn(Optional.empty());

        NotFoundException exception = assertThrows(NotFoundException.class, () -> {
            cidadeService.findCidadeById(cidadeId);
        });

        assertTrue(exception.getMessage().contains("Cidade não encontrada com o ID"));
    }

    @Test
    @DisplayName("Deve atualizar cidade com sucesso")
    void updateCidade_Success() {
        when(cidadeRepository.findByNome(cidadeRequestDTO.getNome())).thenReturn(Optional.empty());
        when(cidadeRepository.findByIdOptional(cidadeId)).thenReturn(Optional.of(cidadeEntity));
        when(cidadeMapper.toResponseDTO(cidadeEntity)).thenReturn(cidadeResponseDTO);

        doNothing().when(cidadeMapper).updateEntityFromDto(cidadeRequestDTO, cidadeEntity);

        CidadeResponseDTO result = cidadeService.updateCidade(cidadeId, cidadeRequestDTO);

        assertNotNull(result);
        verify(cidadeMapper, times(1)).updateEntityFromDto(cidadeRequestDTO, cidadeEntity);
    }

    @Test
    @DisplayName("Deve lançar exceção ao atualizar para um nome que já existe em outra cidade")
    void updateCidade_DuplicateName_ThrowsException() {
        Cidade outraCidade = new Cidade();
        outraCidade.id = UUID.randomUUID();
        outraCidade.nome = "Goiânia";

        when(cidadeRepository.findByNome("Goiânia")).thenReturn(Optional.of(outraCidade));

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> {
            cidadeService.updateCidade(cidadeId, cidadeRequestDTO);
        });

        assertEquals("Outra cidade com este nome já existe.", exception.getMessage());
        verify(cidadeMapper, never()).updateEntityFromDto(any(), any());
    }

    @Test
    @DisplayName("Deve permitir atualizar se o nome for igual mas pertencer à mesma cidade")
    void updateCidade_SameNameSameId_Success() {
        when(cidadeRepository.findByNome("Goiânia")).thenReturn(Optional.of(cidadeEntity));
        when(cidadeRepository.findByIdOptional(cidadeId)).thenReturn(Optional.of(cidadeEntity));
        when(cidadeMapper.toResponseDTO(cidadeEntity)).thenReturn(cidadeResponseDTO);

        CidadeResponseDTO result = cidadeService.updateCidade(cidadeId, cidadeRequestDTO);

        assertNotNull(result);
        verify(cidadeMapper, times(1)).updateEntityFromDto(cidadeRequestDTO, cidadeEntity);
    }
}