package org.ufg.service;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.ForbiddenException;
import jakarta.ws.rs.NotFoundException;
import org.jboss.logging.Logger;
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

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@ApplicationScoped
public class PreferenciaService {

    private static final Logger LOG = Logger.getLogger(PreferenciaService.class);

    @Inject
    PreferenciaRepository preferenciaRepository;

    @Inject
    PreferenciaMapper preferenciaMapper;

    @Inject
    EventoRepository eventoRepository; // Necessário para buscar Evento

    @Inject
    CidadeRepository cidadeRepository;

    @Transactional
    public PreferenciaResponseDTO createPreferencia(UUID idUsuario, PreferenciaRequestDTO dto) {
        LOG.infof("Service: Criando preferência para Usuário %s, Evento %s, Cidade %s",
                idUsuario, dto.getIdEvento(), dto.getIdCidade());

        Preferencia preferencia = preferenciaMapper.toEntity(dto);

        if (preferencia.evento == null) {
            throw new NotFoundException("Evento não encontrado com o ID: " + dto.getIdEvento());
        }
        if (preferencia.cidade == null) {
            throw new NotFoundException("Cidade não encontrada com o ID: " + dto.getIdCidade());
        }

        Usuario usuario = Usuario.findById(idUsuario);
        if (usuario == null) {
            throw new NotFoundException("Usuário não encontrado.");
        }
        preferencia.usuario = usuario;

        if (!preferencia.evento.getPersonalizavel()) {
            throw new ForbiddenException(
                    String.format("Não é possível criar preferências para o evento '%s' pois ele não é personalizável.", preferencia.evento.getNomeEvento())
            );
        }

        if (preferenciaRepository.findByUsuarioEventoCidade(idUsuario, dto.getIdEvento(), dto.getIdCidade()).isPresent()) {
            throw new IllegalArgumentException("Já existe uma preferência para este evento e cidade para o seu usuário.");
        }

        preferencia.dataCriacao = LocalDate.now();
        preferencia.dataUltimaEdicao = LocalDate.now();

        preferenciaRepository.persist(preferencia);
        return preferenciaMapper.toResponseDTO(preferencia);
    }

    public List<PreferenciaResponseDTO> findAllPreferenciasByUsuario(UUID idUsuario) {
        LOG.infof("Service: Buscando todas as preferências do Usuário %s.", idUsuario);
        List<Preferencia> entities = preferenciaRepository.list("usuario.id", idUsuario);
        return preferenciaMapper.toResponseDTOList(entities);
    }

    @Transactional
    public PreferenciaResponseDTO updatePreferencia(UUID idUsuario, UUID id, PreferenciaRequestDTO dto) {
        LOG.infof("Service: Atualizando preferência ID: %s para Usuário %s", id, idUsuario);

        Preferencia preferencia = preferenciaRepository.findByIdOptional(id)
                .orElseThrow(() -> new NotFoundException("Preferencia não encontrada com o ID: " + id));

        if (!preferencia.usuario.id.equals(idUsuario)) {
            throw new ForbiddenException("Você não tem permissão para alterar esta preferência.");
        }

        preferenciaMapper.updateEntityFromDto(dto, preferencia);

        preferencia.dataUltimaEdicao = LocalDate.now();

        return preferenciaMapper.toResponseDTO(preferencia);
    }

    @Transactional
    public void substituirPreferenciasDoUsuario(Usuario usuario, List<PreferenciaRequestDTO> dtos) {
        preferenciaRepository.delete("usuario", usuario);

        if (dtos == null || dtos.isEmpty()) {
            return;
        }

        for (PreferenciaRequestDTO dto : dtos) {

            Evento evento = eventoRepository.findByIdOptional(dto.getIdEvento())
                    .orElseThrow(() -> new NotFoundException("Evento não encontrado: " + dto.getIdEvento()));

            Cidade cidade = cidadeRepository.findByIdOptional(dto.getIdCidade())
                    .orElseThrow(() -> new NotFoundException("Cidade não encontrada: " + dto.getIdCidade()));

            if (Boolean.TRUE.equals(dto.getPersonalizavel()) && !evento.getPersonalizavel()) {
                throw new ForbiddenException("O evento " + evento.getNomeEvento() + " não aceita parâmetros personalizados, apenas monitoramento padrão.");
            }

            Preferencia novaPreferencia = new Preferencia();
            novaPreferencia.usuario = usuario;
            novaPreferencia.evento = evento;
            novaPreferencia.cidade = cidade;

            novaPreferencia.valor = dto.getValor();
            novaPreferencia.personalizavel = dto.getPersonalizavel();
            novaPreferencia.dataCriacao = LocalDate.now();
            novaPreferencia.dataUltimaEdicao = LocalDate.now();

            preferenciaRepository.persist(novaPreferencia);
        }
    }
}