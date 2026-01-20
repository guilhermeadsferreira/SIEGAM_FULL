package org.ufg.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.Named;
import org.mapstruct.ReportingPolicy;
import org.ufg.dto.PreferenciaRequestDTO;
import org.ufg.dto.PreferenciaResponseDTO;
import org.ufg.entity.Cidade;
import org.ufg.entity.Evento;
import org.ufg.entity.Preferencia;

import jakarta.enterprise.context.ApplicationScoped;
import java.util.List;
import java.util.UUID;

@Mapper(componentModel = "cdi",
        unmappedTargetPolicy = ReportingPolicy.IGNORE,
        uses = {PreferenciaMapper.PreferenciaMappersAuxiliares.class}
)
@ApplicationScoped
public interface PreferenciaMapper {

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "dataCriacao", ignore = true)
    @Mapping(target = "dataUltimaEdicao", ignore = true)
    @Mapping(target = "usuario", ignore = true)

    @Mapping(target = "evento", source = "idEvento", qualifiedByName = "mapEvento")
    @Mapping(target = "cidade", source = "idCidade", qualifiedByName = "mapCidade")
    Preferencia toEntity(PreferenciaRequestDTO dto);

    @Mapping(target = "idUsuario", source = "usuario.id")
    @Mapping(target = "idEvento", source = "evento.id")
    @Mapping(target = "idCidade", source = "cidade.id")
    PreferenciaResponseDTO toResponseDTO(Preferencia entity);

    List<PreferenciaResponseDTO> toResponseDTOList(List<Preferencia> entities);

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "dataCriacao", ignore = true)
    @Mapping(target = "dataUltimaEdicao", ignore = true)
    @Mapping(target = "usuario", ignore = true)
    @Mapping(target = "evento", ignore = true)
    @Mapping(target = "cidade", ignore = true)
    void updateEntityFromDto(PreferenciaRequestDTO dto, @MappingTarget Preferencia entity);

    class PreferenciaMappersAuxiliares {

        @Named("mapEvento")
        public static Evento mapEvento(UUID id) {
            if (id == null) return null;
            return Evento.findById(id);
        }

        @Named("mapCidade")
        public static Cidade mapCidade(UUID id) {
            if (id == null) return null;
            return Cidade.findById(id);
        }
    }
}