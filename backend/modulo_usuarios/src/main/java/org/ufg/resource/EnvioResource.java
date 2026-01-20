package org.ufg.resource;

import jakarta.annotation.security.RolesAllowed;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.ufg.dto.EnvioBulkRequestDTO;
import org.ufg.dto.EnvioRequestDTO;
import org.ufg.dto.EnvioResponseDTO;
import org.ufg.service.EnvioService;

import java.net.URI;
import java.util.List;
import java.util.UUID;

@Path("/envios")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@RolesAllowed("ADMIN")
public class EnvioResource {

    @Inject
    EnvioService envioService;

    @POST
    public Response create(@Valid EnvioRequestDTO dto) {
        try {
            EnvioResponseDTO newEnvio = envioService.createEnvio(dto);
            return Response.created(URI.create("/envios/" + newEnvio.getId()))
                    .entity(newEnvio)
                    .build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        }
    }

    @POST
    @Path("/bulk")
    public Response createBulk(@Valid EnvioBulkRequestDTO bulkDto) {
        try {
            List<EnvioResponseDTO> novosEnvios = envioService.createEnviosBulk(bulkDto);
            return Response.status(Response.Status.CREATED)
                    .entity(novosEnvios)
                    .build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        }
    }

    @GET
    public List<EnvioResponseDTO> findAll() {
        return envioService.findAllEnvios();
    }

    @GET
    @Path("/{id}")
    public Response findById(@PathParam("id") String id) {
        try {
            UUID uuid = UUID.fromString(id);
            EnvioResponseDTO envio = envioService.findEnvioById(uuid);
            return Response.ok(envio).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity("ID inválido.").build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        }
    }
}