package org.ufg.mapper;

import org.mapstruct.*;
import org.ufg.dto.AvisoDTO;
import org.ufg.dto.AvisoResponseDTO; // Importar o novo DTO
import org.ufg.entity.Aviso;
import org.ufg.entity.Cidade;
import org.ufg.entity.Evento;
import java.util.UUID;
import java.util.List;
import jakarta.enterprise.context.ApplicationScoped;

@Mapper(componentModel = "cdi",
        unmappedTargetPolicy = ReportingPolicy.IGNORE,
        uses = {AvisoMapper.MappersAuxiliares.class}
)
@ApplicationScoped
public interface AvisoMapper {


    @Mapping(target = "evento", source = "idEvento", qualifiedByName = "mapEvento")
    @Mapping(target = "cidade", source = "idCidade", qualifiedByName = "mapCidade")
    Aviso toEntity(AvisoDTO dto);

    @Mapping(target = "idEvento", source = "evento.id")
    @Mapping(target = "nomeEvento", source = "evento.nomeEvento")
    @Mapping(target = "idCidade", source = "cidade.id")
    @Mapping(target = "nomeCidade", source = "cidade.nome")
    AvisoResponseDTO toResponseDTO(Aviso entity);

    List<AvisoResponseDTO> toResponseDTOList(List<Aviso> entities);

    // Mappers Auxiliares (Mantidos iguais)
    class MappersAuxiliares {
        @Named("mapEvento")
        public static Evento mapEvento(UUID id) {
            if (id == null) return null;
            Evento evento = new Evento();
            evento.id = id;
            return evento;
        }

        @Named("mapCidade")
        public static Cidade mapCidade(UUID id) {
            if (id == null) return null;
            Cidade cidade = new Cidade();
            cidade.id = id;
            return cidade;
        }
    }
}