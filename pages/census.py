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

def get_options(df, column_name):
    df.fillna("",inplace=True)
    options_arr = [{'label': val1, 'value': val1} for val1 in sorted(df[column_name].unique()) if val1]
    return options_arr

def layout():
    patient_roster_data = chart_utils.get_loaded_data("VW_PATIENT_ROSTER","DATASET")
    data = chart_utils.get_loaded_data("VW_VISITSBYSTATUS_TASK_CATEGORY","DATASET")
    remove_cols = ['BRANCH', 'COLUMN_MAPPING', 'COLUMN_PARAMETERS']
    max_date = datetime.now()

    children = html.Div(
        [
            ddk.Row(
                [
                    ddk.Card(id="patient-roster-chart"),
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
                                        {"label": status, "value": status}
                                        for status in sorted(
                                            [
                                                status
                                                for status in data["STATUS"].unique()
                                                if status
                                            ]
                                        )
                                    ],
                                    multi=True,
                                    placeholder="Select Status",
                                    id="census-status-selector"
                                    #value=["Not Yet Started", "Saved"],
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=[
                                        {"label": task, "value": task}
                                        for task in sorted(
                                            [
                                                task
                                                for task in data["TASK"].unique()
                                                if task
                                            ]
                                        )
                                    ],
                                    multi=True,
                                    placeholder="Select Task",
                                    id="census-task-selector"
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=[
                                        {"label": task_category, "value": task_category}
                                        for task_category in sorted(
                                            [
                                                task_category
                                                for task_category in data["TASK_CATEGORY"].unique()
                                                if task_category
                                            ]
                                        )
                                    ],
                                    multi=True,
                                    placeholder="Select Task Category",
                                    id="census-task_category-selector"
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=get_options(data, "ASSIGNED_TO"),
                                    multi=True,
                                    placeholder="Select a Clinician",
                                    id="census-clinician-selector",
                                )
                            ),
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    multi=True,
                                    placeholder="Select a Patient",
                                    id="census-patient-selector",
                                )
                            ),
                            ddk.ControlItem(
                                dcc.DatePickerRange(
                                    id="census-date-picker",
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
                                    id="census-select-all-rows",
                                    children="Select all matching records",
                                    style={"margin": "auto"},
                                    n_clicks=0,
                                )
                            ),
                            html.Div(
                                [
                                    ddk.Modal(
                                        id="census-modal-btn-outer",
                                        children=[
                                            html.Button(
                                                id="census-expand-modal-2",
                                                n_clicks=0,
                                                children="Take action",
                                            ),
                                        ],
                                        target_id="census-modal-content",
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
                    ddk.Card(id="census-time-series"),
                ]
            ),
            #ddk.Row(id="census-pie-charts"),
            ddk.Card(
                children=[
                    ddk.CardHeader(
                        children=[
                            html.Div(
                                "Table of selected tasks", style={"float": "left"},
                            ),
                            html.Div(
                                [
                                    ddk.Modal(
                                        id="census-modal-btn-outer",
                                        children=[
                                            html.Button(
                                                id="census-expand-modal",
                                                n_clicks=0,
                                                children="Take action",
                                            )
                                        ],
                                        target_id="census-modal-content",
                                        hide_target=True,
                                        style={"float": "right"},
                                    ),
                                    ddk.Block(
                                        id="census-modal-content",
                                        children=html.Div(id="census-modal-div"),
                                        style={
                                            "width": "50%",
                                            "margin": "auto",
                                            "overflow": "scroll",
                                        },
                                    ),
                                ]
                            ),
                        ]
                    ),
                    ddk.Block(
                        ddk.DataTable(
                            columns=[
                                {"name": i.replace("_", " ").title(), "id": i}
                                for i in data.columns if (i not in remove_cols)
                            ],

                            filter_action="native",
                            page_action="native",
                            page_size=25,
                            row_selectable="multi",
                            id="census-data-table",
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
    [Output("census-data-table", "selected_rows"), Output("census-select-all-rows", "children"),],
    [Input("census-select-all-rows", "n_clicks")],
    [State("census-data-table", "data")],
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
    Output("census-patient-selector", "options"), [Input("census-clinician-selector", "value"),],
)
def show_patients(clinicians):
    """
    List of options to drill down into specific patients is controlled by the clinician selected:
    the list of patients will be the list of patients the selected clinicians are responsible for.
    """
    data = chart_utils.get_loaded_data("VW_VISITSBYSTATUS_TASK_CATEGORY","DATASET")
    if clinicians:
        data = data.loc[data["ASSIGNED_TO"].isin(clinicians)]
    #patients = sorted([patient for patient in data["PATIENT"].unique() if patient])
    #options = [{"label": patient, "value": patient} for patient in patients]
    options = get_options(data, "PATIENT")
    return options

@app.callback(
    [
        Output("patient-roster-chart", "children"),
        #Output("census-pie-charts", "children"),
        Output("census-data-table", "data"),
        Output("census-time-series", "children"),
        Output("census-select-all-rows", "n_clicks"),
    ],
    [
        Input("census-status-selector", "value"),
        Input("census-clinician-selector", "value"),
        Input("census-patient-selector", "value"),
        Input("census-date-picker", "start_date"),
        Input("census-date-picker", "end_date"),
        Input("census-task-selector", "value"),
        Input("census-task_category-selector", "value"),
    ],
)
def update_charts(selected_status, selected_clinicians, selected_patients, start_date, end_date, selected_task, selected_task_category):
    data = chart_utils.get_loaded_data("VW_VISITSBYSTATUS_TASK_CATEGORY","DATASET")
    patient_roster_data = chart_utils.get_loaded_data('VW_PATIENT_ROSTER', 'DATASET')

    if start_date:
        data = data.loc[data["SCHEDULED_DATE"] >= start_date]
    if end_date:
        data = data.loc[data["SCHEDULED_DATE"] < end_date]
    if selected_clinicians:
        data = data.loc[data["ASSIGNED_TO"].isin(selected_clinicians)]
    if selected_status:
        data = data.loc[data["STATUS"].isin(selected_status)]
    if selected_patients:
        data = data.loc[data["PATIENT"].isin(selected_patients)]
    if selected_task:
        data = data.loc[data["TASK"].isin(selected_task)]
    if selected_task_category:
        data = data.loc[data["TASK_CATEGORY"].isin(selected_task_category)]

    pie_charts = [
        ddk.Card(
            [
                ddk.CardHeader("Overview of {}".format(column.title())),
                chart_utils.generate_pie(data, column),
            ],
        )
        for column in ["PAYOR", "STATUS"]
    ]

    #print(data)
    time_series = [
        ddk.DataCard(
            id='visits_by_status_count',
            value=data.shape[0]
        ),
        ddk.CardHeader("Status of tasks for selected clinicians, dates, and status"),
        chart_utils.generate_census_bar(data),
    ]
    data_table = data.sort_values(by="SCHEDULED_DATE").to_dict("records")

    patient_roster_chart = [
        ddk.DataCard(
            id='census_count',
            value=patient_roster_data.shape[0]
        ),
        ddk.CardHeader("Patient Roster Chart"),
        chart_utils.generate_patient_roster_bar(patient_roster_data),
    ]
    return patient_roster_chart, data_table, time_series, 0
