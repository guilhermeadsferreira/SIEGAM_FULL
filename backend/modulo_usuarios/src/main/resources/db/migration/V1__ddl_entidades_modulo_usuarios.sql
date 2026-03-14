-- DDL PostgreSQL - Módulo Usuários
-- Ordem: tabelas sem FK primeiro, depois tabelas com dependências

-- Extensão para UUID (se não existir)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- Tabelas independentes (sem FKs)
-- =============================================================================

CREATE TABLE IF NOT EXISTS cidades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS canais (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome_canal VARCHAR(45) NOT NULL,
    data_inclusao DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS eventos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome_evento VARCHAR(50) NOT NULL,
    personalizavel BOOLEAN NOT NULL,
    horario TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(45),
    whatsapp VARCHAR(45),
    data_criacao TIMESTAMP NOT NULL,
    data_ultima_edicao DATE NOT NULL,
    senha VARCHAR(100) NOT NULL,
    login_token VARCHAR(1024),
    nivel_acesso VARCHAR(45) NOT NULL
);

-- =============================================================================
-- Tabelas com FKs (ordem por dependência)
-- =============================================================================

CREATE TABLE IF NOT EXISTS possiveis_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome_status VARCHAR(45) NOT NULL,
    id_canal UUID NOT NULL,
    CONSTRAINT fk_possivel_status_canal FOREIGN KEY (id_canal) REFERENCES canais(id)
);

CREATE TABLE IF NOT EXISTS avisos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_evento UUID NOT NULL,
    valor NUMERIC(15, 6),
    data_geracao DATE NOT NULL,
    data_referencia DATE NOT NULL,
    id_cidade UUID NOT NULL,
    valor_limite NUMERIC(15, 6),
    unidade_medida VARCHAR(45) NOT NULL,
    diferenca NUMERIC(15, 6) NOT NULL,
    horario TIME,
    segundos NUMERIC(15, 6),
    CONSTRAINT fk_aviso_evento FOREIGN KEY (id_evento) REFERENCES eventos(id),
    CONSTRAINT fk_aviso_cidade FOREIGN KEY (id_cidade) REFERENCES cidades(id)
);

CREATE TABLE IF NOT EXISTS preferencias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario UUID NOT NULL,
    id_evento UUID NOT NULL,
    id_cidade UUID NOT NULL,
    data_criacao DATE NOT NULL,
    data_ultima_edicao DATE NOT NULL,
    valor NUMERIC(15, 6),
    personalizavel BOOLEAN,
    id_canal UUID,
    CONSTRAINT fk_preferencia_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    CONSTRAINT fk_preferencia_evento FOREIGN KEY (id_evento) REFERENCES eventos(id),
    CONSTRAINT fk_preferencia_cidade FOREIGN KEY (id_cidade) REFERENCES cidades(id),
    CONSTRAINT fk_preferencia_canal FOREIGN KEY (id_canal) REFERENCES canais(id)
);

CREATE TABLE IF NOT EXISTS envios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_canal UUID NOT NULL,
    id_aviso UUID NOT NULL,
    id_usuario_destinatario UUID NOT NULL,
    id_status UUID NOT NULL,
    CONSTRAINT fk_envio_canal FOREIGN KEY (id_canal) REFERENCES canais(id),
    CONSTRAINT fk_envio_aviso FOREIGN KEY (id_aviso) REFERENCES avisos(id),
    CONSTRAINT fk_envio_usuario FOREIGN KEY (id_usuario_destinatario) REFERENCES usuarios(id),
    CONSTRAINT fk_envio_status FOREIGN KEY (id_status) REFERENCES possiveis_status(id)
);

-- Tabela de junção ManyToMany: usuarios <-> canais (canais preferidos)
CREATE TABLE IF NOT EXISTS usuario_canais_preferidos (
    id_usuario UUID NOT NULL,
    id_canal UUID NOT NULL,
    PRIMARY KEY (id_usuario, id_canal),
    CONSTRAINT fk_ucp_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    CONSTRAINT fk_ucp_canal FOREIGN KEY (id_canal) REFERENCES canais(id)
);

-- =============================================================================
-- Índices (preferencias - conforme entidade)
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_pref_evento_cidade ON preferencias(id_evento, id_cidade);
CREATE INDEX IF NOT EXISTS idx_pref_usuario ON preferencias(id_usuario);
CREATE INDEX IF NOT EXISTS idx_pref_evento ON preferencias(id_evento);
CREATE INDEX IF NOT EXISTS idx_pref_cidade ON preferencias(id_cidade);
CREATE INDEX IF NOT EXISTS idx_pref_canal ON preferencias(id_canal);

-- Índices úteis em FKs para consultas e joins
CREATE INDEX IF NOT EXISTS idx_avisos_id_evento ON avisos(id_evento);
CREATE INDEX IF NOT EXISTS idx_avisos_id_cidade ON avisos(id_cidade);
CREATE INDEX IF NOT EXISTS idx_envios_id_canal ON envios(id_canal);
CREATE INDEX IF NOT EXISTS idx_envios_id_aviso ON envios(id_aviso);
CREATE INDEX IF NOT EXISTS idx_envios_id_usuario ON envios(id_usuario_destinatario);
CREATE INDEX IF NOT EXISTS idx_envios_id_status ON envios(id_status);
CREATE INDEX IF NOT EXISTS idx_possiveis_status_id_canal ON possiveis_status(id_canal);
