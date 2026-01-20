package org.ufg.resource;

import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.ufg.dto.AvisoDTO;
import org.ufg.dto.AvisoListDTO;
import jakarta.annotation.security.RolesAllowed;
import org.ufg.dto.AvisoResponseDTO;
import org.ufg.dto.PageDTO;
import org.ufg.service.AvisoService;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@Path("/avisos")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@RolesAllowed("ADMIN")
public class AvisoResource {
    @Inject
    AvisoService avisoService;

    @POST
    public Response createAviso(@Valid AvisoDTO avisoDTO) {
        AvisoResponseDTO novoAviso = avisoService.criarAviso(avisoDTO);

        return Response.status(Response.Status.CREATED)
                .entity(novoAviso)
                .build();
    }

    @GET
    @Path("/{id}")
    public Response getAviso(@PathParam("id") String id) {
        UUID uuid;
        try {
            uuid = UUID.fromString(id);
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity("ID de Aviso inválido: " + id)
                    .build();
        }

        AvisoResponseDTO aviso = avisoService.buscarAvisoPorId(uuid);

        if (aviso == null) {
            return Response.status(Response.Status.NOT_FOUND).build(); // 404 Not Found
        }

        return Response.ok(aviso).build();
    }


    @GET
    public Response getAllAvisos() {
        List<AvisoResponseDTO> avisos = avisoService.listarTodosAvisos();

        return Response.ok(avisos).build();
    }

    @GET
    @Path("/today")
    public Response getAllAvisosToday() {
        List<AvisoResponseDTO> avisos = avisoService.listarTodosAvisosDataAtual();

        return Response.ok(avisos).build();
    }


    @PUT
    @Path("/{id}")
    public Response updateAviso(@PathParam("id") String id, AvisoDTO avisoDTO) {
        System.out.println("Endpoint PUT /avisos/" + id + " acessado por ADMIN.");
        return Response.status(Response.Status.NOT_IMPLEMENTED) // 501 Not Implemented
                .entity("Método de atualização não implementado no Service.")
                .build();
    }


    @POST
    @Path("/lote")
    public Response processListAvisos(@Valid AvisoListDTO avisoListDTO) {
        int processadosCount = avisoService.processarLoteAvisos(avisoListDTO.getAvisos());

        return Response.ok(
                "Lote processado com sucesso. Total de avisos inseridos: " + processadosCount
        ).build();
    }

    @GET
    @Path("/filtro")
    public Response buscarComFiltros(
            @QueryParam("data") LocalDate data,
            @QueryParam("idEvento") String idEventoStr,
            @QueryParam("idCidade") String idCidadeStr,
            @QueryParam("page") @DefaultValue("0") int page,
            @QueryParam("size") @DefaultValue("10") int size
    ) {
        UUID idEvento = null;
        UUID idCidade = null;

        try {
            if (idEventoStr != null && !idEventoStr.isBlank()) {
                idEvento = UUID.fromString(idEventoStr);
            }
            if (idCidadeStr != null && !idCidadeStr.isBlank()) {
                idCidade = UUID.fromString(idCidadeStr);
            }
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity("ID de Evento ou Cidade inválido.")
                    .build();
        }

        PageDTO<AvisoResponseDTO> resultado = avisoService.filtrarAvisos(data, idEvento, idCidade, page, size);

        return Response.ok(resultado).build();
    }

    @GET
    @Path("/estatisticas/cidades")
    public Response getTopCidades() {
        return Response.ok(avisoService.getTopCidades()).build();
    }

    @GET
    @Path("/estatisticas/eventos")
    public Response getDistribuicaoEventos() {
        return Response.ok(avisoService.getDistribuicaoEventos()).build();
    }

    @GET
    @Path("/estatisticas/tendencia")
    public Response getTendencia() {
        return Response.ok(avisoService.getTendenciaSemanal()).build();
    }
}