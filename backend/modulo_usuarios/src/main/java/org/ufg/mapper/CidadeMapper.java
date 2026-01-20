package org.ufg.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.ReportingPolicy;
import org.ufg.dto.CidadeRequestDTO;
import org.ufg.dto.CidadeResponseDTO;
import org.ufg.entity.Cidade;

import jakarta.enterprise.context.ApplicationScoped;
import java.util.List;

@Mapper(componentModel = "cdi", unmappedTargetPolicy = ReportingPolicy.IGNORE)
@ApplicationScoped
public interface CidadeMapper {

    @Mapping(target = "id", ignore = true)
    Cidade toEntity(CidadeRequestDTO dto);

    List<Cidade> toEntityList(List<CidadeRequestDTO> dtos);

    CidadeResponseDTO toResponseDTO(Cidade entity);

    List<CidadeResponseDTO> toResponseDTOList(List<Cidade> entities);

    @Mapping(target = "id", ignore = true)
    void updateEntityFromDto(CidadeRequestDTO dto, @MappingTarget Cidade entity);
}