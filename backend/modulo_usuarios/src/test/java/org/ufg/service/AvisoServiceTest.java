package org.ufg.service;

import io.quarkus.hibernate.orm.panache.PanacheQuery;
import io.quarkus.panache.common.Page;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.ufg.dto.AvisoDTO;
import org.ufg.dto.AvisoResponseDTO;
import org.ufg.dto.EstatisticaDTO;
import org.ufg.dto.PageDTO;
import org.ufg.entity.Aviso;
import org.ufg.mapper.AvisoMapper;
import org.ufg.repository.AvisoRepository;

import java.time.LocalDate;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AvisoServiceTest {

    @Mock
    AvisoRepository avisoRepository;

    @Mock
    AvisoMapper avisoMapper;

    @InjectMocks
    AvisoService avisoService;

    private Aviso avisoEntity;
    private AvisoDTO avisoDTO;
    private AvisoResponseDTO avisoResponseDTO;
    private UUID avisoId;

    @BeforeEach
    void setUp() {
        avisoId = UUID.randomUUID();

        avisoEntity = new Aviso();
        avisoEntity.setId(avisoId);

        avisoDTO = new AvisoDTO();

        avisoResponseDTO = new AvisoResponseDTO();
        avisoResponseDTO.setId(avisoId);
    }

    @Test
    @DisplayName("Deve criar um aviso com sucesso")
    void criarAvisoTest() {
        when(avisoMapper.toEntity(avisoDTO)).thenReturn(avisoEntity);
        when(avisoMapper.toResponseDTO(avisoEntity)).thenReturn(avisoResponseDTO);

        AvisoResponseDTO result = avisoService.criarAviso(avisoDTO);

        assertNotNull(result);
        assertEquals(avisoId, result.getId());

        verify(avisoRepository, times(1)).persist(avisoEntity);
        verify(avisoMapper, times(1)).toEntity(avisoDTO);
    }

    @Test
    @DisplayName("Deve buscar aviso por ID e encontrar")
    void buscarAvisoPorId_EncontradoTest() {
        when(avisoRepository.findById(avisoId)).thenReturn(avisoEntity);
        when(avisoMapper.toResponseDTO(avisoEntity)).thenReturn(avisoResponseDTO);

        AvisoResponseDTO result = avisoService.buscarAvisoPorId(avisoId);

        assertNotNull(result);
        assertEquals(avisoId, result.getId());
    }

    @Test
    @DisplayName("Deve retornar null ao buscar aviso por ID inexistente")
    void buscarAvisoPorId_NaoEncontradoTest() {
        // Arrange
        when(avisoRepository.findById(avisoId)).thenReturn(null);

        AvisoResponseDTO result = avisoService.buscarAvisoPorId(avisoId);

        assertNull(result);
        verify(avisoMapper, never()).toResponseDTO(any());
    }

    @Test
    @DisplayName("Deve listar todos os avisos")
    void listarTodosAvisosTest() {
        List<Aviso> listaEntidades = List.of(avisoEntity);
        when(avisoRepository.listAll()).thenReturn(listaEntidades);
        when(avisoMapper.toResponseDTO(avisoEntity)).thenReturn(avisoResponseDTO);

        List<AvisoResponseDTO> result = avisoService.listarTodosAvisos();

        assertFalse(result.isEmpty());
        assertEquals(1, result.size());
        assertEquals(avisoId, result.get(0).getId());
    }

    @Test
    @DisplayName("Deve processar lote de avisos corretamente")
    void processarLoteAvisosTest() {
        List<AvisoDTO> loteDTO = List.of(avisoDTO, avisoDTO); // 2 itens

        when(avisoMapper.toEntity(any(AvisoDTO.class))).thenReturn(avisoEntity);

        int qtdProcessada = avisoService.processarLoteAvisos(loteDTO);

        assertEquals(2, qtdProcessada);
        verify(avisoRepository, times(1)).persist(any(List.class));
    }

    @Test
    @DisplayName("Processar lote deve retornar 0 se a lista for vazia ou nula")
    void processarLoteAvisos_VazioTest() {
        int qtdNull = avisoService.processarLoteAvisos(null);
        int qtdVazio = avisoService.processarLoteAvisos(Collections.emptyList());

        assertEquals(0, qtdNull);
        assertEquals(0, qtdVazio);
        verify(avisoRepository, never()).persist(any(List.class));
    }

    @Test
    @DisplayName("Deve filtrar avisos com paginação corretamente")
    void filtrarAvisosTest() {
        LocalDate data = LocalDate.now();
        UUID idEvento = UUID.randomUUID();
        UUID idCidade = UUID.randomUUID();
        int page = 0;
        int size = 10;

        PanacheQuery<Aviso> queryMock = mock(PanacheQuery.class);

        when(avisoRepository.buscarComFiltros(data, idEvento, idCidade)).thenReturn(queryMock);

        when(queryMock.page(any(Page.class))).thenReturn(queryMock);

        when(queryMock.list()).thenReturn(List.of(avisoEntity));
        when(queryMock.count()).thenReturn(1L);
        when(queryMock.pageCount()).thenReturn(1);

        when(avisoMapper.toResponseDTO(avisoEntity)).thenReturn(avisoResponseDTO);

        PageDTO<AvisoResponseDTO> result = avisoService.filtrarAvisos(data, idEvento, idCidade, page, size);

        assertNotNull(result);
        assertEquals(1, result.getContent().size());


        ArgumentCaptor<Page> pageCaptor = ArgumentCaptor.forClass(Page.class);

        verify(queryMock).page(pageCaptor.capture());

        Page paginaCapturada = pageCaptor.getValue();
        assertEquals(page, paginaCapturada.index);
        assertEquals(size, paginaCapturada.size);
    }

    @Test
    @DisplayName("Deve retornar estatísticas de top cidades")
    void getTopCidadesTest() {
        // Arrange
        EstatisticaDTO est = new EstatisticaDTO("Goiânia", 10L);
        when(avisoRepository.countPorCidade()).thenReturn(List.of(est));

        // Act
        List<EstatisticaDTO> result = avisoService.getTopCidades();

        // Assert
        assertEquals(1, result.size());
        assertEquals("Goiânia", result.get(0).getLabel());
        verify(avisoRepository).countPorCidade();
    }
}