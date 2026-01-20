package org.ufg.resource;

import jakarta.annotation.security.RolesAllowed;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.ufg.dto.EventoRequestDTO;
import org.ufg.dto.EventoResponseDTO;
import org.ufg.service.EventoService;

import java.net.URI;
import java.util.List;
import java.util.UUID;

@Path("/eventos")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@RolesAllowed("ADMIN")
public class EventoResource {

    @Inject
    EventoService eventoService;

    @POST
    public Response create(@Valid EventoRequestDTO dto) {
        try {
            EventoResponseDTO newEvento = eventoService.createEvento(dto);
            return Response.created(URI.create("/eventos/" + newEvento.getId()))
                    .entity(newEvento)
                    .build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity(e.getMessage()).build();
        }
    }

    @GET
    public List<EventoResponseDTO> findAll() {
        return eventoService.findAllEventos();
    }

    @GET
    @Path("/{id}")
    public Response findById(@PathParam("id") String id) {
        try {
            UUID uuid = UUID.fromString(id);
            EventoResponseDTO evento = eventoService.findEventoById(uuid);
            return Response.ok(evento).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity("ID inválido.").build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        }
    }

    @PUT
    @Path("/{id}")
    public Response update(@PathParam("id") String id, @Valid EventoRequestDTO dto) {
        try {
            UUID uuid = UUID.fromString(id);
            EventoResponseDTO updatedEvento = eventoService.updateEvento(uuid, dto);
            return Response.ok(updatedEvento).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity(e.getMessage()).build();
        } catch (NotFoundException e) {
            return Response.status(Response.Status.NOT_FOUND).entity(e.getMessage()).build();
        }
    }
}