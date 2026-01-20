package org.ufg.service;

import jakarta.ws.rs.BadRequestException;
import jakarta.ws.rs.ForbiddenException;
import jakarta.ws.rs.NotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.ufg.dto.*;
import org.ufg.entity.Canal;
import org.ufg.entity.Usuario;
import org.ufg.mapper.UsuarioMapper;
import org.ufg.repository.CanalRepository;
import org.ufg.repository.UsuarioRepository;
import org.ufg.util.SecurityUtils;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UsuarioServiceTest {

    @Mock
    UsuarioRepository usuarioRepository;

    @Mock
    UsuarioMapper usuarioMapper;

    @Mock
    SecurityUtils securityUtils;

    @Mock
    PreferenciaService preferenciaService;

    @Mock
    CanalRepository canalRepository;

    @InjectMocks
    UsuarioService usuarioService;

    private UUID usuarioId;
    private Usuario usuarioEntity;
    private UsuarioRequestDTO usuarioRequestDTO;
    private UsuarioResponseDTO usuarioResponseDTO;
    private LoginResponseDTO loginResponseDTO;

    @BeforeEach
    void setUp() {
        usuarioId = UUID.randomUUID();

        usuarioEntity = new Usuario();
        usuarioEntity.id = usuarioId;
        usuarioEntity.email = "test@email.com";
        usuarioEntity.senha = "hashedPassword";
        usuarioEntity.nivelAcesso = "CLIENTE";
        usuarioEntity.canaisPreferidos = new ArrayList<>();

        usuarioRequestDTO = new UsuarioRequestDTO();
        usuarioRequestDTO.setEmail("test@email.com");
        usuarioRequestDTO.setSenha("rawPassword");
        usuarioRequestDTO.setWhatsapp("11999999999");

        usuarioResponseDTO = new UsuarioResponseDTO();
        usuarioResponseDTO.setId(usuarioId);
        usuarioResponseDTO.setEmail("test@email.com");
    }

    @Test
    @DisplayName("Deve autenticar com sucesso")
    void authenticate_Success() {
        when(usuarioRepository.findByEmail("test@email.com")).thenReturn(usuarioEntity);
        when(securityUtils.verifyPassword("rawPassword", "hashedPassword")).thenReturn(true);
        when(securityUtils.generateJwt(any(), any(), any())).thenReturn("token123");

        LoginResponseDTO result = usuarioService.authenticate("test@email.com", "rawPassword");

        assertNotNull(result);
        assertEquals("token123", result.getToken());
        assertEquals(usuarioId, result.getId());
    }

    @Test
    @DisplayName("Deve lançar NotFoundException ao tentar autenticar e-mail inexistente")
    void authenticate_UserNotFound() {
        when(usuarioRepository.findByEmail("test@email.com")).thenReturn(null);

        assertThrows(NotFoundException.class, () ->
                usuarioService.authenticate("test@email.com", "rawPassword")
        );
    }

    @Test
    @DisplayName("Deve lançar ForbiddenException ao tentar autenticar com senha errada")
    void authenticate_WrongPassword() {
        when(usuarioRepository.findByEmail("test@email.com")).thenReturn(usuarioEntity);
        when(securityUtils.verifyPassword("wrongPassword", "hashedPassword")).thenReturn(false);

        assertThrows(ForbiddenException.class, () ->
                usuarioService.authenticate("test@email.com", "wrongPassword")
        );
    }

    @Test
    @DisplayName("Deve criar usuário com sucesso")
    void criarUsuario_Success() {
        when(usuarioRepository.findByEmail(anyString())).thenReturn(null);
        when(usuarioRepository.findByWhatsapp(anyString())).thenReturn(null);
        when(usuarioMapper.toEntity(usuarioRequestDTO)).thenReturn(usuarioEntity);
        when(securityUtils.hashPassword("rawPassword")).thenReturn("hashedPassword");
        when(usuarioMapper.toResponseDTO(usuarioEntity)).thenReturn(usuarioResponseDTO);

        UsuarioResponseDTO result = usuarioService.criarUsuario(usuarioRequestDTO, false);

        assertNotNull(result);
        assertEquals("CLIENTE", usuarioEntity.nivelAcesso);
        verify(usuarioRepository).persist(usuarioEntity);
    }

    @Test
    @DisplayName("Deve criar usuário ADMIN se solicitado por admin")
    void criarUsuario_Admin_Success() {
        usuarioRequestDTO.setNivelAcesso("ADMIN");

        when(usuarioRepository.findByEmail(anyString())).thenReturn(null);
        when(usuarioMapper.toEntity(usuarioRequestDTO)).thenReturn(usuarioEntity);
        when(securityUtils.hashPassword("rawPassword")).thenReturn("hashedPassword");
        when(usuarioMapper.toResponseDTO(usuarioEntity)).thenReturn(usuarioResponseDTO);

        usuarioService.criarUsuario(usuarioRequestDTO, true);

        assertEquals("ADMIN", usuarioEntity.nivelAcesso);
    }

    @Test
    @DisplayName("Deve lançar BadRequestException se e-mail já existe")
    void criarUsuario_EmailDuplicate() {
        when(usuarioRepository.findByEmail("test@email.com")).thenReturn(usuarioEntity);

        assertThrows(BadRequestException.class, () ->
                usuarioService.criarUsuario(usuarioRequestDTO, false)
        );
        verify(usuarioRepository, never()).persist(any(Usuario.class));
    }

    @Test
    @DisplayName("Deve lançar BadRequestException se WhatsApp já existe")
    void criarUsuario_WhatsappDuplicate() {
        when(usuarioRepository.findByEmail("test@email.com")).thenReturn(null);
        when(usuarioRepository.findByWhatsapp("11999999999")).thenReturn(usuarioEntity);

        assertThrows(BadRequestException.class, () ->
                usuarioService.criarUsuario(usuarioRequestDTO, false)
        );
    }

    @Test
    @DisplayName("Deve listar todos os usuários")
    void listarTodos_Success() {
        when(usuarioRepository.findAllWithCanais()).thenReturn(List.of(usuarioEntity));
        when(usuarioMapper.toResponseDTOList(anyList())).thenReturn(List.of(usuarioResponseDTO));

        List<UsuarioResponseDTO> result = usuarioService.listarTodos();

        assertFalse(result.isEmpty());
        assertEquals(1, result.size());
    }

    @Test
    @DisplayName("Deve atualizar usuário com sucesso")
    void atualizarUsuario_Success() {
        when(usuarioRepository.findById(usuarioId)).thenReturn(usuarioEntity);
        doNothing().when(usuarioMapper).updateEntityFromDto(usuarioRequestDTO, usuarioEntity);
        when(usuarioMapper.toResponseDTO(usuarioEntity)).thenReturn(usuarioResponseDTO);
        when(securityUtils.hashPassword("rawPassword")).thenReturn("newHash");

        UsuarioResponseDTO result = usuarioService.atualizarUsuario(usuarioId, usuarioRequestDTO);

        assertNotNull(result);
        verify(usuarioMapper).updateEntityFromDto(usuarioRequestDTO, usuarioEntity);
        assertEquals("newHash", usuarioEntity.senha);
    }

    @Test
    @DisplayName("Deve lançar BadRequestException ao atualizar para e-mail duplicado")
    void atualizarUsuario_EmailDuplicate() {
        UsuarioRequestDTO updateDto = new UsuarioRequestDTO();
        updateDto.setEmail("new@email.com");

        when(usuarioRepository.findById(usuarioId)).thenReturn(usuarioEntity);
        when(usuarioRepository.findByEmail("new@email.com")).thenReturn(new Usuario());

        assertThrows(BadRequestException.class, () ->
                usuarioService.atualizarUsuario(usuarioId, updateDto)
        );
    }

    @Test
    @DisplayName("Deve atualizar nível de acesso")
    void atualizarNivelAcesso_Success() {
        when(usuarioRepository.findById(usuarioId)).thenReturn(usuarioEntity);
        when(usuarioMapper.toResponseDTO(usuarioEntity)).thenReturn(usuarioResponseDTO);

        usuarioService.atualizarNivelAcesso(usuarioId, "ADMIN");

        assertEquals("ADMIN", usuarioEntity.nivelAcesso);
    }

    @Test
    @DisplayName("Deve lançar BadRequestException para nível de acesso inválido")
    void atualizarNivelAcesso_Invalid() {
        assertThrows(BadRequestException.class, () ->
                usuarioService.atualizarNivelAcesso(usuarioId, "INVALIDO")
        );
    }

    @Test
    @DisplayName("Deve buscar usuário por ID")
    void buscarUsuarioPorId_Success() {
        when(usuarioRepository.findByIdWithCanais(usuarioId)).thenReturn(usuarioEntity);
        when(usuarioMapper.toResponseDTO(usuarioEntity)).thenReturn(usuarioResponseDTO);

        UsuarioResponseDTO result = usuarioService.buscarUsuarioPorId(usuarioId);

        assertNotNull(result);
        assertEquals(usuarioId, result.getId());
    }

    @Test
    @DisplayName("Deve lançar NotFoundException ao buscar usuário inexistente")
    void buscarUsuarioPorId_NotFound() {
        when(usuarioRepository.findByIdWithCanais(usuarioId)).thenReturn(null);

        assertThrows(NotFoundException.class, () ->
                usuarioService.buscarUsuarioPorId(usuarioId)
        );
    }

    @Test
    @DisplayName("Deve atualizar perfil completo")
    void atualizarPerfilCompleto_Success() {
        PerfilUsuarioDTO perfilDTO = new PerfilUsuarioDTO();
        perfilDTO.setIdsCanaisPreferidos(List.of(UUID.randomUUID()));
        perfilDTO.setPreferencias(Collections.emptyList());

        when(usuarioRepository.findById(usuarioId)).thenReturn(usuarioEntity);
        when(canalRepository.list(anyString(), anyList())).thenReturn(List.of(new Canal()));

        usuarioService.atualizarPerfilCompleto(usuarioId, perfilDTO);

        verify(preferenciaService).substituirPreferenciasDoUsuario(usuarioEntity, perfilDTO.getPreferencias());
        assertEquals(1, usuarioEntity.canaisPreferidos.size());
    }

    @Test
    @DisplayName("deletarUsuario deve lançar UnsupportedOperationException")
    void deletarUsuario_ThrowsException() {
        assertThrows(UnsupportedOperationException.class, () ->
                usuarioService.deletarUsuario(usuarioId)
        );
    }
}