package org.ufg.util;

import io.quarkus.elytron.security.common.BcryptUtil;
import io.smallrye.jwt.build.Jwt;

import jakarta.enterprise.context.ApplicationScoped;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Set;
import java.util.UUID;

@ApplicationScoped
public class SecurityUtilsImpl implements SecurityUtils {

    private static final long EXPIRATION_TIME_HOURS = 24L;

    private static final String JWT_ISSUER = "org.ufg.api";


    @Override
    public String hashPassword(String rawPassword) {
        return BcryptUtil.bcryptHash(rawPassword);
    }

    @Override
    public boolean verifyPassword(String rawPassword, String hashedPassword) {
        return BcryptUtil.matches(rawPassword, hashedPassword);
    }


    @Override
    public String generateJwt(UUID userId, String email, Set<String> roles) {


        Instant expiration = Instant.now().plus(EXPIRATION_TIME_HOURS, ChronoUnit.HOURS);

        return Jwt.issuer(JWT_ISSUER)
                .subject(userId.toString())
                .upn(email)
                .groups(roles)
                .issuedAt(Instant.now())
                .expiresAt(expiration)
                .sign();
    }
}