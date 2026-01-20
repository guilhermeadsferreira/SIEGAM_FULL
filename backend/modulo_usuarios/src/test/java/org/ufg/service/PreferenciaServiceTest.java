package org.ufg.service;

import jakarta.ws.rs.ForbiddenException;
import jakarta.ws.rs.NotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.junit.jupiter.MockitoExtension;
import org.ufg.dto.PreferenciaRequestDTO;
import org.ufg.dto.PreferenciaResponseDTO;
import org.ufg.entity.Cidade;
import org.ufg.entity.Evento;
import org.ufg.entity.Preferencia;
import org.ufg.entity.Usuario;
import org.ufg.mapper.PreferenciaMapper;
import org.ufg.repository.CidadeRepository;
import org.ufg.repository.EventoRepository;
import org.ufg.repository.PreferenciaRepository;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PreferenciaServiceTest {

    @Mock
    PreferenciaRepository preferenciaRepository;

    @Mock
    PreferenciaMapper preferenciaMapper;

    @Mock
    EventoRepository eventoRepository;

    @Mock
    CidadeRepository cidadeRepository;

    @InjectMocks
    PreferenciaService preferenciaService;

    private UUID usuarioId;
    private UUID preferenciaId;
    private UUID eventoId;
    private UUID cidadeId;

    private Usuario usuarioEntity;
    private Evento eventoEntity;
    private Cidade cidadeEntity;
    private Preferencia preferenciaEntity;
    private PreferenciaRequestDTO preferenciaDTO;
    private PreferenciaResponseDTO preferenciaResponseDTO;

    @BeforeEach
    void setUp() {
        usuarioId = UUID.randomUUID();
        preferenciaId = UUID.randomUUID();
        eventoId = UUID.randomUUID();
        cidadeId = UUID.randomUUID();

        usuarioEntity = new Usuario();
        usuarioEntity.id = usuarioId;

        eventoEntity = new Evento();
        eventoEntity.id = eventoId;
        eventoEntity.setNomeEvento("Vento");
        eventoEntity.setPersonalizavel(true);

        cidadeEntity = new Cidade();
        cidadeEntity.id = cidadeId;
        cidadeEntity.nome = "Goiânia";

        preferenciaDTO = new PreferenciaRequestDTO();
        preferenciaDTO.setIdEvento(eventoId);
        preferenciaDTO.setIdCidade(cidadeId);
        preferenciaDTO.setValor(new BigDecimal("50.0"));
        preferenciaDTO.setPersonalizavel(true);

        preferenciaEntity = new Preferencia();
        preferenciaEntity.id = preferenciaId;
        preferenciaEntity.usuario = usuarioEntity;
        preferenciaEntity.evento = eventoEntity;
        preferenciaEntity.cidade = cidadeEntity;

        preferenciaResponseDTO = new PreferenciaResponseDTO();
        preferenciaResponseDTO.setId(preferenciaId);
    }

    @Test
    @DisplayName("Deve lançar NotFoundException se o evento não existir")
    void createPreferencia_EventoNotFound() {
        Preferencia prefSemEvento = new Preferencia();
        prefSemEvento.evento = null;

        when(preferenciaMapper.toEntity(preferenciaDTO)).thenReturn(prefSemEvento);

        NotFoundException exception = assertThrows(NotFoundException.class, () -> {
            preferenciaService.createPreferencia(usuarioId, preferenciaDTO);
        });

        assertTrue(exception.getMessage().contains("Evento não encontrado"));
    }

    @Test
    @DisplayName("Deve retornar lista de preferências do usuário")
    void findAllPreferenciasByUsuario_Success() {
        List<Preferencia> entities = List.of(preferenciaEntity);
        List<PreferenciaResponseDTO> dtos = List.of(preferenciaResponseDTO);

        when(preferenciaRepository.list("usuario.id", usuarioId)).thenReturn(entities);
        when(preferenciaMapper.toResponseDTOList(entities)).thenReturn(dtos);

        List<PreferenciaResponseDTO> result = preferenciaService.findAllPreferenciasByUsuario(usuarioId);

        assertEquals(1, result.size());
        assertEquals(preferenciaId, result.get(0).getId());
    }

    @Test
    @DisplayName("Deve atualizar preferência com sucesso")
    void updatePreferencia_Success() {
        when(preferenciaRepository.findByIdOptional(preferenciaId)).thenReturn(Optional.of(preferenciaEntity));
        doNothing().when(preferenciaMapper).updateEntityFromDto(preferenciaDTO, preferenciaEntity);
        when(preferenciaMapper.toResponseDTO(preferenciaEntity)).thenReturn(preferenciaResponseDTO);

        PreferenciaResponseDTO result = preferenciaService.updatePreferencia(usuarioId, preferenciaId, preferenciaDTO);

        assertNotNull(result);
        assertNotNull(preferenciaEntity.dataUltimaEdicao);
        verify(preferenciaMapper).updateEntityFromDto(preferenciaDTO, preferenciaEntity);
    }

    @Test
    @DisplayName("Deve lançar ForbiddenException se tentar atualizar preferência de outro usuário")
    void updatePreferencia_Forbidden() {
        Usuario outroUsuario = new Usuario();
        outroUsuario.id = UUID.randomUUID();
        preferenciaEntity.usuario = outroUsuario;

        when(preferenciaRepository.findByIdOptional(preferenciaId)).thenReturn(Optional.of(preferenciaEntity));

        assertThrows(ForbiddenException.class, () -> {
            preferenciaService.updatePreferencia(usuarioId, preferenciaId, preferenciaDTO);
        });
    }

    @Test
    @DisplayName("Deve substituir todas as preferências do usuário")
    void substituirPreferenciasDoUsuario_Success() {
        when(eventoRepository.findByIdOptional(eventoId)).thenReturn(Optional.of(eventoEntity));
        when(cidadeRepository.findByIdOptional(cidadeId)).thenReturn(Optional.of(cidadeEntity));

        preferenciaService.substituirPreferenciasDoUsuario(usuarioEntity, List.of(preferenciaDTO));

        verify(preferenciaRepository).delete("usuario", usuarioEntity);
        verify(preferenciaRepository).persist(any(Preferencia.class));
    }

    @Test
    @DisplayName("Deve apenas limpar preferências se a lista nova for vazia")
    void substituirPreferenciasDoUsuario_EmptyList() {
        preferenciaService.substituirPreferenciasDoUsuario(usuarioEntity, Collections.emptyList());

        verify(preferenciaRepository).delete("usuario", usuarioEntity);
        verify(preferenciaRepository, never()).persist(any(Preferencia.class));
    }

    @Test
    @DisplayName("Deve lançar ForbiddenException ao tentar criar preferência personalizada para evento fixo")
    void substituirPreferenciasDoUsuario_EventoFixoError() {
        eventoEntity.setPersonalizavel(false);
        preferenciaDTO.setPersonalizavel(true);

        when(eventoRepository.findByIdOptional(eventoId)).thenReturn(Optional.of(eventoEntity));
        when(cidadeRepository.findByIdOptional(cidadeId)).thenReturn(Optional.of(cidadeEntity));

        assertThrows(ForbiddenException.class, () -> {
            preferenciaService.substituirPreferenciasDoUsuario(usuarioEntity, List.of(preferenciaDTO));
        });

        verify(preferenciaRepository).delete("usuario", usuarioEntity);
        verify(preferenciaRepository, never()).persist(any(Preferencia.class));
    }
}