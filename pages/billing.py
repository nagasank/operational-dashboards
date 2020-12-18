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
from . import modal
from datetime import datetime, timedelta
import dash


def layout():
    # load data for display
    episodesummdata = chart_utils.get_loaded_data("AXXESS_API.RAW.VW_ALLPAYOR_EPISODE_BILLING_TIMELYFILING", "DATASET")

    #reorder the columns
    new_order = ['INSURANCE_CODE',
                 'INITIAL_TIMELY_FILING',
                 'MRN',
                 'PATIENT',
                 'PATIENT_STATUS',
                 'EPISODE_START_DATE',
                 'EPISODE_END_DATE',
                 'INSURANCE',
                 'AUTH_REQUIRED',
                 'EPISODE_UNEARNED_AMOUNT',
                 'EPISODE_EARNED_AMOUNT',
                 'EPISODE_BILLED_AMOUNT',
                 'EPISODE_ADJUSTMENTS',
                 'ORDERS_DETAILS',
                 'PHYSICIAN_NAME',
                 'PHYSICIAN_PHONE',
                 'PHYSICIAN_FACSIMILE',
                 'Auth #|Auth type|Range|Discipline|Authorized|Used|Unused|Units|']
    episodesummdata = episodesummdata[new_order]

    claimsdetailsdata = chart_utils.get_loaded_data("AXXESS_API.RAW.VW_ALLPAYOR_BILLING_CLAIMS_DETAILS", "DATASET")

   # print(episodesummdata.columns)
   # print(claimsdetailsdata.columns)
    gl_mrn_arr = chart_utils.get_options(episodesummdata, "MRN")
    gl_ins_code_arr = chart_utils.get_options(episodesummdata, "INSURANCE_CODE")
    gl_auth_reqd_arr = chart_utils.get_options(episodesummdata, "AUTH_REQUIRED")
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
                                            id="billing-ins-code-selector"
                                            # value=["Not Yet Started", "Saved"],
                                        )
                                    ),
                                    ddk.ControlItem(
                                        dcc.Dropdown(

                                            options=gl_auth_reqd_arr,
                                            multi=True,
                                            placeholder="Select Auth Reqd Status",
                                            id="billing-auth-reqd-selector"
                                            # value=["Not Yet Started", "Saved"],
                                        )
                                    ),
                                    ddk.ControlItem(
                                        dcc.Dropdown(

                                            options=gl_mrn_arr,
                                            multi=True,
                                            placeholder="Select MRN",
                                            id="billing-mrn-selector"
                                            # value=["Not Yet Started", "Saved"],
                                        )
                                    ),
                                    ddk.ControlItem(
                                        dcc.DatePickerRange(
                                            id="billing-episode-picker",
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
                                                id="billing-select-all-rows",
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
                    ddk.Block(

                        children=[generate_table_layout(episodesummdata, "ALL PAYOR EPISODES",
                                                        "all_payor_episodes-table", "MRN", remove_cols)]
                    )

                ]),

                ddk.Row([
                    ddk.Block(

                        children=[generate_table_layout(claimsdetailsdata, "CLAIMS DETAILS",
                                                        "claims_details-table", "MRN",
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
                                                       } for c in ['OASIS_DETAILS', 'ORDERS_DETAILS', 'AUTH #|AUTH TYPE|RANGE|DISCIPLINE|AUTHORIZED|USED|UNUSED|UNITS|']

                                                   ] + [{'if': {'column_id': 'MRN'},
                                                         'width': '90px',
                                                         'whiteSpace': 'normal',
                                                         'textAlign': 'center'
                                                         },
                                                        {'if': {'column_id': 'INSURANCE_CODE'},
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
        Output("all_payor_episodes-table", "data"),
        Output("claims_details-table", "data")
    ],
    [
        Input("billing-mrn-selector", "value"),
        Input("billing-ins-code-selector", "value"),
        Input("billing-auth-reqd-selector", "value"),
        Input("billing-episode-picker", "start_date"),
        Input("billing-episode-picker", "end_date"),
    ],
)
def update_charts(selected_mrns,selected_ins_codes, selected_auth_reqds, start_date, end_date):
    # subset data-table data

    data = chart_utils.get_loaded_data("AXXESS_API.RAW.VW_ALLPAYOR_EPISODE_BILLING_TIMELYFILING", "DATASET")
    ubrev = chart_utils.get_loaded_data("AXXESS_API.RAW.VW_ALLPAYOR_BILLING_CLAIMS_DETAILS", "DATASET")

    if start_date:
        data = data.loc[data["EPISODE_START_DATE"] > start_date]
    if end_date:
        data = data.loc[data["EPISODE_END_DATE"] < end_date]
    if selected_ins_codes:
        try:
            data = data.loc[data["INSURANCE_CODE"].isin(selected_ins_codes)]
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
            data = data.loc[data["AUTH_REQUIRED"].isin(selected_auth_reqds)]
            #ubrev = ubrev.loc[ubrev["AUTH_REQUIRED"].isin(selected_mrns)]
        except (IndexError):
            print('IndexError')
            print(selected_mrns)
        except:
            print('Something else went wrong for AUTH_REQUIRED')
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
