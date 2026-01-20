package org.ufg.resource;

import jakarta.validation.Valid;
import org.ufg.dto.*;
import org.ufg.service.UsuarioService;
import org.ufg.mapper.UsuarioMapper;

import jakarta.annotation.security.PermitAll;
import jakarta.annotation.security.RolesAllowed;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.Context;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.core.SecurityContext;
import org.eclipse.microprofile.jwt.JsonWebToken;

import java.util.List;
import java.util.UUID;

@Path("/usuarios")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class UsuarioResource {

    @Inject
    UsuarioService usuarioService;

    @Inject
    UsuarioMapper usuarioMapper;

    @Inject
    JsonWebToken jwt;

    @Context
    SecurityContext securityContext;


    @POST
    @Path("/login")
    @PermitAll
    public Response login(LoginRequestDTO loginDto) {
        LoginResponseDTO response = usuarioService.authenticate(
                loginDto.getEmail(),
                loginDto.getSenha()
        );

        return Response.ok(response).build();
    }

    @POST
    @PermitAll
    public Response criar(UsuarioRequestDTO usuarioDto) {
        boolean isCreationByAdmin = securityContext.getUserPrincipal() != null
                && securityContext.isUserInRole("ADMIN");

        UsuarioResponseDTO responseDto = usuarioService.criarUsuario(usuarioDto, isCreationByAdmin);

        return Response.status(Response.Status.CREATED).entity(responseDto).build();
    }


    @GET
    @RolesAllowed({"ADMIN"})
    public List<UsuarioResponseDTO> listarTodos() {
        return usuarioService.listarTodos();
    }

    @GET
    @Path("/{id}")
    @RolesAllowed({"ADMIN", "CLIENTE"})
    public Response buscarPorId(@PathParam("id") UUID id) {

        if (securityContext.isUserInRole("CLIENTE") && !isTargetIdSelf(id)) {
            throw new ForbiddenException("Acesso negado. Você só pode consultar o seu próprio registro.");
        }

        UsuarioResponseDTO responseDto = usuarioService.buscarUsuarioPorId(id);

        return Response.ok(responseDto).build();
    }

    @GET
    @Path("/preferencia/evento/{idEvento}")
    @RolesAllowed("ADMIN")
    public Response findByEvento(@PathParam("idEvento") String idEvento) {
        UUID eventoUuid;
        try {
            eventoUuid = UUID.fromString(idEvento);
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity("ID do evento inválido.")
                    .build();
        }

        List<UsuarioResponseDTO> usuarios = usuarioService.findUsuariosByEvento(eventoUuid);

        return Response.ok(usuarios).build();
    }

    @PUT
    @Path("/meu-perfil")
    @RolesAllowed({"CLIENTE", "ADMIN"})
    public Response atualizarPerfilCompleto(@Valid PerfilUsuarioDTO perfilDto) {
        UUID idUsuario = getUserIdFromJwt();

        usuarioService.atualizarPerfilCompleto(idUsuario, perfilDto);

        return Response.ok("Perfil de notificações atualizado com sucesso.").build();
    }

    @PUT
    @Path("/{id}")
    @RolesAllowed({"ADMIN", "CLIENTE"})
    public Response atualizar(@PathParam("id") UUID id, UsuarioRequestDTO usuarioDto) {

        if (securityContext.isUserInRole("CLIENTE") && !isTargetIdSelf(id)) {
            throw new ForbiddenException("Acesso negado. Você só pode atualizar o seu próprio registro.");
        }

        UsuarioResponseDTO responseDto = usuarioService.atualizarUsuario(id, usuarioDto);

        return Response.ok(responseDto).build();
    }


    @PATCH
    @Path("/{id}/nivelAcesso")
    @RolesAllowed({"ADMIN"}) // Somente ADMIN pode chamar
    public Response atualizarNivelAcesso(@PathParam("id") UUID id, String nivelAcesso) {
        UsuarioResponseDTO responseDto = usuarioService.atualizarNivelAcesso(id, nivelAcesso);

        return Response.ok(responseDto).build();
    }

    @DELETE
    @Path("/{id}")
    @RolesAllowed({"ADMIN"})
    public Response deletar(@PathParam("id") UUID id) {
        usuarioService.deletarUsuario(id);
        return Response.noContent().build();
    }

    private boolean isTargetIdSelf(UUID targetId) {
        try {
            UUID loggedUserId = UUID.fromString(jwt.getSubject());
            return loggedUserId.equals(targetId);
        } catch (Exception e) {
            return false;
        }
    }

    @GET
    @Path("/preferencia/evento/{idEvento}/cidade/{idCidade}")
    @RolesAllowed("ADMIN")
    public Response findByEventoAndCidade(
            @PathParam("idEvento") String idEvento,
            @PathParam("idCidade") String idCidade) {

        UUID eventoUuid;
        UUID cidadeUuid;
        try {
            eventoUuid = UUID.fromString(idEvento);
            cidadeUuid = UUID.fromString(idCidade);
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity("IDs de evento ou cidade inválidos.")
                    .build();
        }

        List<UsuarioResponseDTO> usuarios = usuarioService.findUsuariosByEventoAndCidade(eventoUuid, cidadeUuid);
        return Response.ok(usuarios).build();
    }

    @GET
    @Path("/preferencia/evento/{idEvento}/cidade/{idCidade}/Detalhado")
    @RolesAllowed("ADMIN")
    public Response findByEventoAndCidadeDetalhado(
            @PathParam("idEvento") String idEvento,
            @PathParam("idCidade") String idCidade) {

        UUID eventoUuid;
        UUID cidadeUuid;
        try {
            eventoUuid = UUID.fromString(idEvento);
            cidadeUuid = UUID.fromString(idCidade);
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity("IDs de evento ou cidade inválidos.")
                    .build();
        }

        List<UsuarioDetalhadoResponseDTO> usuarios = usuarioService.findUsuariosDetalhadoByEventoAndCidade(eventoUuid, cidadeUuid);
        return Response.ok(usuarios).build();
    }

    private UUID getUserIdFromJwt() {
        try {
            return UUID.fromString(jwt.getSubject());
        } catch (Exception e) {
            throw new ForbiddenException("Token JWT inválido ou usuário não autenticado.");
        }
    }
}