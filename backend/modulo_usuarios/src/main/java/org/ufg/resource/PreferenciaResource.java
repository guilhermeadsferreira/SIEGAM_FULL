package org.ufg.resource;

import jakarta.annotation.security.RolesAllowed;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.jwt.JsonWebToken;
import org.ufg.dto.PreferenciaRequestDTO;
import org.ufg.dto.PreferenciaResponseDTO;
import org.ufg.service.PreferenciaService;

import java.net.URI;
import java.util.List;
import java.util.UUID;

@Path("/preferencias")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@RolesAllowed({"CLIENTE", "ADMIN"})
public class PreferenciaResource {

    @Inject
    PreferenciaService preferenciaService;

    @Inject
    JsonWebToken jwt;

    private UUID getUserId() {
        if (jwt != null && jwt.getSubject() != null) {
            try {
                return UUID.fromString(jwt.getSubject());
            } catch (IllegalArgumentException e) {
            }
        }
        throw new ForbiddenException("Usuário não autenticado ou token inválido.");
    }

    @POST
    public Response create(@Valid PreferenciaRequestDTO dto) {
        UUID idUsuario = getUserId();
        try {
            PreferenciaResponseDTO newPreferencia = preferenciaService.createPreferencia(idUsuario, dto);
            return Response.created(URI.create("/preferencias/" + newPreferencia.getId()))
                    .entity(newPreferencia)
                    .build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        } catch (ForbiddenException e) {
            return Response.status(Response.Status.FORBIDDEN).entity(e.getMessage()).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity(e.getMessage()).build();
        }
    }

    @GET
    public List<PreferenciaResponseDTO> findAllForUser() {
        UUID idUsuario = getUserId();
        return preferenciaService.findAllPreferenciasByUsuario(idUsuario);
    }

    @PUT
    @Path("/{id}")
    public Response update(@PathParam("id") String id, @Valid PreferenciaRequestDTO dto) {
        UUID idUsuario = getUserId();
        try {
            UUID uuid = UUID.fromString(id);
            PreferenciaResponseDTO updatedPreferencia = preferenciaService.updatePreferencia(idUsuario, uuid, dto);
            return Response.ok(updatedPreferencia).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity("ID inválido.").build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        } catch (ForbiddenException e) {
            return Response.status(Response.Status.FORBIDDEN).entity(e.getMessage()).build();
        }
    }
}