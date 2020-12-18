from dash.dependencies import Input, Output, State
import dash_design_kit as ddk
import dash_html_components as html
import dash_core_components as dcc
from app import app, redis_instance
import chart_utils
import dash_table
import json
import pandas as pd
from . import modal
from datetime import datetime, timedelta
import dash


def layout():
    # load data for display
    authorizations_data = chart_utils.get_loaded_data("VW_AUTHORIZATIONS", "DATASET")

    patient_status_arr = chart_utils.get_options(authorizations_data, "PATIENTSTATUS")
    discipline_arr = chart_utils.get_options(authorizations_data, "DISCIPLINE")
    auth_type_arr = chart_utils.get_options(authorizations_data, "AUTHORIZATION_TYPE")
    payer_arr = chart_utils.get_options(authorizations_data, "PAYER")
    patient_arr = chart_utils.get_options(authorizations_data, "PATIENT")
    remove_cols = ['BRANCH','COLUMN_MAPPING', 'COLUMN_PARAMETERS' ]
    max_date = datetime.now()
    #pending_df = authorizations_data.loc[authorizations_data["DATA_SOURCE_ARRAY"].str.contains(r'authsPENDINGMDS', na=True)]
    #history_df = authorizations_data.loc[authorizations_data["DATA_SOURCE_ARRAY"].str.contains(r'authsHISTORY', na=True)]
    #tbs_df = authorizations_data.loc[ authorizations_data["DATA_SOURCE_ARRAY"].str.contains(r'authsTOBESENT', na=True)]

    children = html.Div(
        [
            ddk.Row(
                [
                    ddk.DataCard(
                        id='auths_patient_status_count',
                        value=12 ,#tbs_df.shape[0],
                        label = 'Patient Status Count'
                    ),
                    ddk.DataCard(
                        id='auths_auth_type_count',
                        value=13,#pending_df.shape[0] ,
                        label='Authorization Type Count'
                    ),
                    ddk.DataCard(
                        id='auths_total_count',
                        value=authorizations_data.shape[0] ,
                        label='Total Authorizations'
                    ),
                ]
            ),
            ddk.Row(
                [
                    ddk.ControlCard(
                        [
                            html.Details(
                                [
                                    html.Summary("About this app"),
                                    html.P(
                                        """Select attributes to fine tune graphs and tables."""
                                    ),
                                ]
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(

                                    options=auth_type_arr,
                                    multi=True,
                                    placeholder="Select Authorization Type",
                                    id="auths-auth-type-selector"
                                    # value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=discipline_arr,
                                    multi=True,
                                    placeholder="Select Discipline",
                                    id="auths-discipline-selector"
                                    # value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=patient_arr,
                                    multi=True,
                                    placeholder="Select Patient",
                                    id="auths-patient-selector"
                                    # value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=patient_status_arr,
                                    multi=True,
                                    placeholder="Select Discipline",
                                    id="auths-patientstatus-selector"
                                    # value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=payer_arr,
                                    multi=True,
                                    placeholder="Select Payer",
                                    id="auths-payer-selector"
                                    # value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.DatePickerRange(
                                    id="auths-date-picker",
                                    min_date_allowed=pd.to_datetime(
                                        authorizations_data["START_DATE"].min()
                                    ),
                                    max_date_allowed=max_date,
                                    initial_visible_month=max_date,
                                    start_date=max_date - timedelta(days=700),
                                    end_date=max_date +timedelta(days=700),
                                ),
                            ),
                            ddk.ControlItem(
                                html.Button(
                                    id="auths-select-all-rows",
                                    children="Select all matching records",
                                    style={"margin": "auto"},
                                    n_clicks=0,
                                )
                            ),
                        ],
                        width=25,
                        style={"overflow": "scroll"},
                    ),
                    ddk.Card(
                        width=75,
                        children=[
                            ddk.CardHeader(
                                children=[
                                    html.Div(
                                        "Combined auths View", style={"float": "left"},
                                    ),

                                ]
                            ),
                            ddk.Block(
                                ddk.DataTable(
                                    columns=[
                                        {"name": i.replace("_", " ").title(), "id": i}
                                        for i in authorizations_data.columns if (i not in remove_cols)
                                    ],
                                    data=authorizations_data.sort_values(by="START_DATE").to_dict("records"),
                                    filter_action="native",
                                    page_action="native",
                                    page_size=50,
                                    row_selectable="multi",
                                    id="auths-history-data-table",
                                    style_cell={'fontSize': 12, 'font-family': 'sans-serif'},
                                    style_table = {'overflowX': 'auto'},
                                ),
                                style={"overflow": "scroll"}
                            ),
                        ]
                    ),
                ]

            ),

        ]
    )
    return children

@app.callback(
    [Output("auths-history-data-table", "selected_rows"), Output("auths-select-all-rows", "children"),],
    [Input("auths-select-all-rows", "n_clicks")],
    [State("auths-history-data-table", "data")],
)
def select_all(n_clicks, rows):
    if n_clicks % 2 == 1:
        selected_rows, text = (
            [i for i, row in enumerate(rows)],
            "Deselect all",
        )
    else:
        selected_rows, text = [], "Select all matching records"

    return selected_rows, text




@app.callback(
    [
        #Output("'auths_patient_status_count'", "value"),
        #Output("auths_auth_type_count", "value"),
        Output("auths_total_count", "value"),
        Output("auths-history-data-table", "data"),
        Output("auths-select-all-rows", "n_clicks"),
    ],
    [
        Input("auths-auth-type-selector", "value"),
        Input("auths-discipline-selector", "value"),
        Input("auths-patient-selector", "value"),
        Input("auths-patientstatus-selector", "value"),
        Input("auths-payer-selector", "value"),
        Input("auths-date-picker", "start_date"),
        Input("auths-date-picker", "end_date"),
    ],
)
def update_charts(
    selected_authorization_type, selected_discipline, selected_patients, selected_patientstatus, selected_payers,start_date, end_date
):
    #subset data-table data
    data = chart_utils.get_loaded_data("VW_AUTHORIZATIONS", "DATASET")
    if start_date:
        data = data.loc[data["START_DATE"] > start_date]
    if end_date:
        data = data.loc[data["END_DATE"] < end_date]
    if selected_discipline:
        data = data.loc[data["DISCIPLINE"].isin(selected_discipline)]
    if selected_authorization_type:
        data = data.loc[data["AUTHORIZATION_TYPE"].isin(selected_authorization_type)]
    if selected_patients:
        data = data.loc[data["PATIENT"].isin(selected_patients)]
    if selected_patientstatus:
            data = data.loc[data["PATIENTSTATUS"].isin(selected_patientstatus)]
    if selected_payers:
            data = data.loc[data["PAYER"].isin(selected_payers)]

    data_table=data.sort_values(by="START_DATE").to_dict("records")

    #update cards

    auths_count = data.shape[0]

    return  auths_count, data_table,  0
