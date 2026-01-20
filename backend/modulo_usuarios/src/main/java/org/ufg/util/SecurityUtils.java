package org.ufg.util;

import java.util.UUID;
import java.util.Set;

import jakarta.enterprise.context.ApplicationScoped;

/**
 * Interface de utilidade de segurança para abstrair operações críticas de segurança.
 * A implementação real desta interface deve utilizar as extensões do Quarkus
 * como quarkus-elytron-security-properties para hashing/verificação de senha
 * e quarkus-smallrye-jwt para geração de tokens.
 */
// A anotação @ApplicationScoped garante que o CDI a injete no service.
@ApplicationScoped
public interface SecurityUtils {

    /**
     * Gera o hash seguro da senha bruta (raw).
     * Deve usar algoritmos modernos como BCrypt.
     * @param rawPassword A senha em texto claro.
     * @return O hash seguro da senha.
     */
    String hashPassword(String rawPassword);

    /**
     * Verifica se a senha bruta (raw) corresponde ao hash armazenado.
     * @param rawPassword A senha em texto claro fornecida pelo usuário.
     * @param hashedPassword O hash da senha armazenado no banco de dados.
     * @return True se as senhas coincidirem, false caso contrário.
     */
    boolean verifyPassword(String rawPassword, String hashedPassword);

    /**
     * Gera um JSON Web Token (JWT) assinado com base nas informações do usuário.
     * @param userId O UUID do usuário (irá para a claim 'sub').
     * @param email O email do usuário (útil para outras claims).
     * @param roles Os níveis de acesso do usuário (irá para a claim 'groups' ou 'roles').
     * @return O JWT como String.
     */
    String generateJwt(UUID userId, String email, Set<String> roles);
}