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

def patient_roster_df():
    sql = """select split_part(MRN, '-', 1) as Insurance_code
            , *
            from HNTS_REVENUE_CYCLE.RAW.PATIENT_ROSTER
            """
    df = chart_utils.read_from_db(sql)
    return df

def full_df():
    sql = """
    select
        split_part(MRN, '-', 1) as Insurance_code
        , case
            when task like 'OASIS-D1 Start of Care%' then 'Admissions'
            when task like 'OASIS-D1%Discharge%' then 'Discharges'
            when task like 'OASIS-D1%Resumption of Care%' then 'Resumptions'
            when task like 'OASIS-D1%Recertification%' then 'Recertifications'
        end as task_category
        , v.*
    from HNTS_REVENUE_CYCLE.RAW.SCHEDULEREPORTS_VISITSBYSTATUS v
    where task_category is not null"""
    df = chart_utils.read_from_db(sql)
    return df

def layout():
    patient_roster_data = patient_roster_df()
    patient_roster_data["DOB"] = patient_roster_data["DOB"].astype(str)
    redis_instance.hset("app-data", "PATIENT_ROSTER", json.dumps(patient_roster_data.to_dict("records")))
    data = full_df()
    data["SCHEDULED_DATE"] = data["SCHEDULED_DATE"].astype(str)
    redis_instance.hset("app-data", "CENSUS_VISITS_BY_STATUS", json.dumps(data.to_dict("records")))
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
                                for i in data.columns if (i != 'BRANCH')
                            ],
                            filter_action="native",
                            page_action="native",
                            page_size=50,
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
    data = chart_utils.get_loaded_data('CENSUS_VISITS_BY_STATUS')
    if clinicians:
        data = data.loc[data["ASSIGNED_TO"].isin(clinicians)]
    patients = sorted([patient for patient in data["PATIENT"].unique() if patient])
    options = [{"label": patient, "value": patient} for patient in patients]
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
    data = chart_utils.get_loaded_data('CENSUS_VISITS_BY_STATUS')
    patient_roster_data = chart_utils.get_loaded_data('PATIENT_ROSTER')

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
