package org.ufg.service;

import jakarta.ws.rs.NotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.ufg.dto.EnvioBulkRequestDTO;
import org.ufg.dto.EnvioRequestDTO;
import org.ufg.dto.EnvioResponseDTO;
import org.ufg.entity.*;
import org.ufg.entity.PossivelStatus;
import org.ufg.mapper.EnvioMapper;
import org.ufg.repository.EnvioRepository;

import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class EnvioServiceTest {

    @Mock
    EnvioRepository envioRepository;

    @Mock
    EnvioMapper envioMapper;

    @InjectMocks
    EnvioService envioService;

    private UUID envioId;
    private Envio envioEntity;
    private EnvioRequestDTO envioRequestDTO;
    private EnvioResponseDTO envioResponseDTO;

    @BeforeEach
    void setUp() {
        envioId = UUID.randomUUID();

        envioRequestDTO = new EnvioRequestDTO();

        envioEntity = new Envio();
        envioEntity.id = envioId;

        envioEntity.canal = new Canal();
        envioEntity.aviso = new Aviso();
        envioEntity.usuarioDestinatario = new Usuario();
        envioEntity.status = new PossivelStatus();

        envioResponseDTO = new EnvioResponseDTO();
        envioResponseDTO.setId(envioId);
    }

    @Test
    @DisplayName("Deve criar envio com sucesso quando todas as entidades relacionadas existem")
    void createEnvio_Success() {
        when(envioMapper.toEntity(envioRequestDTO)).thenReturn(envioEntity);
        when(envioMapper.toResponseDTO(envioEntity)).thenReturn(envioResponseDTO);

        EnvioResponseDTO result = envioService.createEnvio(envioRequestDTO);

        assertNotNull(result);
        assertEquals(envioId, result.getId());
        verify(envioRepository, times(1)).persist(envioEntity);
    }

    @Test
    @DisplayName("Deve lançar exceção ao criar envio se alguma entidade relacionada for nula")
    void createEnvio_MissingEntity_ThrowsException() {
        envioEntity.canal = null;

        when(envioMapper.toEntity(envioRequestDTO)).thenReturn(envioEntity);

        NotFoundException exception = assertThrows(NotFoundException.class, () -> {
            envioService.createEnvio(envioRequestDTO);
        });

        assertTrue(exception.getMessage().contains("Uma ou mais entidades"));
        verify(envioRepository, never()).persist(any(Envio.class));
    }

    @Test
    @DisplayName("Deve criar envios em lote com sucesso")
    void createEnviosBulk_Success() {
        EnvioBulkRequestDTO bulkDto = new EnvioBulkRequestDTO();
        bulkDto.setEnvios(List.of(envioRequestDTO));

        List<Envio> listaEntidades = List.of(envioEntity);
        List<EnvioResponseDTO> listaResponse = List.of(envioResponseDTO);

        when(envioMapper.toEntityList(bulkDto.getEnvios())).thenReturn(listaEntidades);
        when(envioMapper.toResponseDTOList(listaEntidades)).thenReturn(listaResponse);

        List<EnvioResponseDTO> result = envioService.createEnviosBulk(bulkDto);

        assertNotNull(result);
        assertEquals(1, result.size());
        verify(envioRepository, times(1)).persist(listaEntidades);
    }

    @Test
    @DisplayName("Deve lançar exceção no lote se algum envio tiver entidade nula")
    void createEnviosBulk_MissingEntity_ThrowsException() {
        EnvioBulkRequestDTO bulkDto = new EnvioBulkRequestDTO();
        bulkDto.setEnvios(List.of(envioRequestDTO));

        envioEntity.usuarioDestinatario = null;
        List<Envio> listaEntidades = List.of(envioEntity);

        when(envioMapper.toEntityList(bulkDto.getEnvios())).thenReturn(listaEntidades);

        NotFoundException exception = assertThrows(NotFoundException.class, () -> {
            envioService.createEnviosBulk(bulkDto);
        });

        assertTrue(exception.getMessage().contains("Pelo menos um dos envios contém um ID"));
        verify(envioRepository, never()).persist(any(List.class));
    }

    @Test
    @DisplayName("Deve retornar lista de envios")
    void findAllEnvios_Success() {
        List<Envio> listaEntidades = List.of(envioEntity);
        List<EnvioResponseDTO> listaDtos = List.of(envioResponseDTO);

        when(envioRepository.listAll()).thenReturn(listaEntidades);
        when(envioMapper.toResponseDTOList(listaEntidades)).thenReturn(listaDtos);

        List<EnvioResponseDTO> result = envioService.findAllEnvios();

        assertFalse(result.isEmpty());
        assertEquals(1, result.size());
    }

    @Test
    @DisplayName("Deve retornar envio por ID com sucesso")
    void findEnvioById_Success() {
        when(envioRepository.findByIdOptional(envioId)).thenReturn(Optional.of(envioEntity));
        when(envioMapper.toResponseDTO(envioEntity)).thenReturn(envioResponseDTO);

        EnvioResponseDTO result = envioService.findEnvioById(envioId);

        assertNotNull(result);
        assertEquals(envioId, result.getId());
    }

    @Test
    @DisplayName("Deve lançar NotFoundException ao buscar ID inexistente")
    void findEnvioById_NotFound() {
        when(envioRepository.findByIdOptional(envioId)).thenReturn(Optional.empty());

        NotFoundException exception = assertThrows(NotFoundException.class, () -> {
            envioService.findEnvioById(envioId);
        });

        assertTrue(exception.getMessage().contains("Envio não encontrado"));
    }
}