import plotly.graph_objects as go
import pandas as pd
import psycopg2
import Data.auth as auth
import random
import os

DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
connection = psycopg2.connect(
    host=auth.host,
    port=DB_PORT,
    database=auth.db,
    user=auth.user,
    password=auth.password
)

poslovanje = """with a as 
          (SELECT t.id_termin, s.id_stranka, s.ime_priimek, t.datum, t.ime_storitve, t.ime_priimek_usluzbenca, st.trajanje, st.cena, i.popust,
              CASE WHEN i.popust IS NULL THEN cena
                  ELSE(1-i.popust) * st.cena 
              END AS koncna_cena, st.stroski, DATE_PART('month', datum) mesec, DATE_PART('year', datum) leto
          FROM Termin1 t
          LEFT JOIN Stranka s ON s.ime_priimek = t.ime_priimek_stranke
          LEFT JOIN Storitev st ON st.ime_storitve = t.ime_storitve
          LEFT JOIN Influencer i ON i.koda = t.koda),
        b as 
          (SELECT DISTINCT leto, mesec, sum(koncna_cena) OVER(PARTITION BY leto, mesec) prihodki, 
          sum(stroski) OVER(PARTITION BY leto, mesec) odhodki
          FROM a)
        SELECT leto, mesec, prihodki, odhodki, prihodki - odhodki dobicek
        FROM b
        ORDER BY leto, mesec ASC;"""

df = pd.read_sql_query(poslovanje, connection)
compile

fig = go.Figure()






for leto in df:
    # Filter the DataFrame for the current country
    
    # Add a trace for each country
    fig.add_trace(
        go.Line(
            x=df['mesec'],
            y=df['dobicek']
            #color=leto,
            #width=0.5
        )
    )

fig.update_layout(
    title='Dobiček po mesecih',
    xaxis_title='Mesec',
    yaxis_title='Dobiček'
    # barmode='group',  # To group the bars by player
    #legend_title='Leto'  # Set the legend title
)

folder_path = "/Users/travn/OneDrive/Namizje/Kozmetični salon/OPB-kozmeticni-salon/Views/graphs"
file_path1 = f"{folder_path}/poslovanje.html"
fig.write_html(file_path1, include_plotlyjs = "cdn")
#fig.show()

