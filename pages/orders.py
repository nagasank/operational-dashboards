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
    orders_history_data = chart_utils.get_loaded_data("VW_ORDERS_HISTORY_FULL", "DATASET")
    remove_cols = ['BRANCH', 'COLUMN_MAPPING', 'COLUMN_PARAMETERS']
    type_arr = chart_utils.get_options(orders_history_data, "TYPE")
    physician_arr = chart_utils.get_options(orders_history_data, "PHYSICIAN")
    patient_arr = chart_utils.get_options(orders_history_data, "TYPE")
    remove_cols = ['BRANCH', 'PAYOR', 'INTERNAL_REFERRAL_SOURCE',]
    max_date = datetime.now()
    pending_df = orders_history_data.loc[
        orders_history_data["DATA_SOURCE_ARRAY"].str.contains(r'ORDERSPENDINGMDS', na=True)]
    history_df = orders_history_data.loc[
        orders_history_data["DATA_SOURCE_ARRAY"].str.contains(r'ORDERSHISTORY', na=True)]
    tbs_df = orders_history_data.loc[
        orders_history_data["DATA_SOURCE_ARRAY"].str.contains(r'ORDERSTOBESENT', na=True)]

    children = html.Div(
        [
            ddk.Row(
                [
                    ddk.DataCard(
                        id='orders_tobe_sent_count',
                        value=tbs_df.shape[0],
                        label = 'To Be Sent'
                    ),
                    ddk.DataCard(
                        id='orders_pending_mds_count',
                        value=pending_df.shape[0] ,
                        label='Pending MD Signature'
                    ),
                    ddk.DataCard(
                        id='orders_history_count',
                        value=history_df.shape[0] ,
                        label='Total Orders'
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

                                    options=type_arr,
                                    multi=True,
                                    placeholder="Select Type",
                                    id="orders-type-selector"
                                    # value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=physician_arr,
                                    multi=True,
                                    placeholder="Select Physician",
                                    id="orders-physician-selector"
                                    # value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=patient_arr,
                                    multi=True,
                                    placeholder="Select Patient",
                                    id="orders-patient-selector"
                                    # value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.DatePickerRange(
                                    id="orders-date-picker",
                                    min_date_allowed=pd.to_datetime(
                                        orders_history_data["ORDER_DATE"].min()
                                    ),
                                    max_date_allowed=max_date,
                                    initial_visible_month=max_date,
                                    start_date=max_date - timedelta(days=700),
                                    end_date=max_date,
                                ),
                            ),
                            ddk.ControlItem(
                                html.Button(
                                    id="orders-select-all-rows",
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
                                        "Combined Orders View", style={"float": "left"},
                                    ),

                                ]
                            ),
                            ddk.Block(
                                ddk.DataTable(
                                    columns=[
                                        {"name": i.replace("_", " ").title(), "id": i}
                                        for i in orders_history_data.columns if (i not in remove_cols)
                                    ],
                                    data=orders_history_data.sort_values(by="PHYSICIAN").to_dict("records"),
                                    filter_action="native",
                                    page_action="native",
                                    page_size=50,
                                    row_selectable="multi",
                                    id="orders-history-data-table",
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
    [Output("orders-history-data-table", "selected_rows"), Output("orders-select-all-rows", "children"),],
    [Input("orders-select-all-rows", "n_clicks")],
    [State("orders-history-data-table", "data")],
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
    Output("orders-patient-selector", "options"), [Input("orders-physician-selector", "value"),],
)
def show_patients(physicians):
    """
    List of options to drill down into specific patients is controlled by the clinician selected:
    the list of patients will be the list of patients the selected clinicians are responsible for.
    """
    data = chart_utils.get_loaded_data("VW_ORDERS_HISTORY_FULL", "DATASET")
    if physicians:
        data = data.loc[data["PHYSICIAN"].isin(physicians)]
    patients = sorted([patient for patient in data["PATIENT"].unique() if patient])
    options = [{"label": patient, "value": patient} for patient in patients]
    return options


@app.callback(
    [
        Output("orders_tobe_sent_count", "value"),
        Output("orders_pending_mds_count", "value"),
        Output("orders_history_count", "value"),
        Output("orders-history-data-table", "data"),
        Output("orders-select-all-rows", "n_clicks"),
    ],
    [
        Input("orders-type-selector", "value"),
        Input("orders-physician-selector", "value"),
        Input("orders-patient-selector", "value"),
        Input("orders-date-picker", "start_date"),
        Input("orders-date-picker", "end_date"),
    ],
)
def update_charts(
    selected_type, selected_physicians, selected_patients, start_date, end_date
):
    #subset data-table data
    data = chart_utils.get_loaded_data("VW_ORDERS_HISTORY_FULL", "DATASET")
    if start_date:
        data = data.loc[data["ORDER_DATE"] > start_date]
    if end_date:
        data = data.loc[data["ORDER_DATE"] < end_date]
    if selected_physicians:
        data = data.loc[data["PHYSICIAN"].isin(selected_physicians)]
    if selected_type:
        data = data.loc[data["TYPE"].isin(selected_type)]
    if selected_patients:
        data = data.loc[data["PATIENT"].isin(selected_patients)]

    data_table=data.sort_values(by="PHYSICIAN").to_dict("records")

    #update cards
    pending_df = data.loc[
        data["DATA_SOURCE_ARRAY"].str.contains(r'ORDERSPENDINGMDS', na=True)]
    history_df = data.loc[
        data["DATA_SOURCE_ARRAY"].str.contains(r'ORDERSHISTORY', na=True)]
    tbs_df = data.loc[
        data["DATA_SOURCE_ARRAY"].str.contains(r'ORDERSTOBESENT', na=True)]
    tbs_count =tbs_df.shape[0]
    pending_count = pending_df.shape[0]
    history_count = history_df.shape[0]

    return  tbs_count, pending_count, history_count, data_table,  0
