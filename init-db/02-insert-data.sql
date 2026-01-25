-- Dados iniciais - Usuários
INSERT INTO usuarios (id, nome, email, whatsapp, data_criacao, data_ultima_edicao, senha, nivel_acesso)
VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Admin Principal',
    'admin@admin.com',
    '62999999999',
    CURRENT_TIMESTAMP,
    CURRENT_DATE,
    '$2a$12$rvgX1ZbqhzUyO0X99HroXe/TVWkZ4TnYvjaqiyZGvDCAOSFiADGhy',
    'ADMIN'
)
ON CONFLICT DO NOTHING;

INSERT INTO usuarios (id, nome, email, whatsapp, data_criacao, data_ultima_edicao, senha, nivel_acesso)
VALUES (
    'b1eebc99-1c0b-4ef8-bb6d-7bb9bd380a22',
    'Cliente Teste',
    'cliente@cliente.com',
    '62888888888',
    CURRENT_TIMESTAMP,
    CURRENT_DATE,
    '$2a$12$rvgX1ZbqhzUyO0X99HroXe/TVWkZ4TnYvjaqiyZGvDCAOSFiADGhy',
    'CLIENTE'
)
ON CONFLICT DO NOTHING;

-- Dados iniciais - Canais
INSERT INTO canais (data_inclusao, id, nome_canal) VALUES
	 (CURRENT_TIMESTAMP, '272d6a2d-e0d1-4fa9-abab-055131c2a4cc', 'Whatsapp'),
	 (CURRENT_TIMESTAMP, 'ed3f001d-655e-428a-9c9f-566e9d4f1203', 'Email')
ON CONFLICT DO NOTHING;

-- Dados iniciais - Cidades (Goiás)
INSERT INTO cidades (id, nome) VALUES
	 ('38732ef2-b776-483a-b04f-b4b634db446f', 'Abadia de Goiás'),
	 ('55fc8533-03eb-4180-8e9f-b2c9b2849689', 'Abadiânia'),
	 ('39b0899b-3807-46a1-9031-d4531cbb0e66', 'Acreúna'),
	 ('768f1fd6-0f59-429d-b06b-da3897d70470', 'Adelândia'),
	 ('d39aa33c-8f23-4da3-8c53-b3197297efe5', 'Água Fria de Goiás'),
	 ('46f2b61f-d644-4eff-abf4-8102357eb528', 'Água Limpa'),
	 ('b26e3338-27d3-41fe-b56a-32b865eecfd9', 'Águas Lindas de Goiás'),
	 ('a0b8ed09-db82-40b4-8dc5-6efd086dcb53', 'Alexânia'),
	 ('139494e5-ffad-4271-8633-998e0b2bcad3', 'Aloândia'),
	 ('f5be9fd0-75ec-4c67-a04a-967b9200a7ec', 'Alto Horizonte')
ON CONFLICT DO NOTHING;
