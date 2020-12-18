import snowflake.connector
import pandas as pd
import plotly.express as px
from dash_design_kit import Graph
from app import redis_instance
import json
import os

# Write to Snowflake DB
def update_data(data):
    con = snowflake.connector.connect(
        user=os.environ.get('SNOWSQL_USER'),
        password=os.environ.get('SNOWSQL_PWD'),
        account=os.environ.get('SNOWSQL_ACCOUNT'),
        database=os.environ.get('SNOWSQL_DATABASE')
    )
    # print(len(data))
    sql_stmt = """
        insert into dash_interactivity.stage_comments_log(payload) 
        select parse_json($1) from values (%s)
        """
    # print(sql_stmt)
    ctx = con.cursor()
    payload = [[json.dumps(x)] for x in data]
    ctx.executemany(sql_stmt, payload)
    con.close()

#read from redis cache
def get_loaded_data(app_name='app-data', redis_key='DATASET'):
    redis_data = redis_instance.hget(app_name, redis_key)
    if redis_data:
        data = json.loads(redis_data)
    else:
        data = {}
    return pd.DataFrame(data)
###layout helper
def get_options(df, column_name):
    df.fillna("",inplace=True)
    options_arr = [{'label': val1, 'value': val1} for val1 in sorted(df[column_name].unique()) if val1]
    return options_arr

### Chart functions
def generate_pie(data, column):
    # df = pd.DataFrame(data[column].value_counts()).reset_index()
    fig = px.pie(data, names=column)
    if len(data[column].unique()) > 10:
        fig.update_layout(legend=dict(x=-1.5, y=1))
    else:
        fig.update_layout(legend=dict(orientation="v",x=0, y=1))
    return Graph(figure=fig)


def generate_bar(data):
    data = (
        data.groupby(["SCHEDULED_DATE", "STATUS"], sort=False)
        .size()
        .reset_index(name="Status")
    )
    fig1 = px.bar(data, x="SCHEDULED_DATE", y="Status", color="STATUS")
    fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig1.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="left",
        x=0.25
    ))
    fig = Graph(
        figure=fig1
    )
    return fig

def generate_census_bar(data):
    if not data.empty:
        data = (
            data.groupby(["SCHEDULED_DATE", "TASK_CATEGORY"], sort=False)
            .size()
            .reset_index(name="Count")
        )
        fig1 = px.bar(data, x="SCHEDULED_DATE", y="Count", color="TASK_CATEGORY",
            hover_data=['SCHEDULED_DATE', 'TASK_CATEGORY', 'Count'])
        #fig1.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', barmode='group')
        fig1.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="left",
            x=0.25
        ))
        fig = Graph(
            figure= fig1
        )
        return fig

def generate_patient_roster_bar(data):
    data = (
        data.groupby(["INSURANCE_CODE"], sort=True)
        .size()
        .reset_index(name="Count")
    )
    fig1 = px.bar(data, x="INSURANCE_CODE", y="Count")
    fig1.update_layout(showlegend=False)
    fig = Graph(
        figure=fig1
    )
    return fig



