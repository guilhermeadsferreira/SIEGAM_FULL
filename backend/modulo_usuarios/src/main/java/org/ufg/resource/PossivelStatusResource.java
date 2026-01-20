package org.ufg.resource;

import jakarta.annotation.security.RolesAllowed;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.ufg.dto.PossivelStatusRequestDTO;
import org.ufg.dto.PossivelStatusResponseDTO;
import org.ufg.service.PossivelStatusService;

import java.net.URI;
import java.util.List;
import java.util.UUID;

@Path("/status")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@RolesAllowed("ADMIN")
public class PossivelStatusResource {

    @Inject
    PossivelStatusService statusService;

    @POST
    public Response create(@Valid PossivelStatusRequestDTO dto) {
        try {
            PossivelStatusResponseDTO newStatus = statusService.createStatus(dto);
            return Response.created(URI.create("/status/" + newStatus.getId()))
                    .entity(newStatus)
                    .build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity(e.getMessage()).build();
        }
    }

    @GET
    public List<PossivelStatusResponseDTO> findAll() {
        return statusService.findAllStatus();
    }

    @GET
    @Path("/{id}")
    public Response findById(@PathParam("id") String id) {
        try {
            UUID uuid = UUID.fromString(id);
            PossivelStatusResponseDTO status = statusService.findStatusById(uuid);
            return Response.ok(status).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity("ID inválido.").build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        }
    }
}