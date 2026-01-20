package org.ufg.mapper;

import org.mapstruct.*;
import org.ufg.dto.CanalRequestDTO;
import org.ufg.dto.CanalResponseDTO;
import org.ufg.entity.Canal;

import jakarta.enterprise.context.ApplicationScoped;
import java.util.List;

@Mapper(componentModel = MappingConstants.ComponentModel.JAKARTA_CDI, unmappedTargetPolicy = ReportingPolicy.IGNORE)
@ApplicationScoped
public interface CanalMapper {

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "dataInclusao", ignore = true)
    Canal toEntity(CanalRequestDTO dto);

    CanalResponseDTO toResponseDTO(Canal entity);

    List<CanalResponseDTO> toResponseDTOList(List<Canal> entities);

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "dataInclusao", ignore = true)
    void updateEntityFromDto(CanalRequestDTO dto, @MappingTarget Canal entity);
}