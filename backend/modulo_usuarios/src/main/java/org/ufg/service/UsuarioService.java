package org.ufg.service;

import jakarta.validation.Valid;
import jakarta.ws.rs.BadRequestException;
import jakarta.ws.rs.ForbiddenException;
import jakarta.ws.rs.NotFoundException;
import org.jboss.logging.Logger;
import org.ufg.dto.PerfilUsuarioDTO;
import org.ufg.dto.UsuarioRequestDTO;
import org.ufg.dto.UsuarioResponseDTO;
import org.ufg.dto.UsuarioDetalhadoResponseDTO;
import org.ufg.dto.LoginResponseDTO;
import org.ufg.entity.Canal;
import org.ufg.entity.Usuario;
import org.ufg.repository.CanalRepository;
import org.ufg.repository.UsuarioRepository;
import org.ufg.mapper.UsuarioMapper;
import org.ufg.util.SecurityUtils;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;
import java.util.UUID;

@ApplicationScoped
public class UsuarioService {

    @Inject
    UsuarioRepository usuarioRepository;

    @Inject
    UsuarioMapper usuarioMapper;

    @Inject
    SecurityUtils securityUtils;

    @Inject
    PreferenciaService preferenciaService;

    @Inject
    CanalRepository canalRepository;

    private static final Logger LOG = Logger.getLogger(UsuarioService.class);

    @Transactional
    public LoginResponseDTO authenticate(String email, String rawPassword) {

        Usuario usuario = usuarioRepository.findByEmail(email);

        if (usuario == null) {
            throw new NotFoundException("Credenciais inválidas.");
        }

        if (!securityUtils.verifyPassword(rawPassword, usuario.senha)) {

            throw new ForbiddenException("Credenciais inválidas.");
        }

        Set<String> roles = Set.of(usuario.nivelAcesso);
        String token = securityUtils.generateJwt(usuario.id, usuario.email, roles);


        usuario.loginToken = token;
        usuario.dataUltimaEdicao = LocalDate.now();

        return new LoginResponseDTO(token, usuario.id, usuario.nivelAcesso);
    }


    @Transactional
    public UsuarioResponseDTO criarUsuario(UsuarioRequestDTO dto, boolean isCreationByAdmin) {
        if (usuarioRepository.findByEmail(dto.getEmail()) != null) {
            throw new BadRequestException("O e-mail informado já está cadastrado.");
        }

        if (dto.getWhatsapp() != null && !dto.getWhatsapp().trim().isEmpty()) {
            if (usuarioRepository.findByWhatsapp(dto.getWhatsapp()) != null) {
                throw new BadRequestException("O número de WhatsApp informado já está cadastrado.");
            }
        }

        if (dto.getSenha() == null || dto.getSenha().trim().isEmpty()) {
            throw new BadRequestException("A senha é obrigatória para a criação do usuário.");
        }
        Usuario novoUsuario = usuarioMapper.toEntity(dto);

        String hashedPassword = securityUtils.hashPassword(dto.getSenha());
        novoUsuario.senha = hashedPassword;

        if (isCreationByAdmin) {
            String nivelDesejado = dto.getNivelAcesso() != null ? dto.getNivelAcesso().toUpperCase() : "CLIENTE";

            if ("ADMIN".equals(nivelDesejado)) {
                novoUsuario.nivelAcesso = "ADMIN";
            } else {
                novoUsuario.nivelAcesso = "CLIENTE";
            }
        } else {
            novoUsuario.nivelAcesso = "CLIENTE";
        }

        LocalDateTime agora = LocalDateTime.now();
        novoUsuario.dataCriacao = agora;
        novoUsuario.dataUltimaEdicao = agora.toLocalDate();

        usuarioRepository.persist(novoUsuario);

        return usuarioMapper.toResponseDTO(novoUsuario);
    }

    public List<UsuarioResponseDTO> listarTodos() {
        List<Usuario> usuarios = usuarioRepository.findAllWithCanais();
        return usuarioMapper.toResponseDTOList(usuarios);
    }


