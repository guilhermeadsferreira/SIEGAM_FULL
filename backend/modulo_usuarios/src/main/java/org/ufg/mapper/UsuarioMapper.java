package org.ufg.mapper;

import org.mapstruct.*;
import org.ufg.dto.UsuarioRequestDTO;
import org.ufg.dto.UsuarioResponseDTO;
import org.ufg.entity.Usuario;
import org.ufg.dto.UsuarioDetalhadoResponseDTO;

import jakarta.enterprise.context.ApplicationScoped;
import java.util.List;

@Mapper(
        componentModel = MappingConstants.ComponentModel.JAKARTA_CDI,
        unmappedTargetPolicy = ReportingPolicy.IGNORE,
        uses = { CanalMapper.class }
)
@ApplicationScoped
public interface UsuarioMapper {

    /**
     * Converte UsuarioRequestDTO para Usuario Entity.
     * Usado para CRIAR um usuário (POST /usuarios).
     */
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "dataCriacao", ignore = true)
    @Mapping(target = "dataUltimaEdicao", ignore = true)
    @Mapping(target = "loginToken", ignore = true)
    @Mapping(target = "preferencias", ignore = true) // Gerenciado pelo PreferenciaService
    @Mapping(target = "canaisPreferidos", ignore = true) // Gerenciado pelo PerfilUsuarioDTO
    Usuario toEntity(UsuarioRequestDTO dto);

    /**
     * Converte Usuario Entity para UsuarioResponseDTO.
     * Usado para RETORNAR dados ao cliente (GET /usuarios, GET /usuarios/{id}).
     * * O MapStruct irá mapear automaticamente 'usuario.canaisPreferidos'
     * usando o CanalMapper injetado.
     */
    UsuarioResponseDTO toResponseDTO(Usuario entity);

    /**
     * Converte uma lista de Entities para uma lista de ResponseDTOs.
     */
    List<UsuarioResponseDTO> toResponseDTOList(List<Usuario> entities);

    /**
     * Atualiza uma entidade existente com dados de um DTO (PUT /usuarios/{id}).
     * Este DTO (Request) não lida com preferências ou canais,
     * por isso ignoramos esses campos.
     */
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "dataCriacao", ignore = true)
    @Mapping(target = "dataUltimaEdicao", ignore = true)
    @Mapping(target = "loginToken", ignore = true)
    @Mapping(target = "senha", ignore = true) 
    @Mapping(target = "preferencias", ignore = true)
    @Mapping(target = "canaisPreferidos", ignore = true)
    void updateEntityFromDto(UsuarioRequestDTO dto, @MappingTarget Usuario entity);

    @Mapping(target = "cidadeId", expression = "java(entity.getPreferencias().iterator().next().getCidade().getId())")
    @Mapping(target = "cidadeNome", expression = "java(entity.getPreferencias().iterator().next().getCidade().getNome())")
    @Mapping(target = "eventoId", expression = "java(entity.getPreferencias().iterator().next().getEvento().getId())")
    @Mapping(target = "eventoNome", expression = "java(entity.getPreferencias().iterator().next().getEvento().getNomeEvento())")
    @Mapping(target = "valor", expression = "java(entity.getPreferencias().iterator().next().getValor())")
    @Mapping(target = "personalizavel", expression = "java(entity.getPreferencias().iterator().next().getPersonalizavel())")
    @Mapping(target = "canaisPreferidos", source = "canaisPreferidos")
    UsuarioDetalhadoResponseDTO toDetalhadoResponseDTO(Usuario entity);

    /**
     * Converte uma lista de Entities para uma lista de UsuarioDetalhadoResponseDTOs.
     */
    List<UsuarioDetalhadoResponseDTO> toDetalhadoResponseDTOList(List<Usuario> entities);

}