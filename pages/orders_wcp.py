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
    orders_history_data = chart_utils.get_loaded_data("VIEW_ORDERSHISTORY", "DATASET")
    orders_pending_mds_data = chart_utils.get_loaded_data("VIEW_ORDERSMANAGEMENT_ORDERSPENDINGMDS", "DATASET")
    orders_tobe_sent_data = chart_utils.get_loaded_data("VIEW_ORDERSTOBESENT", "DATASET")
    max_date = datetime.now()

    order_number_data = pd.concat(
        [orders_history_data["ORDER_NUMBER"], orders_pending_mds_data["ORDER_NUMBER"],
         orders_tobe_sent_data["ORDER_NUMBER"]])
    physician_data = pd.concat(
        [orders_history_data["PHYSICIAN"], orders_pending_mds_data["PHYSICIAN"],
         orders_tobe_sent_data["PHYSICIAN"]])
    ordertype_data = pd.concat(
        [orders_history_data["TYPE"], orders_pending_mds_data["TYPE"],
         orders_tobe_sent_data["TYPE"]])
    patient_data = pd.concat(
        [orders_history_data["PATIENT"], orders_pending_mds_data["PATIENT"],
         orders_tobe_sent_data["PATIENT"]])

    children = html.Div(
        [
            ddk.Row(
                [
                    ddk.DataCard(
                        id='orders_tobe_sent_count',
                        value=orders_tobe_sent_data.shape[0],
                        label = 'To Be Sent'
                    ),
                    ddk.DataCard(
                        id='orders_pending_mds_count',
                        value=orders_pending_mds_data.shape[0] ,
                        label='Pending MD Signature'
                    ),
                    ddk.DataCard(
                        id='orders_history_count',
                        value=orders_history_data.shape[0] ,
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
                                    options=[
                                        {"label": orderstype, "value": orderstype}
                                        for orderstype in sorted(
                                            [
                                                orderstype
                                                for orderstype in ordertype_data.unique()
                                                if orderstype
                                            ]
                                        )
                                    ],
                                    multi=True,
                                    placeholder="Select Type",
                                    id="orders-type-selector"
                                    # value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=[
                                        {"label": physician, "value": physician}
                                        for physician in sorted(
                                            [
                                                physician
                                                for physician in physician_data.unique()
                                                if physician
                                            ]
                                        )
                                    ],
                                    multi=True,
                                    placeholder="Select Physician",
                                    id="orders-physician-selector"
                                    # value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=[
                                        {"label": patient, "value": patient}
                                        for patient in sorted(
                                            [
                                                patient
                                                for patient in patient_data.unique()
                                                if patient
                                            ]
                                        )
                                    ],
                                    multi=True,
                                    placeholder="Select Patient",
                                    id="orders-patient-selector"
                                    # value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.DatePickerRange(
                                    id="order-date-picker",
                                    min_date_allowed=pd.to_datetime(
                                        orders_history_data["ORDER_DATE"].min()
                                    ),
                                    max_date_allowed=max_date,
                                    initial_visible_month=max_date,
                                    start_date=max_date - timedelta(days=30),
                                    end_date=max_date,
                                ),
                            ),
                            ddk.ControlItem(
                                html.Button(
                                    id="orders_tob_esent-select-all-rows",
                                    children="Select all matching records",
                                    style={"margin": "auto"},
                                    n_clicks=0,
                                )
                            ),
                        ],
                        width=30,
                        style={"overflow": "scroll"},
                    ),
                    ddk.Card(
                        children=[
                            ddk.CardHeader(
                                children=[
                                    html.Div(
                                        "Table of selected tasks", style={"float": "left"},
                                    ),

                                ]
                            ),
                            ddk.Block(
                                ddk.DataTable(
                                    columns=[
                                        {"name": i.replace("_", " ").title(), "id": i}
                                        for i in orders_history_data.columns if (i != 'BRANCH')
                                    ],
                                    data=orders_history_data.sort_values(by="PHYSICIAN").to_dict("records"),
                                    filter_action="native",
                                    page_action="native",
                                    page_size=50,
                                    row_selectable="multi",
                                    id="orders-history-data-table",
                                    style_cell={'fontSize': 12, 'font-family': 'sans-serif'}
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
