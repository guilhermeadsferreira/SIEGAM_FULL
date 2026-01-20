package org.ufg.resource;

import jakarta.annotation.security.RolesAllowed;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.ufg.dto.CanalRequestDTO;
import org.ufg.dto.CanalResponseDTO;
import org.ufg.service.CanalService;

import java.net.URI;
import java.util.List;
import java.util.UUID;

@Path("/canais")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@RolesAllowed("ADMIN")
public class CanalResource {

    @Inject
    CanalService canalService;

    @POST
    public Response create(@Valid CanalRequestDTO dto) {
        CanalResponseDTO newCanal = canalService.createCanal(dto);

        return Response.created(URI.create("/canais/" + newCanal.getId()))
                .entity(newCanal)
                .build();
    }

    @GET
    public List<CanalResponseDTO> findAll() {
        return canalService.findAllCanais();
    }

    @GET
    @Path("/{id}")
    public Response findById(@PathParam("id") String id) {
        try {
            UUID uuid = UUID.fromString(id);
            CanalResponseDTO canal = canalService.findCanalById(uuid);
            return Response.ok(canal).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity("ID inválido.").build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        }
    }

    @PUT
    @Path("/{id}")
    public Response update(@PathParam("id") String id, @Valid CanalRequestDTO dto) {
        try {
            UUID uuid = UUID.fromString(id);
            CanalResponseDTO updatedCanal = canalService.updateCanal(uuid, dto);
            return Response.ok(updatedCanal).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity("ID inválido ou nome de canal já existe.").build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        }
    }
}