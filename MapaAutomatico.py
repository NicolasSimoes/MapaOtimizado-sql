import pandas as pd
import pyodbc
import folium
import math
from datetime import datetime, timedelta
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def haversine_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    lat1, lon1 = math.radians(lat1), math.radians(lon1)
    lat2, lon2 = math.radians(lat2), math.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    return 6371 * 2 * math.asin(math.sqrt(a))

def build_distance_matrix(coords):
    return [[haversine_distance(c1, c2) for c2 in coords] for c1 in coords]

def solve_tsp(distance_matrix):
    size = len(distance_matrix)
    manager = pywrapcp.RoutingIndexManager(size, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_idx, to_idx):
        return int(distance_matrix[manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)] * 1000)

    transit_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = 10

    solution = routing.SolveWithParameters(params)
    if solution:
        idx = routing.Start(0)
        route = []
        while not routing.IsEnd(idx):
            route.append(manager.IndexToNode(idx))
            idx = solution.Value(routing.NextVar(idx))
        route.append(manager.IndexToNode(idx))
        return route
    return list(range(size))

def gerar_mapa_com_query(tipo):
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=10.1.0.3\\SQLSTANDARD;"
        "DATABASE=dbactions;"
        "UID=analistarpt;"
        "PWD=mM=DU9lUd3C$qb@"
    )
    conn = pyodbc.connect(conn_str)

    if tipo == 1:
        nome_arquivo = "mapa_motorista.html"
        query = """
        WITH RankedData AS (
            SELECT 
                dt.M06_DTSAIDA,
                m.M13_DESC AS MOTORISTA,
                dt.M06_VEIC_PLACA,
                dt.M06_ID_CLIENTE AS CODIGO,
                dt.M06_ID_A76 AS OP,
                c.A00_FANTASIA AS NOME_FANTASIA,
                c.A00_LAT AS LATITUDE,
                c.A00_LONG AS LONGITUDE,
                SUM(dt.M06_TOTPRO) AS FATURAMENTO,
                ROW_NUMBER() OVER (PARTITION BY dt.M06_ID_CLIENTE ORDER BY dt.M06_DTSAIDA) AS rn
            FROM M06 AS dt
            JOIN M13 AS m ON dt.M06_ID_M13 = m.M13_ID
            JOIN A00 AS c ON dt.M06_ID_CLIENTE = c.A00_ID
            WHERE 
                c.A00_STATUS = 1
                AND dt.M06_DTSAIDA >= CAST(DATEADD(DAY, 1, GETDATE()) AS DATE)
                AND dt.M06_DTSAIDA < DATEADD(DAY, 2, CAST(GETDATE() AS DATE))
                AND dt.M06_ID_A76 IN (38, 39, 100, 1171, 101, 172, 112, 130, 113)
            GROUP BY 
                dt.M06_DTSAIDA,
                m.M13_DESC,
                dt.M06_VEIC_PLACA,
                dt.M06_ID_CLIENTE,
                dt.M06_ID_A76,
                c.A00_FANTASIA,
                c.A00_LAT,
                c.A00_LONG
        )
        SELECT 
            M06_DTSAIDA,
            MOTORISTA,
            M06_VEIC_PLACA,
            CODIGO,
            OP,
            NOME_FANTASIA,
            LATITUDE,
            LONGITUDE,
            FATURAMENTO
        FROM RankedData
        WHERE rn = 1
        ORDER BY M06_DTSAIDA ASC;
        """
    else:
        nome_arquivo = "mapa_cliente.html"
        query = """
    WITH RankedData AS (
        SELECT 
            dt.M06_STATUS,
            dt.M06_DTSAIDA,
            dt.M06_ID_CLIENTE AS CODIGO,
            dt.M06_ID_A76 AS OP,
            c.A00_FANTASIA AS NOME_FANTASIA,
            c.A00_LAT AS LATITUDE,
            c.A00_LONG AS LONGITUDE,
            SUM(dt.M06_TOTPRO) AS FATURAMENTO,
            ROW_NUMBER() OVER (
                PARTITION BY dt.M06_ID_CLIENTE 
                ORDER BY dt.M06_DTSAIDA
            ) AS rn
        FROM M06 AS dt
        JOIN A00 AS c ON dt.M06_ID_CLIENTE = c.A00_ID
        WHERE 
            c.A00_STATUS = 1
            AND CAST(dt.M06_DTSAIDA AS DATE) = CAST(DATEADD(DAY, 1, GETDATE()) AS DATE)
            AND dt.M06_ID_A76 IN (38, 39, 100, 1171, 101, 172, 112, 130, 113)
            AND dt.M06_STATUS IN (1, 3)
        GROUP BY 
            dt.M06_STATUS,
            dt.M06_DTSAIDA,
            dt.M06_ID_CLIENTE,
            dt.M06_ID_A76,
            c.A00_FANTASIA,
            c.A00_LAT,
            c.A00_LONG
    )
    SELECT 
        M06_DTSAIDA,
        CODIGO,
        OP,
        NOME_FANTASIA,
        LATITUDE,
        LONGITUDE,
        FATURAMENTO
    FROM RankedData
    WHERE rn = 1
    ORDER BY M06_DTSAIDA ASC;
    """

    df = pd.read_sql(query, conn)
    df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce')
    df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
    df['FATURAMENTO'] = pd.to_numeric(df['FATURAMENTO'], errors='coerce')
    df['M06_DTSAIDA'] = pd.to_datetime(df['M06_DTSAIDA']).dt.date

    data_filtro = (datetime.now() + timedelta(days=1)).date()
    df = df[df['M06_DTSAIDA'] == data_filtro]

    casa_motorista = (-3.7572635398641, -38.5854081195323)
    mapa = folium.Map(location=casa_motorista, zoom_start=10)

    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'darkblue', 'cadetblue', 'pink', 'black']
    if tipo == 1 and 'MOTORISTA' in df.columns:
        truck_colors = {t: colors[i % len(colors)] for i, t in enumerate(df['MOTORISTA'].unique())}
    else:
        df['MOTORISTA'] = 'CLIENTES'
        truck_colors = {'CLIENTES': 'blue'}

    folium.Marker(
        casa_motorista,
        icon=folium.Icon(color='gray', icon='home', prefix='fa'),
        tooltip='CD - VALEMILK'
    ).add_to(mapa)

    rotas = []

    for truck, grp in df.groupby('MOTORISTA'):
        clientes_validos = grp[grp['LATITUDE'].notnull() & grp['LONGITUDE'].notnull()].reset_index(drop=True)
        if clientes_validos.empty:
            continue

        coords = [casa_motorista] + list(zip(clientes_validos['LATITUDE'], clientes_validos['LONGITUDE']))
        dm = build_distance_matrix(coords)
        route = solve_tsp(dm)
        ordered_coords = [coords[i] for i in route if i < len(coords)]

        color = truck_colors[truck]
        fg = folium.FeatureGroup(name=f'{truck}')

        count = 1
        for i in route[1:]:
            if i == 0 or (i - 1) >= len(clientes_validos):
                continue
            row = clientes_validos.iloc[i - 1]
            loc = (row['LATITUDE'], row['LONGITUDE'])
            nome = row['NOME_FANTASIA']
            codigo = row['CODIGO']

            icon_html = (
                f"<div style='width:30px;height:30px;border-radius:50%;background:{color};"
                f"display:flex;align-items:center;justify-content:center;font-weight:bold;color:white;'>"
                f"{count}</div>"
            )
            folium.Marker(
                loc,
                icon=folium.DivIcon(html=icon_html),
                tooltip=f"{count} - {nome}",
                popup=f"<b>{nome}</b> (Cód: {codigo})"
            ).add_to(fg)

            folium.PolyLine([ordered_coords[count - 1], loc], color=color, weight=2).add_to(fg)

            rotas.append({
                'Motorista': truck,
                'Ordem': count,
                'Codigo': codigo,
                'Nome Fantasia': nome,
                'Latitude': loc[0],
                'Longitude': loc[1]
            })

            count += 1

        fg.add_to(mapa)

    folium.LayerControl().add_to(mapa)

    df_group = df.groupby('MOTORISTA').agg(
        FATURAMENTO_TOTAL=('FATURAMENTO', 'sum'),
        CLIENTES=('CODIGO', 'nunique')
    ).reset_index()

    faturamento_total = df['FATURAMENTO'].sum()
    total_clientes = df['CODIGO'].nunique()
    df_group['USO_PERC'] = (df_group['FATURAMENTO_TOTAL'] / 8000) * 100

    legenda_html = (
        f"<div style='position:fixed;bottom:50px;left:50px;width:300px;"
        f"background:white;border:2px solid grey;z-index:9999;padding:10px;"
        f"box-shadow:2px 2px 5px rgba(0,0,0,0.3);font-size:14px;'>"
        f"<b>Clientes totais:</b> {total_clientes}<br>"
        f"<b>Faturamento total:</b> R$ {faturamento_total:,.2f}<br>"
        f"<b>Atualizado:</b> Saída: {data_filtro.strftime('%d/%m/%Y')}<br><br>"
        + ''.join([
            f"<div style='display:flex;align-items:center;margin-bottom:5px;'>"
            f"<div style='width:15px;height:15px;background:{truck_colors.get(row['MOTORISTA'], 'gray')};"
            f"border-radius:50%;margin-right:8px;'></div>"
            f"<b>{row['MOTORISTA'].upper()}</b>: R$ {row['FATURAMENTO_TOTAL']:,.2f}  "
                      f"</div>"
            for _, row in df_group.iterrows()
        ]) +
        "</div>"
    )

    mapa.get_root().html.add_child(folium.Element(legenda_html))
    mapa.save(nome_arquivo)
