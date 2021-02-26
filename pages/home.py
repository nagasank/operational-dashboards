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
    data = chart_utils.get_loaded_data("SCHEDULEREPORTS_VISITSBYSTATUS","DATASET")
    remove_cols = ['BRANCH','COLUMN_MAPPING', 'COLUMN_PARAMETERS']

    max_date = datetime.now()

    children = html.Div(
        [
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
                                        {"label": status, "value": status,}
                                        for status in sorted(
                                            [
                                                patient
                                                for patient in data["STATUS"].unique()
                                                if patient
                                            ]
                                        )
                                    ],
                                    multi=True,
                                    placeholder="Select Status",
                                    id="status-selector",
                                    value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=[
                                        {"label": clinician, "value": clinician,}
                                        for clinician in sorted(
                                            [
                                                patient
                                                for patient in data[
                                                    "ASSIGNED_TO"
                                                ].unique()
                                                if patient
                                            ]
                                        )
                                        if clinician
                                    ],
                                    multi=True,
                                    placeholder="Select a Clinician",
                                    id="clinician-selector",
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    multi=True,
                                    placeholder="Select a Patient",
                                    id="patient-selector",
                                )
                            ),
                            ddk.ControlItem(
                                dcc.DatePickerRange(
                                    id="date-picker",
                                    min_date_allowed=pd.to_datetime(
                                        data["SCHEDULED_DATE"].min()
                                    ),
                                    max_date_allowed=max_date,
                                    initial_visible_month=max_date,
                                    start_date=max_date - timedelta(days=30),
                                    end_date=max_date,
                                ),
                            ),
                            ddk.ControlItem(
                                html.Button(
                                    id="select-all-rows",
                                    children="Select all matching records",
                                    style={"margin": "auto"},
                                    n_clicks=0,
                                )
                            ),
                            html.Div(
                                [
                                    ddk.Modal(
                                        id="modal-btn-outer",
                                        children=[
                                            html.Button(
                                                id="expand-modal-2",
                                                n_clicks=0,
                                                children="Take action",
                                            ),
                                        ],
                                        target_id="modal-content",
                                        hide_target=True,
                                        style={"float": "right"},
                                    ),
                                ],
                                style={"margin": "auto"},
                            ),
                        ],
                        width=30,
                        style={"overflow": "scroll"},
                    ),
                    ddk.Card(id="time-series"),
                ]
            ),
            ddk.Row(id="pie-charts"),
            ddk.Card(
                children=[
                    ddk.CardHeader(
                        title="Table of selected tasks",
                        children=[
                            html.Div(
                                [
                                    ddk.Modal(
                                        id="modal-btn-outer",
                                        children=[
                                            html.Button(
                                                id="expand-modal",
                                                n_clicks=0,
                                                children="Take action",
                                            )
                                        ],
                                        target_id="modal-content",
                                        hide_target=True,
                                        style={"float": "right"},
                                    ),
                                    ddk.Block(
                                        id="modal-content",
                                        children=html.Div(id="modal-div"),
                                        style={
                                            "width": "50%",
                                            "margin": "auto",
                                            "overflow": "scroll",
                                        },
                                    ),
                                ]
                            ),
                        ],
                    ),
                    ddk.Block(
                        ddk.DataTable(
                            columns=[
                                {"name": i.replace("_", " ").title(), "id": i}
                                for i in data.columns if (i not in remove_cols)
                            ],
                            data = data.sort_values(by="SCHEDULED_DATE").to_dict("records"),
                            filter_action="native",
                            page_action="native",
                            page_size=25,
                            row_selectable="multi",
                            id="data-table",
                            style_cell={'fontSize': 12, 'font-family': 'sans-serif'}
                        ),
                        style={"overflow": "scroll"}
                    ),
                ]
            ),
        ]
    )
    return children


@app.callback(
    [Output("data-table", "selected_rows"), Output("select-all-rows", "children"),],
    [Input("select-all-rows", "n_clicks")],
    [State("data-table", "data")],
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
    Output("patient-selector", "options"), [Input("clinician-selector", "value"),],
)
def show_patients(clinicians):
    """
    List of options to drill down into specific patients is controlled by the clinician selected:
    the list of patients will be the list of patients the selected clinicians are responsible for.
    """
    data = chart_utils.get_loaded_data("SCHEDULEREPORTS_VISITSBYSTATUS","DATASET")
    #print(data.columns)
    if clinicians:
        data = data.loc[data["ASSIGNED_TO"].isin(clinicians)]
    patients = sorted([patient for patient in data["PATIENT"].unique() if patient])
    #print(patients)
    options = [{"label": patient, "value": patient} for patient in patients]
    return options


@app.callback(
    [
        Output("pie-charts", "children"),
        Output("data-table", "data"),
        Output("time-series", "children"),
        Output("select-all-rows", "n_clicks"),
    ],
    [
        Input("status-selector", "value"),
        Input("clinician-selector", "value"),
        Input("patient-selector", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ],
)
def update_charts(
    selected_status, selected_clinicians, selected_patients, start_date, end_date
):
    data = chart_utils.get_loaded_data("SCHEDULEREPORTS_VISITSBYSTATUS","DATASET")
    #print(data.columns)
    if start_date:
        data = data.loc[data["SCHEDULED_DATE"] > start_date]
    if end_date:
        data = data.loc[data["SCHEDULED_DATE"] < end_date]
    if selected_clinicians:
        data = data.loc[data["ASSIGNED_TO"].isin(selected_clinicians)]
    if selected_status:
        data = data.loc[data["STATUS"].isin(selected_status)]
    if selected_patients:
        data = data.loc[data["PATIENT"].isin(selected_patients)]

    pie_charts = [
        ddk.Card(
            [
                ddk.CardHeader(title="Overview of {}".format(column.title())),
                chart_utils.generate_pie(data, column),
            ],
        )
        for column in ["PAYOR", "STATUS"]
    ]

    time_series = [
        ddk.DataCard(
            id='total_visits_count',
            value=data.shape[0]
        ),
        ddk.CardHeader(
            title="Status of tasks for selected clinicians, dates, and status"
        ),
        chart_utils.generate_bar(data),
    ]
    data_table = data.sort_values(by="SCHEDULED_DATE").to_dict("records")

    return pie_charts, data_table, time_series, 0
