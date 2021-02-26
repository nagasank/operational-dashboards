import sys

from dash.dependencies import Input, Output, State
import dash_design_kit as ddk
import dash_html_components as html
import dash_core_components as dcc
from app import app, redis_instance
import chart_utils
import dash_table
import json
import pandas as pd
from . import OrderProcessingmodal
from datetime import datetime, timedelta
import dash


def layout():
    # load data for display
    episodesummdata = chart_utils.get_loaded_data("AXXESS_API.USER_INPUTS.VW_PENDING_ORDERS_TF_SIMPLE", "DATASET")

    #reorder the columns
    new_order = ['INS_CODE',
                 'INITIAL_TIMELY_FILING',
                 'MRN',
                 'PATIENT',
                 'PATIENT_STATUS',
                 'DATE_OF_BIRTH',
                 'EPISODE_START_DATE',
                 'EPISODE_END_DATE',
                 'PHYSICIAN_NAME',
                 'PHYSICIAN_PHONE',
                 'PHYSICIAN_FACSIMILE',
                 'ORDERS_DETAILS',
                 'CONSOLIDATED_COMMENTS',
                 'COLOR',
                 'USER_UPDATE_DATE',
                 'NEW_COMMENTS',
                 'EPISODE_UNEARNED_AMOUNT',
                 'EPISODE_EARNED_AMOUNT',
                 'EPISODE_BILLED_AMOUNT',
                 'EPISODE_ADJUSTMENTS'
                 ]
    episodesummdata = episodesummdata[new_order]

    claimsdetailsdata = chart_utils.get_loaded_data("AXXESS_API.RAW.VW_ALLPAYOR_BILLING_CLAIMS_DETAILS", "DATASET")

   # print(episodesummdata.columns)
   # print(claimsdetailsdata.columns)
    gl_mrn_arr = chart_utils.get_options(episodesummdata, "MRN")
    gl_ins_code_arr = chart_utils.get_options(episodesummdata, "INS_CODE")
    gl_patient_arr = chart_utils.get_options(episodesummdata, "PATIENT")
    gl_patient_status_arr = chart_utils.get_options(episodesummdata, "PATIENT_STATUS")

    remove_cols = ['BRANCH', 'COLUMN_MAPPING', 'COLUMN_PARAMETERS']
    max_date = pd.to_datetime(episodesummdata['EPISODE_END_DATE']).max()
    min_date = pd.to_datetime(episodesummdata['EPISODE_END_DATE']).min()


    children = html.Div([

        # block on the right
        ddk.Block(
            width=100,
            children=[
                ddk.Row([
                    ddk.Block(
                        children=[
                            ddk.ControlCard(
                                orientation='horizontal',
                                width = 100,
                                children=[

                                    html.Details(
                                        [
                                            html.Summary("Filter here"),
                                            html.P(
                                                """Select attributes to fine tune tables."""
                                            ),
                                        ]
                                    ),
                                    ddk.ControlItem(
                                        dcc.Dropdown(

                                            options=gl_ins_code_arr,
                                            multi=True,
                                            placeholder="Select Ins code",
                                            id="op-ins-code-selector"
                                            # value=["Not Yet Started", "Saved"],
                                        )
                                    ),
                                    ddk.ControlItem(
                                        dcc.Dropdown(

                                            options=gl_patient_arr,
                                            multi=True,
                                            placeholder="Select Patient",
                                            id="op-patient-selector"
                                            # value=["Not Yet Started", "Saved"],
                                        )
                                    ),
                                    ddk.ControlItem(
                                        dcc.Dropdown(

                                            options=gl_mrn_arr,
                                            multi=True,
                                            placeholder="Select MRN",
                                            id="op-mrn-selector"
                                            # value=["Not Yet Started", "Saved"],
                                        )
                                    ),
                                    ddk.ControlItem(
                                        dcc.DatePickerRange(
                                            id="op-episode-picker",
                                            min_date_allowed=pd.to_datetime(episodesummdata['EPISODE_START_DATE'].min()
                                            ),
                                            max_date_allowed=max_date,
                                            initial_visible_month=max_date,
                                            start_date=min_date,
                                            end_date=max_date
                                        ),
                                    ),
                                    ddk.ControlItem(
                                            html.Button(
                                                id="op-select-all-rows",
                                                children="Select all matching records",
                                                style={"margin": "auto"},
                                                n_clicks=0,
                                            )
                                    ),
                                ], )
                        ]
                    ),
                ]),
                ddk.Row([
                    ddk.Card(
                        children=[
                            ddk.CardHeader(
                                title="Pending Orders",
                                children=[
                                    html.Div(
                                        [
                                            ddk.Modal(
                                                id="op-modal-btn-outer",
                                                children=[
                                                    html.Button(
                                                        id="op-expand-modal",
                                                        n_clicks=0,
                                                        children="Take action",
                                                    )
                                                ],
                                                target_id="op-modal-content",
                                                hide_target=True,
                                                style={"float": "right"},
                                            ),
                                            ddk.Block(
                                                id="op-modal-content",
                                                children=html.Div(id="op-modal-div"),
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

                                children=[generate_table_layout(episodesummdata, "PENDING ORDERS",
                                                                "pending_tf-table", "MRN", remove_cols)]
                            )
                            ]
                    ),


                ]),

                ddk.Row([
                    ddk.Block(

                        children=[generate_table_layout(claimsdetailsdata, "CLAIMS DETAILS",
                                                        "op_claims_details-table", "MRN",
                                                        remove_cols)]
                    )

                ]),

            ]
        )
    ])

    return children


def generate_table_layout(table_df, title, tableid, sort_cols, remove_cols):
    children = html.Div(
        [
            ddk.Card(
                children=[
                    ddk.CardHeader(
                        children=[
                            html.Div(
                                title, style={"float": "left"},
                            ),

                        ]
                    ),
                    ddk.Block(
                        ddk.DataTable(
                            columns=[
                                {"name": i.replace("_", " ").title(), "id": i}
                                for i in table_df.columns if (i not in remove_cols)
                            ],
                            data=table_df.sort_values(by=sort_cols).to_dict("records"),
                            filter_action="native",
                            sort_action="native",
                            page_action="native",
                            # page_size=10,
                            row_selectable="multi",
                            id=tableid,
                            style_cell={
                                'height': 'auto',
                                # all three widths are needed
                                # 'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                                'fontSize': 12,
                                'font-family': 'sans-serif',
                                'whiteSpace': 'pre',
                                #'wordBreak': 'break-all',
                                'textAlign': 'center'

                            },
                            style_cell_conditional=[

                                                       {
                                                           'if': {'column_id': c},
                                                           'textAlign': 'left'
                                                       } for c in ['ORDERS_DETAILS', 'CONSOLIDATED_COMMENTS', 'NEW_COMMENTS']

                                                   ] + [{'if': {'column_id': 'CONSOLIDATED_COMMENTS'},
                                                         'width': '100px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'left'
                                                         },
                                                        {'if': {'column_id': 'MRN'},
                                                         'width': '90px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },
                                                        {'if': {'column_id': 'INS_CODE'},
                                                         'width': '40px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },
                                                        {'if': {'column_id': 'PATIENT_STATUS'},
                                                         'width': '60px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },
                                                        {'if': {'column_id': 'INSURANCE'},
                                                         'width': '60px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },
                                                        {'if': {'column_id': 'PATIENT'},
                                                         'width': '60px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },

                                                        {'if': {'column_id': 'EPISODE_START_DATE'},
                                                         'width': '70px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },
                                                        {'if': {'column_id': 'EPISODE_END_DATE'},
                                                         'width': '70px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },
                                                        {'if': {'column_id': 'AUTH_REQUIRED'},
                                                         'width': '45px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },
                                                        {'if': {'column_id': 'EPISODE_UNEARNED_AMOUNT'},
                                                         'width': '70px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },
                                                        {'if': {'column_id': 'EPISODE_EARNED_AMOUNT'},
                                                         'width': '70px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },
                                                        {'if': {'column_id': 'EPISODE_BILLED_AMOUNT'},
                                                         'width': '70px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },
                                                        {'if': {'column_id': 'EPISODE_ADJUSTMENTS'},
                                                         'width': '70px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },

                                                        ],
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                }
                            ],
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold',
                                'whiteSpace': 'normal',
                                'textAlign': 'center'
                            },
                            style_table={'overflowX': 'auto', 'maxHeight': '400px', 'overflowY': 'scroll'},
                        ),
                        style={"overflow": "scroll"}
                    ),
                ]
            ),
        ]
    )
    return children


def subset_data(tablename, filtered_vals, start_date, end_date, filter_colname, start_date_fieldname,
                end_date_fieldname):
    data = chart_utils.get_loaded_data(tablename, "DATASET")
    if start_date:
        data = data.loc[data[start_date_fieldname] > start_date]
    if end_date:
        data = data.loc[data[end_date_fieldname] < end_date]
    if filtered_vals:
        data = data.loc[data[filter_colname].isin(filtered_vals)]

    data_table = data.sort_values(by=filter_colname).to_dict("rows")
    return data_table


@app.callback(
    [
        Output("pending_tf-table", "data"),
        Output("op_claims_details-table", "data")
    ],
    [
        Input("op-mrn-selector", "value"),
        Input("op-ins-code-selector", "value"),
        Input("op-patient-selector", "value"),
        Input("op-episode-picker", "start_date"),
        Input("op-episode-picker", "end_date"),
    ],
)
def update_charts(selected_mrns,selected_ins_codes, selected_auth_reqds, start_date, end_date):
    # subset data-table data

    data = chart_utils.get_loaded_data("AXXESS_API.USER_INPUTS.VW_PENDING_ORDERS_TF_SIMPLE", "DATASET")
    ubrev = chart_utils.get_loaded_data("AXXESS_API.RAW.VW_ALLPAYOR_BILLING_CLAIMS_DETAILS", "DATASET")

    if start_date:
        data = data.loc[data["EPISODE_START_DATE"] > start_date]
    if end_date:
        data = data.loc[data["EPISODE_END_DATE"] < end_date]
    if selected_ins_codes:
        try:
            data = data.loc[data["INS_CODE"].isin(selected_ins_codes)]
            ubrev = ubrev.loc[ubrev["INS_CODE"].isin(selected_ins_codes)]
        except (IndexError):
            print('IndexError')
            print(selected_ins_codes)
        except:
            print('Something else went wrong for INS_CODE')
            print(sys.exc_info())
            print(selected_ins_codes)
    if selected_auth_reqds:
        try:
            data = data.loc[data["PATIENT"].isin(selected_auth_reqds)]
            #ubrev = ubrev.loc[ubrev["AUTH_REQUIRED"].isin(selected_mrns)]
        except (IndexError):
            print('IndexError')
            print(selected_mrns)
        except:
            print('Something else went wrong for PATIENT')
            print(sys.exc_info())
            print(selected_mrns)
    if selected_mrns:
        try:
            data = data.loc[data["MRN"].isin(selected_mrns)]
            ubrev = ubrev.loc[ubrev["MRN"].isin(selected_mrns)]

        except (IndexError):
            print('IndexError')
            print(selected_mrns)
        except:
            print('Something else went wrong for MRN')
            print(sys.exc_info())
            print(selected_mrns)

    data_table = data.sort_values(by="MRN").to_dict("records")
    ubrev_table = ubrev.sort_values("MRN").to_dict("records")

    # update cards

    return [data_table, ubrev_table]
