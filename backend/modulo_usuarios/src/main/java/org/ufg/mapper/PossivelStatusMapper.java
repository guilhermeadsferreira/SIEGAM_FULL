package org.ufg.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.mapstruct.ReportingPolicy;
import org.ufg.dto.PossivelStatusRequestDTO;
import org.ufg.dto.PossivelStatusResponseDTO;
import org.ufg.entity.Canal;
import org.ufg.entity.PossivelStatus;

import jakarta.enterprise.context.ApplicationScoped;
import java.util.List;
import java.util.UUID;

@Mapper(componentModel = "cdi",
        unmappedTargetPolicy = ReportingPolicy.IGNORE,
        uses = {PossivelStatusMapper.PossivelStatusMappersAuxiliares.class}
)
@ApplicationScoped
public interface PossivelStatusMapper {

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "canal", source = "idCanal", qualifiedByName = "mapCanal")
    PossivelStatus toEntity(PossivelStatusRequestDTO dto);

    @Mapping(target = "idCanal", source = "canal.id")
    PossivelStatusResponseDTO toResponseDTO(PossivelStatus entity);

    List<PossivelStatusResponseDTO> toResponseDTOList(List<PossivelStatus> entities);


    class PossivelStatusMappersAuxiliares {

        @Named("mapCanal")
        public static Canal mapCanal(UUID id) {
            if (id == null) return null;
            return Canal.findById(id);
        }
    }
}