package org.ufg.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.mapstruct.ReportingPolicy;
import org.ufg.dto.EnvioRequestDTO;
import org.ufg.dto.EnvioResponseDTO;
import org.ufg.entity.*;

import jakarta.enterprise.context.ApplicationScoped;
import java.util.List;
import java.util.UUID;

@Mapper(componentModel = "cdi",
        unmappedTargetPolicy = ReportingPolicy.IGNORE,
        uses = {EnvioMapper.EnvioMappersAuxiliares.class}
)
@ApplicationScoped
public interface EnvioMapper {

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "canal", source = "idCanal", qualifiedByName = "mapCanal")
    @Mapping(target = "aviso", source = "idAviso", qualifiedByName = "mapAviso")
    @Mapping(target = "usuarioDestinatario", source = "idUsuarioDestinatario", qualifiedByName = "mapUsuario")
    @Mapping(target = "status", source = "idStatus", qualifiedByName = "mapStatus")
    Envio toEntity(EnvioRequestDTO dto);

    List<Envio> toEntityList(List<EnvioRequestDTO> dtos);

    @Mapping(target = "idCanal", source = "canal.id")
    @Mapping(target = "idAviso", source = "aviso.id")
    @Mapping(target = "idUsuarioDestinatario", source = "usuarioDestinatario.id")
    @Mapping(target = "idStatus", source = "status.id")
    EnvioResponseDTO toResponseDTO(Envio entity);

    List<EnvioResponseDTO> toResponseDTOList(List<Envio> entities);


    class EnvioMappersAuxiliares {


        @Named("mapCanal")
        public static Canal mapCanal(UUID id) {
            if (id == null) return null;
            return Canal.findById(id);
        }

        @Named("mapAviso")
        public static Aviso mapAviso(UUID id) {
            if (id == null) return null;
            return Aviso.findById(id);
        }

        @Named("mapUsuario")
        public static Usuario mapUsuario(UUID id) {
            if (id == null) return null;
            return Usuario.findById(id);
        }

        @Named("mapStatus")
        public static PossivelStatus mapStatus(UUID id) {
            if (id == null) return null;
            return PossivelStatus.findById(id);
        }
    }
}