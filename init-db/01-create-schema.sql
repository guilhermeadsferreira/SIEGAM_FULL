-- Criação das tabelas do SIGEDAM
-- Este arquivo é executado automaticamente pelo PostgreSQL Docker ao iniciar

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(45),
    whatsapp VARCHAR(45),
    data_criacao TIMESTAMP NOT NULL,
    data_ultima_edicao DATE NOT NULL,
    senha VARCHAR(100) NOT NULL,
    login_token VARCHAR(1024),
    nivel_acesso VARCHAR(45) NOT NULL
);

-- Tabela de canais de comunicação
CREATE TABLE IF NOT EXISTS canais (
    id UUID PRIMARY KEY,
    nome_canal VARCHAR(45) NOT NULL,
    data_inclusao DATE NOT NULL
);

-- Tabela de cidades
CREATE TABLE IF NOT EXISTS cidades (
    id UUID PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

-- Tabela de eventos
CREATE TABLE IF NOT EXISTS eventos (
    id UUID PRIMARY KEY,
    nome_evento VARCHAR(50) NOT NULL,
    personalizavel BOOLEAN NOT NULL,
    horario TIMESTAMP NOT NULL
);

-- Tabela de possíveis status
CREATE TABLE IF NOT EXISTS possiveis_status (
    id UUID PRIMARY KEY,
    nome_status VARCHAR(45) NOT NULL,
    id_canal UUID NOT NULL,
    FOREIGN KEY (id_canal) REFERENCES canais(id)
);

-- Tabela de preferências
CREATE TABLE IF NOT EXISTS preferencias (
    id UUID PRIMARY KEY,
    id_usuario UUID NOT NULL,
    id_evento UUID NOT NULL,
    id_cidade UUID NOT NULL,
    data_criacao DATE NOT NULL,
    data_ultima_edicao DATE NOT NULL,
    valor DECIMAL(15,6),
    personalizavel BOOLEAN,
    id_canal UUID,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_evento) REFERENCES eventos(id),
    FOREIGN KEY (id_cidade) REFERENCES cidades(id),
    FOREIGN KEY (id_canal) REFERENCES canais(id)
);

-- Tabela de junção para canais preferidos dos usuários
CREATE TABLE IF NOT EXISTS usuario_canais_preferidos (
    id_usuario UUID NOT NULL,
    id_canal UUID NOT NULL,
    PRIMARY KEY (id_usuario, id_canal),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_canal) REFERENCES canais(id)
);

-- Tabela de avisos
CREATE TABLE IF NOT EXISTS avisos (
    id UUID PRIMARY KEY,
    id_evento UUID NOT NULL,
    id_cidade UUID NOT NULL,
    valor DECIMAL(15,6),
    data_geracao DATE NOT NULL,
    data_referencia DATE NOT NULL,
    valor_limite DECIMAL(15,6),
    unidade_medida VARCHAR(45) NOT NULL,
    diferenca DECIMAL(15,6) NOT NULL,
    horario TIME,
    segundos DECIMAL(15,6),
    FOREIGN KEY (id_evento) REFERENCES eventos(id),
    FOREIGN KEY (id_cidade) REFERENCES cidades(id)
);

-- Tabela de envios
CREATE TABLE IF NOT EXISTS envios (
    id UUID PRIMARY KEY,
    id_aviso UUID NOT NULL,
    id_usuario_destinatario UUID NOT NULL,
    id_canal UUID NOT NULL,
    id_status UUID NOT NULL,
    FOREIGN KEY (id_aviso) REFERENCES avisos(id),
    FOREIGN KEY (id_usuario_destinatario) REFERENCES usuarios(id),
    FOREIGN KEY (id_canal) REFERENCES canais(id),
    FOREIGN KEY (id_status) REFERENCES possiveis_status(id)
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_pref_usuario ON preferencias(id_usuario);
CREATE INDEX IF NOT EXISTS idx_pref_evento ON preferencias(id_evento);
CREATE INDEX IF NOT EXISTS idx_pref_cidade ON preferencias(id_cidade);
CREATE INDEX IF NOT EXISTS idx_pref_canal ON preferencias(id_canal);
CREATE INDEX IF NOT EXISTS idx_pref_evento_cidade ON preferencias(id_evento, id_cidade);
CREATE INDEX IF NOT EXISTS idx_avisos_cidade ON avisos(id_cidade);
CREATE INDEX IF NOT EXISTS idx_envios_usuario ON envios(id_usuario_destinatario);
