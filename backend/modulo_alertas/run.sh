#!/bin/bash

# Arquivo deve estar na pasta do modulo_alertas
# Carregar .env
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "Variáveis carregadas do arquivo.env local."
else
    echo "AVISO: Arquivo .env não encontrado no diretório!"
fi

echo "Executando script em $(date)"

source venv/bin/activate
python3 src/alert_generator.py

echo "Script finalizado em $(date) com código de saída $?"