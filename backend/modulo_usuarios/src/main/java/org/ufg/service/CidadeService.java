package org.ufg.service;

import io.quarkus.cache.CacheInvalidateAll;
import io.quarkus.cache.CacheResult;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.NotFoundException;
import org.jboss.logging.Logger;
import org.ufg.dto.CidadeBulkRequestDTO;
import org.ufg.dto.CidadeRequestDTO;
import org.ufg.dto.CidadeResponseDTO;
import org.ufg.entity.Cidade;
import org.ufg.mapper.CidadeMapper;
import org.ufg.repository.CidadeRepository;
import java.util.List;
import java.util.stream.Collectors;
import java.util.Optional;
import java.util.UUID;

@ApplicationScoped
public class CidadeService {

    private static final Logger LOG = Logger.getLogger(CidadeService.class);

    @Inject
    CidadeRepository cidadeRepository;

    @Inject
    CidadeMapper cidadeMapper;

    @CacheInvalidateAll(cacheName = "lista-cidades")
    @Transactional
    public CidadeResponseDTO createCidade(CidadeRequestDTO dto) {
        LOG.infof("Service: Criando nova cidade: %s", dto.getNome());

        if (cidadeRepository.findByNome(dto.getNome()).isPresent()) {
            throw new IllegalArgumentException("Cidade com este nome já existe.");
        }

        Cidade cidade = cidadeMapper.toEntity(dto);
        cidadeRepository.persist(cidade);
        return cidadeMapper.toResponseDTO(cidade);
    }

    @CacheInvalidateAll(cacheName = "lista-cidades")
    @Transactional
    public List<CidadeResponseDTO> createCidadesBulk(CidadeBulkRequestDTO bulkDto) {
        LOG.infof("Service: Criando %d cidades em lote.", bulkDto.getCidades().size());

        List<Cidade> novasCidades = cidadeMapper.toEntityList(bulkDto.getCidades());


        List<String> nomesDuplicados = novasCidades.stream()
                .map(Cidade::getNome)
                .filter(nome -> cidadeRepository.findByNome(nome).isPresent())
                .collect(Collectors.toList());

        if (!nomesDuplicados.isEmpty()) {
            throw new IllegalArgumentException("As seguintes cidades já existem no banco: " + String.join(", ", nomesDuplicados));
        }
        cidadeRepository.persist(novasCidades);

        return cidadeMapper.toResponseDTOList(novasCidades);
    }

    @CacheResult(cacheName = "lista-cidades")
    public List<CidadeResponseDTO> findAllCidades() {
        LOG.info("Service: Buscando todas as cidades.");
        List<Cidade> entities = cidadeRepository.listAll();
        return cidadeMapper.toResponseDTOList(entities);
    }

    public CidadeResponseDTO findCidadeById(UUID id) {
        LOG.infof("Service: Buscando cidade por ID: %s", id);
        Cidade cidade = cidadeRepository.findByIdOptional(id)
                .orElseThrow(() -> new NotFoundException("Cidade não encontrada com o ID: " + id));
        return cidadeMapper.toResponseDTO(cidade);
    }

    @CacheInvalidateAll(cacheName = "lista-cidades")
    @Transactional
    public CidadeResponseDTO updateCidade(UUID id, CidadeRequestDTO dto) {
        LOG.infof("Service: Atualizando cidade ID: %s", id);

        Optional<Cidade> existingByName = cidadeRepository.findByNome(dto.getNome());
        if (existingByName.isPresent() && !existingByName.get().id.equals(id)) {
            throw new IllegalArgumentException("Outra cidade com este nome já existe.");
        }

        Cidade cidade = cidadeRepository.findByIdOptional(id)
                .orElseThrow(() -> new NotFoundException("Cidade não encontrada para atualização com o ID: " + id));

        cidadeMapper.updateEntityFromDto(dto, cidade);

        return cidadeMapper.toResponseDTO(cidade);
    }
}