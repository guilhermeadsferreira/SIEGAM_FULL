-- seed_e2e.sql
-- Dados de teste para E2E controlado.
-- Executar após a stack estar no ar (schema.sql + seed.sql já aplicados).
-- Idempotente: ON CONFLICT DO NOTHING em todas as inserções.

-- =============================================================================
-- 1. Canais
-- =============================================================================
INSERT INTO canais (id, nome_canal, data_inclusao) VALUES
  ('00000000-0000-0000-0000-000000000001', 'whatsapp', CURRENT_DATE),
  ('00000000-0000-0000-0000-000000000002', 'email',    CURRENT_DATE)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- 2. Status possíveis por canal
-- =============================================================================
INSERT INTO possiveis_status (id, nome_status, id_canal) VALUES
  ('00000000-0000-0000-0001-000000000001', 'Sucesso', '00000000-0000-0000-0000-000000000001'),
  ('00000000-0000-0000-0001-000000000002', 'Falha',   '00000000-0000-0000-0000-000000000001'),
  ('00000000-0000-0000-0001-000000000003', 'Sucesso', '00000000-0000-0000-0000-000000000002'),
  ('00000000-0000-0000-0001-000000000004', 'Falha',   '00000000-0000-0000-0000-000000000002')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- 3. Usuários de teste
-- =============================================================================
INSERT INTO usuarios (id, nome, email, whatsapp, data_criacao, data_ultima_edicao, senha, nivel_acesso)
VALUES
  (
    '00000000-0000-0000-0004-000000000001',
    'Teste E2E - Usuario 1',
    'teste1@e2e.local',
    '62996401335',
    NOW(), CURRENT_DATE, 'hash-nao-usado', 'admin'
  ),
  (
    '00000000-0000-0000-0004-000000000002',
    'Teste E2E - Usuario 2',
    'teste2@e2e.local',
    '62985804130',
    NOW(), CURRENT_DATE, 'hash-nao-usado', 'admin'
  )
ON CONFLICT DO NOTHING;

-- =============================================================================
-- 4. Vincular usuários ao canal WhatsApp
-- =============================================================================
INSERT INTO usuario_canais_preferidos (id_usuario, id_canal)
VALUES
  ('00000000-0000-0000-0004-000000000001', '00000000-0000-0000-0000-000000000001'),
  ('00000000-0000-0000-0004-000000000002', '00000000-0000-0000-0000-000000000001')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- 5. Preferências: ambos os usuários para todos os alertas em Goiânia
-- Usa subquery para buscar os UUIDs reais (gerados com gen_random_uuid no seed.sql).
-- =============================================================================
-- 5a. Preferências sem personalização: temperatura alta, temperatura baixa, chuva
--     (filtro sempre envia para personalizavel=false)
INSERT INTO preferencias (id, id_usuario, id_evento, id_cidade, data_criacao, data_ultima_edicao, personalizavel)
SELECT
  gen_random_uuid(),
  u.id,
  e.id,
  c.id,
  CURRENT_DATE,
  CURRENT_DATE,
  false
FROM
  (VALUES
    ('00000000-0000-0000-0004-000000000001'::uuid),
    ('00000000-0000-0000-0004-000000000002'::uuid)
  ) AS u(id)
  CROSS JOIN eventos e
  CROSS JOIN cidades c
WHERE
  c.nome = 'Goiânia'
  AND e.nome_evento IN ('temperatura alta', 'temperatura baixa', 'chuva')
ON CONFLICT DO NOTHING;

-- 5b. Preferências personalizadas: vento (threshold=12 km/h, alinhado com ETL)
--     Envia quando valor > 12 km/h (qualquer vento acima do mínimo do ETL)
INSERT INTO preferencias (id, id_usuario, id_evento, id_cidade, data_criacao, data_ultima_edicao, personalizavel, valor)
SELECT
  gen_random_uuid(),
  u.id,
  e.id,
  c.id,
  CURRENT_DATE,
  CURRENT_DATE,
  true,
  12.0
FROM
  (VALUES
    ('00000000-0000-0000-0004-000000000001'::uuid),
    ('00000000-0000-0000-0004-000000000002'::uuid)
  ) AS u(id)
  CROSS JOIN eventos e
  CROSS JOIN cidades c
WHERE
  c.nome = 'Goiânia'
  AND e.nome_evento = 'vento'
ON CONFLICT DO NOTHING;

-- 5c. Preferências personalizadas: umidade baixa (threshold=60%, alinhado com ETL)
--     Envia quando valor < 60% (qualquer umidade abaixo do mínimo do ETL)
INSERT INTO preferencias (id, id_usuario, id_evento, id_cidade, data_criacao, data_ultima_edicao, personalizavel, valor)
SELECT
  gen_random_uuid(),
  u.id,
  e.id,
  c.id,
  CURRENT_DATE,
  CURRENT_DATE,
  true,
  60.0
FROM
  (VALUES
    ('00000000-0000-0000-0004-000000000001'::uuid),
    ('00000000-0000-0000-0004-000000000002'::uuid)
  ) AS u(id)
  CROSS JOIN eventos e
  CROSS JOIN cidades c
WHERE
  c.nome = 'Goiânia'
  AND e.nome_evento = 'umidade baixa'
ON CONFLICT DO NOTHING;
