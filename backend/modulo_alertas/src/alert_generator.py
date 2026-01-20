import os
import json
from datetime import datetime
from meteogram_parser import MeteogramParser
from file_utils import clean_old_files, download_meteogram_file
import sys
import math
from datetime import date, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from config_parser import ConfigParser
from http_client import HttpClient

minimum_diff_temperature_min = 3.0


class AlertGenerator:
    """
    Classe para gerar alertas com base em dados meteorológicos.
    Utiliza ConfigParser e MeteogramParser para obter dados e configurações.
    Monitora temperatura e umidade, gerando alertas únicos por cidade e tipo.
    """
    
    def __init__(self, config_path=None, meteogram_path=None):
        """
        Inicializa o gerador de alertas.
        
        Args:
            config_path (str, optional): Caminho para o arquivo de configuração
            meteogram_path (str, optional): Caminho para o arquivo de meteograma
            alert_service (object, optional): Serviço para buscar usuários para notificação
        """
        # Inicializar componentes
        self.config = ConfigParser(config_path)
        self.config.parse()
        self.config_map = self.config.get_config_map()
        
        # Configurar o parser de meteograma
        self.meteogram_path = meteogram_path
        self.meteogram_parser = None
        self.meteogram_data = None
        
        # Armazenar alertas gerados (para evitar duplicação)
        # Estrutura: {cidade: {tipo_alerta: dados_alerta}}
        self.alerts = {}
        
        # Inicializar o parser de meteograma se o caminho foi fornecido
        if self.meteogram_path:
            self._init_meteogram_parser()
        else:
            # Tentar encontrar automaticamente o arquivo de meteograma
            self._find_meteogram_file()
    
    def _find_meteogram_file(self):
        """
        Tenta encontrar o arquivo de meteograma mais recente na pasta padrão.
        
        Raises:
            FileNotFoundError: Se nenhum arquivo de meteograma for encontrado
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tmp_dir = os.path.abspath(os.path.join(current_dir, "tmp_files"))
        
        if not os.path.exists(tmp_dir):
            error_msg = f"Diretório de arquivos temporários não encontrado: {tmp_dir}"
            print(f"ERRO: {error_msg}")
            raise FileNotFoundError(error_msg)
        
        meteogram_files = [
            os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir)
            if f.startswith("HST") and f.endswith("MeteogramASC.out")
        ]
        
        if not meteogram_files:
            error_msg = f"Nenhum arquivo de meteograma encontrado em: {tmp_dir}"
            print(f"ERRO: {error_msg}")
            raise FileNotFoundError(error_msg)
        
        # Ordenar por data de modificação (mais recente primeiro)
        meteogram_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        self.meteogram_path = meteogram_files[0]
        print(f"Arquivo de meteograma encontrado: {self.meteogram_path}")
        
        try:
            self._init_meteogram_parser()
        except (FileNotFoundError, ValueError) as e:
            print(f"ERRO ao inicializar parser com o arquivo encontrado: {str(e)}")
            raise
    
    def _init_meteogram_parser(self):
        """
        Inicializa o parser de meteograma com o arquivo definido.
        
        Raises:
            FileNotFoundError: Se o arquivo de meteograma não for encontrado
            ValueError: Se o caminho do arquivo não for fornecido
        """
        try:
            self.meteogram_parser = MeteogramParser(self.meteogram_path)
            print(f"Parser de meteograma inicializado com o arquivo: {self.meteogram_path}")
        except (FileNotFoundError, ValueError) as e:
            print(f"ERRO: {str(e)}")
            self.meteogram_parser = None
            raise
    
    def kelvin_to_celsius(self, temp_k):
        """
        Converte temperatura de Kelvin para Celsius.
        
        Args:
            temp_k (float): Temperatura em Kelvin
            
        Returns:
            float: Temperatura em Celsius
        """
        return temp_k - 273.15
    
    def calculate_relative_humidity(self, t_max, td_max):
        """
        Calcula a umidade relativa usando a fórmula de Magnus-Tetens.
        
        Args:
            t_max (float): Temperatura máxima em Celsius
            td_max (float): Temperatura do ponto de orvalho em Celsius
            
        Returns:
            float: Umidade relativa em porcentagem (0-100)
        """
        # Constantes para a fórmula de Magnus-Tetens
        a = 17.27
        b = 237.7
        
        # Calcular pressão de saturação para temperatura e ponto de orvalho
        es_t = 6.112 * math.exp((a * t_max) / (t_max + b))
        es_td = 6.112 * math.exp((a * td_max) / (td_max + b))
        
        # Calcular umidade relativa em porcentagem
        rh = (es_td / es_t) * 100
        
        # Limitar a umidade entre 0 e 100%
        return max(0, min(100, rh))
    
    def load_meteogram_data(self):
        """
        Carrega os dados do meteograma.
        
        Returns:
            dict: Dados do meteograma
            
        Raises:
            FileNotFoundError: Se nenhum arquivo de meteograma for encontrado
            Exception: Se ocorrer erro ao carregar os dados
        """
        if not self.meteogram_parser:
            if not self.meteogram_path:
                # Tentar encontrar um arquivo automaticamente
                self._find_meteogram_file()
            else:
                # Inicializar com o arquivo já definido
                self._init_meteogram_parser()
            
            if not self.meteogram_parser:
                error_msg = "Não foi possível inicializar o parser de meteograma"
                print(f"ERRO: {error_msg}")
                raise FileNotFoundError(error_msg)
        
        try:
            self.meteogram_data = self.meteogram_parser.parse()
            print(f"Dados do meteograma carregados: {len(self.meteogram_data)} polígonos encontrados")
            return self.meteogram_data
        except Exception as e:
            error_msg = f"Erro ao carregar dados do meteograma: {str(e)}"
            print(f"ERRO: {error_msg}")
            raise Exception(error_msg) from e

    def check_temperature_alerts(self, date=None):
        """
        Verifica temperaturas e retorna os valores máximos e mínimos encontrados.
        Ignora limiares configurados e apenas obtém o maior valor de temperatura máxima
        e o menor valor de temperatura mínima para cada cidade.
        
        Args:
            date (datetime, optional): Data para referência.
                Se None, usa a data atual.
        
        Returns:
            dict: Dicionário com alertas de temperatura (max e min) por cidade
        """
        if not self.meteogram_data:
            self.load_meteogram_data()
            if not self.meteogram_data:
                return {}
        
        # Se a data não for especificada, usar a data atual
        if date is None:
            date = datetime.now()
        
        alerts = {}
        
        # Para cada polígono na configuração
        for polygon_name, config_data in self.config_map.items():
            display_name = self.config.get_display_name(polygon_name)
            
            if not display_name:
                continue  # Pular se não tiver nome de exibição
            
            # Verificar se o polígono existe nos dados do meteograma
            if polygon_name not in self.meteogram_data:
                continue  # Pular se não tiver dados para este polígono
            
            time_data = self.meteogram_data[polygon_name]
            
            # Inicializar o alerta para esta cidade se ainda não existir
            if display_name not in alerts:
                alerts[display_name] = {}
            
            # Rastrear temperatura máxima e mínima
            max_temp_c = float('-inf')
            min_temp_c = float('inf')
            max_temp_data = None
            min_temp_data = None
            
            for seconds, values in time_data.items():
                if 'Tmax' in values and 'Tmin' in values:
                    # Converter de Kelvin para Celsius
                    temp_max_k = values['Tmax']
                    temp_min_k = values['Tmin']
                    temp_max_c = self.kelvin_to_celsius(temp_max_k)
                    temp_min_c = self.kelvin_to_celsius(temp_min_k)
                    
                    # Atualizar temperatura máxima
                    if temp_max_c > max_temp_c:
                        max_temp_c = temp_max_c
                        max_temp_data = {
                            'polygon_name': polygon_name,
                            'seconds': seconds,
                            'date': values.get('date', 'N/A'),
                            'temp_k': temp_max_k,
                            'temp_c': temp_max_c,
                        }
                    
                    # Atualizar temperatura mínima
                    if temp_min_c < min_temp_c:
                        min_temp_c = temp_min_c
                        min_temp_data = {
                            'polygon_name': polygon_name,
                            'seconds': seconds,
                            'date': values.get('date', 'N/A'),
                            'temp_k': temp_min_k,
                            'temp_c': temp_min_c,
                        }
            
            # Se encontrou dados, adicionar aos alertas
            if max_temp_data:
                alerts[display_name]['temperatura alta'] = {
                    'value': max_temp_data['temp_c'],
                    'value_k': max_temp_data['temp_k'],
                    'threshold': 0,
                    'difference': 0,
                    'date': max_temp_data['date'],
                    'seconds': max_temp_data['seconds'],
                    'polygon_name': polygon_name,
                    'unit': "°C"
                }
            
            if min_temp_data:
                alerts[display_name]['temperatura baixa'] = {
                    'value': min_temp_data['temp_c'],
                    'value_k': min_temp_data['temp_k'],
                    'threshold': 0,
                    'difference': 0,
                    'date': min_temp_data['date'],
                    'seconds': min_temp_data['seconds'],
                    'polygon_name': polygon_name,
                    'unit': "°C"
                }
        
        # Filtrar apenas as cidades com alertas
        return {city: data for city, data in alerts.items() if data}
    
    def check_humidity_alerts(self, min_threshold=60, max_threshold=90, date=None):
        """
        Verifica se há alertas de umidade baseados nos limiares especificados.
        Gera alertas apenas para umidade baixa (abaixo do limiar mínimo).
        Calcula a umidade relativa a partir de Tave e TDave usando a fórmula de Magnus-Tetens.
        
        Args:
            min_threshold (float): Limiar mínimo de umidade (%)
            max_threshold (float): Limiar máximo de umidade (%) - não utilizado
            date (datetime, optional): Data de referência
        
        Returns:
            dict: Dicionário com alertas de umidade por cidade
        """
        if not self.meteogram_data:
            self.load_meteogram_data()
            if not self.meteogram_data:
                return {}
        
        alerts = {}
        
        # Para cada polígono na configuração
        for polygon_name, config_data in self.config_map.items():
            display_name = self.config.get_display_name(polygon_name)
            
            if not display_name:
                continue  # Pular se não tiver nome de exibição
            
            # Verificar se o polígono existe nos dados do meteograma
            if polygon_name not in self.meteogram_data:
                continue  # Pular se não tiver dados para este polígono
            
            time_data = self.meteogram_data[polygon_name]
            
            # Inicializar o alerta para esta cidade se ainda não existir
            if display_name not in alerts:
                alerts[display_name] = {}
            
            # Verificar cada registro de tempo
            min_humidity = float('inf')
            min_humidity_data = None
            
            for seconds, values in time_data.items():
                # Verificar se temos os dados necessários para calcular a umidade relativa
                if 'Tave' in values and 'TDave' in values:
                    # Converter para Celsius se estão em Kelvin
                    t_ave_celsius = self.kelvin_to_celsius(values['Tave'])
                    td_ave_celsius = self.kelvin_to_celsius(values['TDave'])
                    
                    # Calcular a umidade relativa
                    humidity = self.calculate_relative_humidity(t_ave_celsius, td_ave_celsius)
                    
                    # Atualizar a umidade mínima
                    if humidity < min_humidity:
                        min_humidity = humidity
                        min_humidity_data = {
                            'polygon_name': polygon_name,
                            'seconds': seconds,
                            'date': values.get('date', 'N/A'),
                            'humidity': humidity,
                            'threshold': min_threshold,
                            'difference': humidity - min_threshold,
                            'tave': t_ave_celsius,
                            'tdave': td_ave_celsius
                        }
            
            # Verificar se há alertas de umidade baixa
            if min_humidity < min_threshold and min_humidity_data:
                alerts[display_name]['umidade baixa'] = {
                    'value': min_humidity,
                    'threshold': min_threshold,
                    'difference': min_humidity - min_threshold,
                    'date': min_humidity_data['date'],
                    'seconds': min_humidity_data['seconds'],
                    'polygon_name': polygon_name,
                    'unit': "%"
                }
                
                # Adicionar detalhes de temperatura se disponíveis
                if 'tave' in min_humidity_data and 'tdave' in min_humidity_data:
                    alerts[display_name]['umidade baixa']['tave'] = min_humidity_data['tave']
                    alerts[display_name]['umidade baixa']['tdave'] = min_humidity_data['tdave']
        
        # Filtrar apenas as cidades com alertas
        return {city: data for city, data in alerts.items() if data}
    
    def check_wind_alerts(self, max_threshold=11.08, date=None):
        """
        Verifica se há alertas de ventania baseados nos limiares especificados.
        Gera alertas para vento forte e ventanias acima de determinado valor.
        Calcula a força do vento partir de Umax e Vmax aplicando a fórmula de pitágoras.
        
        Args:
            max_threshold (float): Vento máximo em m/s^2 (limiar máximo) vento forte apartir de 12km/h = 3.33m/s
            date (datetime, optional): Data de referência
        
        Returns:
            dict: Dicionário com alertas de vento por cidade
        """

        # Carrega os dados do meteograma apenas uma vez
        data = self.meteogram_data
        if not data:
            self.load_meteogram_data()
            data = self.meteogram_data
            if not data:
                return {}

        alerts = {}

        # Cache de métodos e constantes para reduzir chamadas dinâmicas
        get_display = self.config.get_display_name
        get_data = data.get
        threshold = max_threshold

        # Loop sobre cada polígono configurado
        for polygon_name, config_data in self.config_map.items():
            display_name = get_display(polygon_name)
            if not display_name:
                continue  # Ignora se não houver nome legível configurado

            time_data = get_data(polygon_name)
            if not time_data:
                continue  # Ignora se não houver dados climáticos para este polígono

            # Controle do maior valor de vento (módulo) encontrado
            max_wind_sq = -1.0
            max_wind_seconds = None
            max_wind_date = None

            # Itera sobre os registros temporais (horas ou minutos)
            for seconds, values in time_data.items():
                u = values.get('Umax')
                v = values.get('Vmax')
                if u is None or v is None:
                    continue  # ignora se faltar dados vetoriais

                # Calcula a intensidade ao quadrado (U² + V²)
                wind_sq = u * u + v * v
                # Atualiza se ultrapassar o limiar e for maior que o anterior
                if wind_sq > threshold and wind_sq > max_wind_sq:
                    max_wind_sq = wind_sq
                    max_wind_seconds = seconds
                    max_wind_date = values.get('date', 'N/A')

            # Se encontrou valor acima do limite, gera o alerta
            if max_wind_sq > threshold:
                max_wind_kmh = self.convert_ms2_to_kmh(max_wind_sq)
                threshold_kmh = self.convert_ms2_to_kmh(threshold)
                alerts[display_name] = {
                    'vento': {
                        'value': max_wind_kmh,
                        'threshold': threshold_kmh,
                        'difference': max_wind_kmh - threshold_kmh,
                        'date': max_wind_date,
                        'seconds': max_wind_seconds,
                        'polygon_name': polygon_name,
                        'unit': "km/h"
                    }
                }

        # Retorna apenas as cidades que tiveram alertas
        return alerts

    
    def check_rain_alerts(self, max_threshold=15.0, date=None):
        """
        Verifica se há alertas de chuva intensa baseados nos limiares especificados.
        Gera alertas para precipitação acima de determinado valor (mm/h).
        
        Args:
            max_threshold (float): Limiar máximo de chuva em mm/h. Chuva intensa a partir de 15 mm/h.
            date (datetime, optional): Data de referência.
        
        Returns:
            dict: Dicionário com alertas de chuva intensa por cidade.
        """

        # Carrega os dados do meteograma, se ainda não estiverem disponíveis
        if not self.meteogram_data:
            self.load_meteogram_data()
            if not self.meteogram_data:
                return {}
        
        alerts = {}
        get_display = self.config.get_display_name  # cache do método
        threshold = max_threshold
        get_data = data.get  # cache do método de acesso

        # Itera sobre cada polígono na configuração
        for polygon_name, config_data in self.config_map.items():
            display_name = get_display(polygon_name)
            if not display_name:
                continue

            time_data = get_data(polygon_name)
            if not time_data:
                continue

            max_rain = -1.0
            max_rain_seconds = None
            max_rain_date = None

            # Iteração sobre os dados de tempo para encontrar a precipitação máxima
            for seconds, values in time_data.items():
                rain = values.get('PRECmax')
                if rain is None or rain <= threshold:
                    continue
                if rain > max_rain:
                    max_rain = rain
                    max_rain_seconds = seconds
                    max_rain_date = values.get('date', 'N/A')

            if max_rain > threshold:
                alerts[display_name] = {
                    'chuva': {
                        'value': max_rain,
                        'threshold': threshold,
                        'difference': max_rain - threshold,
                        'date': max_rain_date,
                        'seconds': max_rain_seconds,
                        'polygon_name': polygon_name,
                        'unit': "mm"
                    }
                }

        return alerts

    def generate_all_alerts(self):
        """
        Gera todos os alertas de temperatura e umidade.
        
        Returns:
            dict: Dicionário com todos os alertas por cidade e tipo
        """
        # Carregar dados se necessário
        if not self.meteogram_data:
            self.load_meteogram_data()
            if not self.meteogram_data:
                return {}
        
        # Obter alertas de temperatura
        temp_alerts = self.check_temperature_alerts()
        
        # Obter alertas de umidade
        humidity_alerts = self.check_humidity_alerts()

        # Obter alertas de vento
        wind_alerts = self.check_wind_alerts()
        
        # Obter alertas de chuva comentado temporariamente
        # rain_alerts = self.check_rain_alerts()

        # Combinar os alertas
        all_alerts = {}
        
        # Adicionar alertas de temperatura
        for city, alerts in temp_alerts.items():
            if city not in all_alerts:
                all_alerts[city] = {}
            all_alerts[city].update(alerts)
        
        # Adicionar alertas de umidade
        for city, alerts in humidity_alerts.items():
            if city not in all_alerts:
                all_alerts[city] = {}
            all_alerts[city].update(alerts)

        # Adicionar alertas de vento
        for city, alerts in wind_alerts.items():
            if city not in all_alerts:
                all_alerts[city] = {}
            all_alerts[city].update(alerts)

        # Adicionar alertas de chuva
        # for city, alerts in rain_alerts.items():
        #     if city not in all_alerts:
        #         all_alerts[city] = {}
        #     all_alerts[city].update(alerts)
        
        # Armazenar os alertas gerados
        self.alerts = all_alerts
        
        return all_alerts
    
    def get_alert_date(self, seconds):
        """
        Obtém a data completa do alerta baseada nos segundos.
        
        Args:
            seconds (int): Segundos desde meia-noite em UTC-0
            
        Returns:
            str: Data formatada como "DD/MM/YYYY"
        """
        time_info = self.seconds_to_hhmm(seconds)
        today = datetime.now()
        
        # Usar o dia calculado pela função seconds_to_hhmm
        alert_day = time_info['day']
        
        # Criar a data usando o dia calculado e o mês/ano atuais
        alert_date = today.replace(day=alert_day)
        
        return alert_date.strftime('%d/%m/%Y')

    def get_alerts_summary(self):
        """
        Retorna um resumo dos alertas gerados.
        
        Returns:
            str: Resumo formatado dos alertas
        """
        if not self.alerts:
            return "Nenhum alerta gerado"
        
        summary = "=== RESUMO DE ALERTAS ===\n"
        
        for city, city_alerts in self.alerts.items():
            summary += f"\nCidade: {city}\n"
            
            if 'temperatura alta' in city_alerts:
                alert = city_alerts['temperatura alta']
                temp_k = alert.get('value_k', 'N/A')
                
                if isinstance(temp_k, (int, float)):
                    summary += f"  - Temperatura alta: {alert['value']:.1f}°C ({temp_k:.1f}K)\n"
                else:
                    summary += f"  - Temperatura alta: {alert['value']:.1f}°C\n"
                    
                summary += f"    Limite: {alert['threshold']}°C\n"
                summary += f"    Diferença: {alert['difference']:.1f}°C\n"
                summary += f"    Segundos: {alert['seconds']}\n"
                summary += f"    Data: {self.get_alert_date(alert['seconds'])}\n"
                summary += f"    Horário: {self.seconds_to_hhmm(alert['seconds'])['formatted']}\n"
            
            if 'temperatura baixa' in city_alerts:
                alert = city_alerts['temperatura baixa']
                temp_k = alert.get('value_k', 'N/A')
                
                if isinstance(temp_k, (int, float)):
                    summary += f"  - Temperatura baixa: {alert['value']:.1f}°C ({temp_k:.1f}K)\n"
                else:
                    summary += f"  - Temperatura baixa: {alert['value']:.1f}°C\n"
                    
                summary += f"    Limite: {alert['threshold']}°C\n"
                summary += f"    Diferença: {alert['difference']:.1f}°C\n"
                summary += f"    Segundos: {alert['seconds']}\n"
                summary += f"    Data: {self.get_alert_date(alert['seconds'])}\n"
                summary += f"    Horário: {self.seconds_to_hhmm(alert['seconds'])['formatted']}\n"
            
            if 'umidade baixa' in city_alerts:
                alert = city_alerts['umidade baixa']
                summary += f"  - Umidade baixa: {alert['value']:.1f}% (limite: {alert['threshold']}%)\n"
                summary += f"    Diferença: {alert['difference']:.1f}%\n"
                
                # Adicionar informações de temperatura se disponíveis
                if 'tave' in alert and 'tdave' in alert:
                    summary += f"    Temperatura média (Tave): {alert['tave']:.1f}°C\n"
                    summary += f"    Temperatura ponto de orvalho (TDave): {alert['tdave']:.1f}°C\n"
                
                summary += f"    Segundos: {alert['seconds']}\n"
                summary += f"    Data: {self.get_alert_date(alert['seconds'])}\n"
                summary += f"    Horário: {self.seconds_to_hhmm(alert['seconds'])['formatted']}\n"
            
            if 'vento' in city_alerts:
                alert = city_alerts['vento']
                summary += f"  - Vento forte: {alert['value']:.1f} km/h (limite: {alert['threshold']:.1f} km/h)\n"
                summary += f"    Diferença: {alert['difference']:.1f} km/h\n"
                summary += f"    Segundos: {alert['seconds']}\n"
                summary += f"    Data: {self.get_alert_date(alert['seconds'])}\n"
                summary += f"    Horário: {self.seconds_to_hhmm(alert['seconds'])['formatted']}\n"

            if 'chuva' in city_alerts:
                alert = city_alerts['chuva']
                summary += f"  - Chuva intensa: {alert['value']:.1f} mm (limite: {alert['threshold']:.1f} mm)\n"
                summary += f"    Diferença: {alert['difference']:.1f} mm\n"
                summary += f"    Segundos: {alert['seconds']}\n"
                summary += f"    Data: {self.get_alert_date(alert['seconds'])}\n"
                summary += f"    Horário: {self.seconds_to_hhmm(alert['seconds'])['formatted']}\n"
        
        return summary
    
    def get_import_request(self, eventos: list, cidades: list) -> list:
        """
        Gera a lista de avisos (payload para /avisos/lote)
        com base nos alertas registrados em self.alerts.

        Args:
            eventos (list): Lista de eventos da API (cada item com 'id' e 'nomeEvento').
            cidades (list): Lista de cidades da API (cada item com 'id' e 'nome').

        Returns:
            list: Lista de dicionários compatíveis com AvisoDTO.
        """
        if not hasattr(self, "alerts") or not self.alerts:
            return []

        avisos = []

        for city_name, city_alerts in self.alerts.items():
            # Buscar cidade correspondente
            cidade = next((c for c in cidades if c["nome"].lower() == city_name.lower()), None)
            if not cidade:
                print(f"Cidade não encontrada: {city_name}")
                continue

            for alert_key, alert_data in city_alerts.items():
                # Exemplo: procurar evento relacionado
                evento = next(
                    (e for e in eventos if alert_key.lower() in e["nomeEvento"].lower()),
                    None
                )
                if not evento:
                    print(f"Evento não encontrado para alerta '{alert_key}' em {city_name}")
                    continue

                # Montagem do aviso
                aviso = {
                    "idEvento": str(evento["id"]),
                    "idCidade": str(cidade["id"]),
                    "valor": alert_data.get("value", 0),
                    "valorLimite": alert_data.get("threshold", 0),
                    "diferenca": alert_data.get("difference", 0),
                    "dataGeracao": date.today().isoformat(),
                    "dataReferencia": datetime.strptime(self.get_alert_date(alert_data['seconds']), "%d/%m/%Y").date().isoformat(),
                    "unidadeMedida": alert_data.get("unit"),
                    "horario": datetime.strptime(self.seconds_to_hhmm(alert_data['seconds'])['formatted'], "%H:%M").time().isoformat(),
                    "segundos": alert_data.get("seconds", 0),
                }

                avisos.append(aviso)

        return avisos
    
    def convert_ms2_to_kmh(self, speed_ms2):
        """
        Converte um valor de velocidade ao quadrado (m/s²) para km/h.
        A operação envolve tirar a raiz quadrada para obter m/s e depois converter para km/h.

        Args:
            speed_ms2 (float): Valor em m/s² (normalmente resultante de U² + V²).

        Returns:
            float: Velocidade em km/h.
        """
        if speed_ms2 is None or speed_ms2 < 0:
            return None

        speed_mps = math.sqrt(speed_ms2)  # converte para m/s
        return speed_mps * 3.6  # converte para km/h

    def seconds_to_hhmm(self, seconds):
        """
        Converte segundos para componentes de tempo (horas, minutos e dia), ajustando de UTC-0 para UTC-3.
        Calcula automaticamente o dia correto quando o horário cruza meia-noite.
        
        Args:
            seconds (int): Segundos desde meia-noite em UTC-0
            
        Returns:
            dict: Dicionário com componentes de tempo em UTC-3:
                {
                    'hours': int,      # Horas (0-23)
                    'minutes': int,    # Minutos (0-59)
                    'day': int,        # Dia do mês (1-31)
                    'formatted': str   # String formatada como "DD HH:MM"
                }
        """
        # Converter para inteiro antes de calcular horas e minutos
        seconds = int(seconds)
        
        # Converter de UTC-0 para UTC-3 (subtrair 3 horas = 10800 segundos)
        seconds_utc3 = seconds - 10800
        
        # Usar a data de hoje como base
        today = datetime.now()
        
        # Calcular o dia baseado no horário resultante
        if seconds_utc3 < 0:
            # Se cruza meia-noite (segundos_utc3 < 0), usar o dia anterior
            from datetime import timedelta
            previous_day = today - timedelta(days=1)
            day = previous_day.day
            seconds_utc3 += 86400  # Adicionar 24 horas (86400 segundos)
        elif seconds_utc3 >= 86400:
            # Se ultrapassa 24 horas (86400 segundos), usar o próximo dia
            from datetime import timedelta
            next_day = today + timedelta(days=1)
            day = next_day.day
            seconds_utc3 -= 86400  # Subtrair 24 horas (86400 segundos)
        else:
            # Dentro do mesmo dia
            day = today.day
        
        # Calcular horas e minutos
        hours = seconds_utc3 // 3600
        minutes = (seconds_utc3 % 3600) // 60
        
        return {
            'hours': hours,
            'minutes': minutes,
            'day': day,
            'formatted': f"{hours:02d}:{minutes:02d}"
        }

    def create_control_file(self, meteogram_filename, error=None):
        """
        Cria um arquivo de controle para indicar que o processamento do dia foi concluído.
        
        Args:
            meteogram_filename (str): Nome do arquivo de meteograma processado
            error (str, optional): Mensagem de erro associada ao processamento
            
        Returns:
            str: Caminho do arquivo de controle criado
        """
        # Obter o diretório do arquivo de meteograma
        meteogram_dir = os.path.dirname(self.meteogram_path)
        
        # Criar nome do arquivo de controle (adicionar .processed ao nome original)
        control_filename = f"{os.path.splitext(meteogram_filename)[0]}.processed"
        control_path = os.path.join(meteogram_dir, control_filename)
        
        # Criar arquivo de controle com timestamp e mensagem de erro
        with open(control_path, 'w') as f:
            f.write(f"Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Arquivo original: {meteogram_filename}\n")
            if error:
                f.write(f"Erro: {error}\n")
        
        print(f"Arquivo de controle criado: {control_path}")
        return control_path

if __name__ == "__main__":
    import time
    start_time = time.time()
    
    # Obter o diretório atual onde o script está sendo executado
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Caminho para o arquivo de configuração (1 nível acima da pasta src)
    config_path = os.path.abspath(os.path.join(current_dir, '../', 'config.csv'))
    
    print(f"Usando arquivo de configuração: {config_path}")

    # Gerar o nome do arquivo de meteograma com base na data atual
    today = datetime.now()
    meteogram_filename = f"HST{today.year}{today.month:02d}{today.day:02d}00-MeteogramASC.out"
    
    meteogramPathDir = os.path.abspath(os.path.join(current_dir, '../', 'tmp_files'))
    meteogramPath = os.path.join(meteogramPathDir, meteogram_filename)
    
    # Verificar se já existe arquivo de controle para este dia
    control_filename = f"{os.path.splitext(meteogram_filename)[0]}.processed"
    control_path = os.path.join(meteogramPathDir, control_filename)
    
    if os.path.exists(control_path):
        print(f"Arquivo de controle encontrado: {control_path}")
        print("Este arquivo já foi processado hoje. Encerrando execução.")
        sys.exit(0)
    
    print(f"Buscando arquivo de meteograma: {meteogramPath}")

    # Limpar arquivos antigos
    clean_old_files(meteogramPathDir)
    
    # Baixar o arquivo de meteograma mais recente
    downloaded_path = download_meteogram_file(
        date=f"{today.year}{today.month:02d}{today.day:02d}",
        directory=meteogramPathDir
    )
    
    if not downloaded_path:
        print("ERRO: Não foi possível baixar o arquivo de meteograma")
        sys.exit(1)

    try:
        alert_gen = AlertGenerator(
            config_path=config_path,
            meteogram_path=downloaded_path
            )
        
        # Carregar dados meteorológicos
        print("Carregando dados do meteograma...")
        data = alert_gen.load_meteogram_data()
        
        if data:
            # Verificar alertas
            print("Gerando avisos...")
            alerts = alert_gen.generate_all_alerts()

            # Mostrar resumo
            print(alert_gen.get_alerts_summary())
            # Enviar alertas
            if not alerts:
                print("Nenhum aviso encontrado. Encerrando execução.")
                alert_gen.create_control_file(meteogram_filename, error="Nenhum aviso encontrado. Encerrando execução.")
                sys.exit(0)

            client = HttpClient()
            
            client.login()
            eventos = client.obter_eventos()
            cidades = client.obter_cidades()

            # Preparar payload de importação
            print("Preparando payload de importação...")
            import_request = alert_gen.get_import_request(eventos, cidades)
            client.importar_avisos(import_request)

            # Iniciar o processamento no módulo de envios
            print("Iniciando o envio de notificações...")
            client.iniciar_processamento_alertas()

            # Criar arquivo de controle para indicar que o processamento foi concluído com sucesso
            alert_gen.create_control_file(meteogram_filename)
            print("Processamento concluído com sucesso!")
        else:
            error_msg = "Não foi possível carregar os dados do meteograma"
            print(error_msg)
            # Criar arquivo de controle com erro
            alert_gen.create_control_file(meteogram_filename, error=error_msg)
            
    except FileNotFoundError as e:
        error_msg = f"ERRO FATAL: {str(e)} - Não foi possível continuar o processamento. Verifique o arquivo de configuração."
        print(error_msg)
        # Criar arquivo de controle com erro
        alert_gen.create_control_file(meteogram_filename, error=error_msg)
        sys.exit(1)
    except Exception as e:
        error_msg = f"ERRO FATAL: {str(e)} - Ocorreu um erro inesperado durante o processamento."
        print(error_msg)
        # Criar arquivo de controle com erro
        alert_gen.create_control_file(meteogram_filename, error=error_msg)
        sys.exit(1)
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\nTempo total de execução: {execution_time:.2f} segundos")