    @Transactional
    public UsuarioResponseDTO atualizarUsuario(UUID id, UsuarioRequestDTO dto) {

        Usuario usuarioParaAtualizar = findByIdOrThrowNotFound(id);

        if (dto.getEmail() != null && !dto.getEmail().equals(usuarioParaAtualizar.email)) {
            if (usuarioRepository.findByEmail(dto.getEmail()) != null) {
                throw new BadRequestException("O novo e-mail informado já está cadastrado em outra conta.");
            }
        }

        if (dto.getWhatsapp() != null && !dto.getWhatsapp().equals(usuarioParaAtualizar.whatsapp)) {
            if (usuarioRepository.findByWhatsapp(dto.getWhatsapp()) != null) {
                throw new BadRequestException("O novo número de WhatsApp informado já está cadastrado em outra conta.");
            }
        }

        usuarioMapper.updateEntityFromDto(dto, usuarioParaAtualizar);

        if (dto.getSenha() != null && !dto.getSenha().trim().isEmpty()) {
            String hashedPassword = securityUtils.hashPassword(dto.getSenha());
            usuarioParaAtualizar.senha = hashedPassword;
        }


        if (dto.getNivelAcesso() != null) {

            usuarioParaAtualizar.nivelAcesso = usuarioParaAtualizar.nivelAcesso;
        }

        usuarioParaAtualizar.dataUltimaEdicao = LocalDate.now();


        return usuarioMapper.toResponseDTO(usuarioParaAtualizar);
    }

    @Transactional
    public UsuarioResponseDTO atualizarNivelAcesso(UUID id, String novoNivelAcesso) {
        if (!"ADMIN".equals(novoNivelAcesso) && !"CLIENTE".equals(novoNivelAcesso)) {
            throw new BadRequestException("Nível de acesso inválido. Permitido: ADMIN ou CLIENTE.");
        }

        Usuario usuario = findByIdOrThrowNotFound(id);
        usuario.nivelAcesso = novoNivelAcesso;
        usuario.dataUltimaEdicao = LocalDate.now();

        return usuarioMapper.toResponseDTO(usuario);
    }

    @Transactional
    public void deletarUsuario(UUID id) {

        throw new UnsupportedOperationException("Método deletarUsuario ainda não implementado.");
    }

    private Usuario findByIdOrThrowNotFound(UUID id) {
        Usuario usuario = usuarioRepository.findById(id);
        if (usuario == null) {
            throw new NotFoundException("Usuário com ID " + id + " não encontrado.");
        }
        return usuario;
    }

    public UsuarioResponseDTO buscarUsuarioPorId(UUID id) {
        Usuario usuario = usuarioRepository.findByIdWithCanais(id);
        if (usuario == null) {
            throw new NotFoundException("Usuário com ID " + id + " não encontrado.");
        }
        return usuarioMapper.toResponseDTO(usuario);
    }

    public List<UsuarioResponseDTO> findUsuariosByEvento(UUID idEvento) {
        LOG.infof("Service: Buscando usuários por ID de evento: %s", idEvento);

        List<Usuario> entities = usuarioRepository.findByPreferenciaEventoId(idEvento);

        List<UsuarioResponseDTO> dtos = usuarioMapper.toResponseDTOList(entities);

        LOG.infof("Service: Encontrados %d usuários para o evento.", dtos.size());
        return dtos;
    }

    public List<UsuarioResponseDTO> findUsuariosByEventoAndCidade(UUID idEvento, UUID idCidade) {
        LOG.infof("Service: Buscando usuários por ID de evento: %s E ID de cidade: %s", idEvento, idCidade);

        List<Usuario> entities = usuarioRepository.findByPreferenciaEventoIdAndCidadeId(idEvento, idCidade);

        List<UsuarioResponseDTO> dtos = usuarioMapper.toResponseDTOList(entities);

        LOG.infof("Service: Encontrados %d usuários.", dtos.size());
        return dtos;
    }

    public List<UsuarioDetalhadoResponseDTO> findUsuariosDetalhadoByEventoAndCidade(UUID idEvento, UUID idCidade) {
        LOG.infof("Service: Buscando usuários por ID de evento: %s E ID de cidade: %s", idEvento, idCidade);

        List<Usuario> entities = usuarioRepository.findDetalhadoByEventoAndCidade(idEvento, idCidade);

        List<UsuarioDetalhadoResponseDTO> dtos = usuarioMapper.toDetalhadoResponseDTOList(entities);

        LOG.infof("Service: Encontrados %d usuários.", dtos.size());
        return dtos;
    }

    @Transactional
    public void atualizarPerfilCompleto(UUID idUsuario, PerfilUsuarioDTO dto) {
        Usuario usuario = findByIdOrThrowNotFound(idUsuario); // Reutilizando seu helper

        usuario.canaisPreferidos.clear();

        if (dto.getIdsCanaisPreferidos() != null && !dto.getIdsCanaisPreferidos().isEmpty()) {
            List<Canal> canais = canalRepository.list("id in ?1", dto.getIdsCanaisPreferidos());
            usuario.canaisPreferidos.addAll(canais);
        }

        preferenciaService.substituirPreferenciasDoUsuario(usuario, dto.getPreferencias());

    }
}