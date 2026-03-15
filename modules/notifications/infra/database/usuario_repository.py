"""Repositório para busca de usuários com preferências em batch."""

from __future__ import annotations

import json

from infra.database.postgres import get_connection


def get_users_with_preferences_batch(
    pairs: list[tuple[str, str]],
) -> dict[tuple[str, str], list[dict]]:
    """
    Busca usuários inscritos para cada par (id_evento, id_cidade).
    Retorna dict[(id_evento, id_cidade)] -> list[user_dict com canais_preferidos].
    """
    if not pairs:
        return {}

    unique_pairs = list(dict.fromkeys(pairs))
    values_ph = ", ".join(["(%s::uuid, %s::uuid)"] * len(unique_pairs))
    flat = [v for p in unique_pairs for v in p]

    query = f"""
    SELECT
        u.id::text,
        u.nome,
        u.email,
        u.whatsapp,
        p.personalizavel,
        p.valor,
        p.id_evento::text,
        p.id_cidade::text,
        COALESCE(
            (SELECT json_agg(json_build_object('id', c.id::text, 'nomeCanal', c.nome_canal))
             FROM usuario_canais_preferidos ucp
             JOIN canais c ON c.id = ucp.id_canal
             WHERE ucp.id_usuario = u.id),
            '[]'::json
        )::text as canais_preferidos
    FROM usuarios u
    JOIN preferencias p ON p.id_usuario = u.id
    WHERE (p.id_evento, p.id_cidade) IN (VALUES {values_ph})
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, flat)
            rows = cur.fetchall()

    result: dict[tuple[str, str], list[dict]] = {p: [] for p in unique_pairs}
    for row in rows:
        uid, nome, email, whatsapp, personalizavel, valor, id_evento, id_cidade, canais_json = row
        canais = json.loads(canais_json) if canais_json else []
        key = (id_evento, id_cidade)
        if key in result:
            result[key].append({
                "id": uid,
                "nome": nome,
                "email": email,
                "whatsapp": whatsapp,
                "personalizavel": personalizavel or False,
                "valor": float(valor) if valor is not None else None,
                "canais_preferidos": canais,
            })

    return result
