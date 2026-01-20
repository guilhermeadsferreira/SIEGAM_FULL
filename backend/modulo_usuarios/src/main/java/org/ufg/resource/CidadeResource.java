package org.ufg.resource;

import jakarta.annotation.security.RolesAllowed;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.ufg.dto.CidadeBulkRequestDTO;
import org.ufg.dto.CidadeRequestDTO;
import org.ufg.dto.CidadeResponseDTO;
import org.ufg.service.CidadeService;

import java.net.URI;
import java.util.List;
import java.util.UUID;

@Path("/cidades")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@RolesAllowed({"ADMIN"})
public class CidadeResource {

    @Inject
    CidadeService cidadeService;

    @POST
    @RolesAllowed({"ADMIN"})
    public Response create(@Valid CidadeRequestDTO dto) {
        try {
            CidadeResponseDTO newCidade = cidadeService.createCidade(dto);
            return Response.created(URI.create("/cidades/" + newCidade.getId()))
                    .entity(newCidade)
                    .build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity(e.getMessage()).build();
        }
    }

    @POST
    @Path("/bulk")
    @RolesAllowed({"ADMIN"})

    public Response createBulk(@Valid CidadeBulkRequestDTO bulkDto) {
        try {
            List<CidadeResponseDTO> novasCidades = cidadeService.createCidadesBulk(bulkDto);
            // Retorna 201 Created com a lista de cidades criadas
            return Response.status(Response.Status.CREATED)
                    .entity(novasCidades)
                    .build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity(e.getMessage()).build();
        }
    }

    @GET
    @RolesAllowed({"ADMIN", "CLIENTE"})

    public List<CidadeResponseDTO> findAll() {
        return cidadeService.findAllCidades();
    }

    @GET
    @Path("/{id}")
    @RolesAllowed({"ADMIN"})

    public Response findById(@PathParam("id") String id) {
        try {
            UUID uuid = UUID.fromString(id);
            CidadeResponseDTO cidade = cidadeService.findCidadeById(uuid);
            return Response.ok(cidade).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity("ID inválido.").build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        }
    }

    @PUT
    @Path("/{id}")
    @RolesAllowed({"ADMIN"})
    public Response update(@PathParam("id") String id, @Valid CidadeRequestDTO dto) {
        try {
            UUID uuid = UUID.fromString(id);
            CidadeResponseDTO updatedCidade = cidadeService.updateCidade(uuid, dto);
            return Response.ok(updatedCidade).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity(e.getMessage()).build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        }
    }
}