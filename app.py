import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

DATA_URL = 'csv/data.csv'

st.title('Historische onttrekkingsverboden Aa of Weerijs')
st.sidebar.title('Controls')

# data laden
@st.cache
def load_data():
    data = pd.read_csv(DATA_URL, parse_dates=[0], index_col=[0])
    return data
data = load_data()

def figure(df, colname, color, colorfill, year, shapes):
    df = df[colname].groupby([df.index.dayofyear, df.index.year]).mean().unstack()
    df = df.dropna(how='all').round(2)
    # layout
    margindict = dict(l=0, r=0, t=0, b=0)
    height = 200
    # opbouwen plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df.quantile(0.95, axis=1), fill='none', fillcolor=colorfill, line={'color': color, 'dash': 'dash'}, opacity=0.5))
    fig.add_trace(go.Scatter(x=df.index, y=df.quantile(0.05, axis=1), fill='tonexty', fillcolor=colorfill, line={'color': color, 'dash': 'dash'}, opacity=0.5))
    fig.add_trace(go.Scatter(x=df.index, y=df[year], mode='lines+markers', line={'color': color, 'width': 3}))
    fig.update_layout(margin=margindict, height=height, shapes=shapes, xaxis=dict(title='day of year'), yaxis=dict(title=colname), showlegend=False) # layout aanpassen en onttrekkingsverboden toevoegen
    if colname == 'afvoer (m3/s)':
        fig.update_layout(margin=margindict, height=height, shapes=shapes, xaxis=dict(title='day of year'), yaxis=dict(title=colname, range=[0,1]), showlegend=False) # layout aanpassen en onttrekkingsverboden toevoegen
    return fig

# jaar selectie
year_to_filter = st.sidebar.slider('selecteer jaar', 2010, 2020, 2010)

# type droogte selectie
type_to_filter = st.sidebar.multiselect('selecteer type droogte', ['hydrologische droogte', 'agrarische droogte', 'meteorologische droogte'], ['hydrologische droogte', 'agrarische droogte', 'meteorologische droogte'])
type_to_col = dict({'hydrologische droogte': ['afvoer (m3/s)', 'daling gws (m)'], 'agrarische droogte': ['bodemvocht (mm)'], 'meteorologische droogte': ['neerslagtekort (mm)']})

# onttrekkingsverboden toevoegen
shapes = []
for color, typeverbod in zip(['green', 'red', 'orange'],['grasland', 'totaal', 'kapitaalintensieve teelten uitgezonderd']):
    temp = data.loc[str(year_to_filter), typeverbod].dropna()
    if not temp.empty:
        shapes.append(dict(type="rect", xref="x", yref="paper", x0=temp.index.dayofyear.min(), y0=0, x1=temp.index.dayofyear.max(), 
                     y1=1, fillcolor=color, opacity=0.5, layer="below", line_width=1))

# plotten
if 'hydrologische droogte' in type_to_filter:
    st.subheader('Hydrologische droogte')
    st.plotly_chart(figure(data, colname='afvoer (m3/s)', color='yellowgreen', colorfill='rgba(154,205,50,0.2)', year=year_to_filter, shapes=shapes))
    st.plotly_chart(figure(data, colname='daling gws (m)', color='orange', colorfill='rgba(255,165,0,0.2)', year=year_to_filter, shapes=shapes))
if 'agrarische droogte' in type_to_filter:
    st.subheader('Agrarische droogte')
    st.plotly_chart(figure(data, colname='bodemvocht (mm)', color='tomato', colorfill='rgba(255,99,71,0.2)', year=year_to_filter, shapes=shapes))
if 'meteorologische droogte' in type_to_filter:
    st.subheader('Meteorologische droogte')
    st.plotly_chart(figure(data, colname='neerslagtekort (mm)', color='navy', colorfill='rgba(0,0,128,0.2)', year=year_to_filter, shapes=shapes))