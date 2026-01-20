package org.ufg.mapper;

import org.ufg.dto.EventoRequestDTO;
import org.ufg.dto.EventoResponseDTO;
import org.ufg.entity.Evento;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.ReportingPolicy;

import jakarta.enterprise.context.ApplicationScoped;
import java.util.List;

@Mapper(componentModel = "cdi", unmappedTargetPolicy = ReportingPolicy.IGNORE)
@ApplicationScoped
public interface EventoMapper {

    @Mapping(target = "id", ignore = true)
    Evento toEntity(EventoRequestDTO dto);

    EventoResponseDTO toResponseDTO(Evento entity);

    List<EventoResponseDTO> toResponseDTOList(List<Evento> entities);

    @Mapping(target = "id", ignore = true)
    void updateEntityFromDto(EventoRequestDTO dto, @MappingTarget Evento entity);
}