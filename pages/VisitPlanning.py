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
import numpy as np
#from . import OrderProcessingmodal
from datetime import datetime as dt
import datetime
import dash

# Define Formatters


def formatter_currency(x):
    return "${:,.0f}".format(x) if x >= 0 else "(${:,.0f})".format(abs(x))


def formatter_currency_with_cents(x):
    return "${:,.2f}".format(x) if x >= 0 else "(${:,.2f})".format(abs(x))


def formatter_percent(x):
    return "{:,.1f}%".format(x) if x >= 0 else "({:,.1f}%)".format(abs(x))


def formatter_percent_2_digits(x):
    return "{:,.2f}%".format(x) if x >= 0 else "({:,.2f}%)".format(abs(x))


def formatter_number(x):
    return "{:,.0f}".format(x) #if x >= 0 else "({:,.0f})".format(abs(x))


def layout():
    # load data for display
    episodicdata = chart_utils.get_loaded_data("AXXESS_API.RAW.MEDICARE_MCRADV_VISITPLANNING_NOAUTH", "DATASET")
    pervisitdata = chart_utils.get_loaded_data("AXXESS_API.RAW.MANAGEDCARE_VISITPLANNING_NOAUTH", "DATASET")
    currentepisodic = chart_utils.get_loaded_data("AXXESS_API.RAW.VW_MEDICARE_MCRADV_VISITPLANNING_CURRENT_EPISODES","DATASET")
    lupa_riskdata = chart_utils.get_loaded_data("AXXESS_API.RAW.VW_MEDICARE_MCRADV_LUPA_RISK", "DATASET")

   

    #reorder the columns

    '''
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
    '''



    gl_mrn_arr = chart_utils.get_options(episodicdata, "MRN")
    gl_ins_code_arr = chart_utils.get_options(episodicdata, "INS_CODE")
    gl_patient_arr = chart_utils.get_options(episodicdata, "PATIENT")
    gl_patient_status_arr = chart_utils.get_options(episodicdata, "PATIENT_STATUS")
    gl_pcc_arr = chart_utils.get_options(currentepisodic, "CASE_MANAGER_NAME")
    gl_lupa_risk_arr = chart_utils.get_options(currentepisodic, "LUPA_RISK")

    remove_cols = ['INS_CODE', 'OASIS_STATUS', 'OASIS_DETAILS', 'EPISODE_PRIMARY_INSURANCE_NAME', 'DATE_OF_BIRTH',
                   'PHONE','PHYSICIAN_FACSIMILE', 'PHYSICIAN_NAME', 'PHYSICIAN_PHONE', 'ZIP', 'ORDERS_STATUS', 'ORDERS_DETAILS',
                   'EARLY_LUPA_RISK', 'LATE_LUPA_RISK', 'EARLY_ORIGINAL_PROSPECTIVE_PAY',
                   'LATE_ORIGINAL_PROSPECTIVE_PAY', 'TOTAL_COST', 'TOTAL_PROFIT', 'EARLY_COST', 'EARLY_PROFIT',
                   'LATE_COST', 'LATE_PROFIT', 'EPISODE_BILLED_AMOUNT', 'EPISODE_ADJUSTMENTS', 'EPISODE_EARNED_AMOUNT',
                   'EPISODE_UNEARNED_AMOUNT',    'SCHEDULE_ACTIVE',    'COMPLETED_VISITS',    'TOTAL_VISITS' ,   'TOTAL_BILLABLE_HHA_VISITS'
                   ]
    max_date = pd.to_datetime(episodicdata['EPISODE_END_DATE']).max()
    today = dt.now().date()
    sixtydaysprior = today
    sixtydaysprior += datetime.timedelta(days=-60)
    #min_date = pd.to_datetime(episodicdata['EPISODE_END_DATE']).min()


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

                                    ddk.ControlItem(
                                        dcc.Dropdown(

                                            options=gl_ins_code_arr,
                                            multi=True,
                                            placeholder="Select",
                                            id="vp-ins-code-selector",
                                            # value=["Not Yet Started", "Saved"],
                                            style = {
                                                'fontSize': 12,
                                                'font-family': 'sans-serif',
                                            }
                                        ),
                                        width = 10,
                                        label='Billing Code',
                                        style={
                                            'fontSize': 12,
                                            'font-family': 'sans-serif',
                                        }
                                    ),
                                    ddk.ControlItem(
                                        dcc.Dropdown(

                                            options=gl_patient_arr,
                                            multi=True,
                                            placeholder="Select",
                                            id="vp-patient-selector",
                                            style = {
                                                'fontSize': 12,
                                                'font-family': 'sans-serif',
                                            }
                                        ),
                                        width=10,
                                        label='Patient',
                                        label_text_alignment='center',
                                        style={
                                            'fontSize': 12,
                                            'font-family': 'sans-serif',
                                        }
                                    ),
                                    ddk.ControlItem(
                                        dcc.Dropdown(

                                            options=gl_mrn_arr,
                                            multi=True,
                                            placeholder="Select",
                                            id="vp-mrn-selector",
                                            style={
                                                'fontSize': 12,
                                                'font-family': 'sans-serif',
                                            }

                                        ),
                                        width =10,
                                        label='MRN',
                                        label_text_alignment='center',
                                        style={
                                            'fontSize': 12,
                                            'font-family': 'sans-serif',
                                        }
                                    ),
                                    ddk.ControlItem(
                                        dcc.Dropdown(

                                            options=gl_patient_status_arr,
                                            id="vp-patient-status-selector",
                                            multi=True,
                                            placeholder="Select",
                                            value=['Active'],
                                            style={
                                                'fontSize': 12,
                                                'font-family': 'sans-serif',
                                            }

                                        ),
                                        width = 10,
                                        label = 'Patient Status',
                                        label_text_alignment='center',
                                        style={
                                            'fontSize': 12,
                                            'font-family': 'sans-serif',
                                        }
                                    ),
                                    ddk.ControlItem(
                                        dcc.Slider(
                                            id='vp-margin-slider',
                                            min=-50,
                                            max=100,
                                            step=10,
                                            marks={-50: '-50',
                                                   -40: '-40',
                                                   -20: '-20',
                                                   -10: '-10',
                                                   0: '0',
                                                   10: '10',
                                                   20: '20',
                                                   40: '40',
                                                   60: '60',
                                                   80: '80',
                                                   100: '100',
                                                   },
                                            value=20,
                                        ),
                                        width = 20,
                                        label='Margin (%)',
                                        label_text_alignment='center',
                                        style={
                                            'fontSize': 12,
                                            'font-family': 'sans-serif',
                                        }
                                    ),
                                    ddk.ControlItem(
                                        dcc.Dropdown(

                                            options=gl_pcc_arr,
                                            multi=True,
                                            placeholder="select",
                                            id="vp-case-manager-selector",
                                            style={
                                                'fontSize': 12,
                                                'font-family': 'sans-serif',
                                            }
                                        ),
                                        width=10,
                                        label='Case Manager',
                                        label_text_alignment= 'center',
                                        style={
                                            'fontSize': 12,
                                            'font-family': 'sans-serif',
                                        }
                                    ),
                                    ddk.ControlItem(
                                        dcc.DatePickerRange(
                                            id="vp-episode-picker",
                                            min_date_allowed=pd.to_datetime(episodicdata['EPISODE_START_DATE'].min()
                                            ),
                                            max_date_allowed=max_date,
                                            initial_visible_month=max_date,
                                            start_date=sixtydaysprior,
                                            end_date=max_date
                                        ),
                                        width = 20,
                                        label='Episode Range',
                                        label_text_alignment='center',
                                        style={
                                            'fontSize': 12,
                                            'font-family': 'sans-serif',
                                        }
                                    ),
                                    ddk.ControlItem(
                                        dcc.Dropdown(

                                            options=gl_lupa_risk_arr,
                                            multi=True,
                                            placeholder="select",
                                            id="vp-lupa-risk-selector",
                                            style={
                                                'fontSize': 12,
                                                'font-family': 'sans-serif',
                                            }

                                        ),
                                        width=10,
                                        label='LUPA RISK',
                                        label_text_alignment='center',
                                        style={
                                            'fontSize': 12,
                                            'font-family': 'sans-serif',
                                        }
                                    ),

                                ], )
                        ]
                    ),
                ]),
                ddk.Row([
                    ddk.Card(
                        children=[
                            ddk.CardHeader(
                                title="VISIT PLANNING",
                                children=[
                                    html.Div(
                                        [
                                            ddk.Modal(
                                                id="vp-modal-btn-outer",
                                                children=[
                                                    html.Button(
                                                        id="vp-expand-modal",
                                                        n_clicks=0,
                                                        children="Take action",
                                                    )
                                                ],
                                                target_id="vp-modal-content",
                                                hide_target=True,
                                                style={"float": "right"},
                                            ),
                                            ddk.Block(
                                                id="vp-modal-content",
                                                children=html.Div(id="vp-modal-div"),
                                                style={
                                                    "width": "50%",
                                                    "margin": "auto",
                                                    "overflow": "scroll",
                                                },
                                            ),
                                            ddk.DataCard(
                                                id='vp_episodic_selected_count',
                                                value=currentepisodic.shape[0],
                                                label='Episodic Selected Count',
                                                style={
                                                    'fontSize': 12,
                                                    'font-family': 'sans-serif',
                                                }
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                            ddk.Block(

                                dcc.Tabs(id='tabs-example',
                                         value='tab-1',
                                         children=[
                                                    dcc.Tab(label='EPISODIC',
                                                            children=[generate_table_layout(episodicdata, "","vp_episodic-table", "MRN", remove_cols)]
                                                            ),
                                                    dcc.Tab(label='PERVISIT',
                                                            children=[generate_table_layout(pervisitdata, "","vp_pervisit-table", "MRN", remove_cols)]),
                                         ]
                                         ),

                            )
                            ]
                    ),


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
                                                       } for c in ['ORDERS_DETAILS', 'OASIS_DETAILS', 'AUTH #|AUTH TYPE|RANGE|DISCIPLINE|AUTHORIZED|USED|UNUSED|UNITS']

                                                   ] +
                                                   [
                                                       {
                                                           'if': {'column_id': c},
                                                           'width': '100px',
                                                           'textAlign': 'right'
                                                       } for c in ['1-30 days Disc: T/S/C/M','31-60 days Disc: T/S/C/M', 'Visits Disc: T/S/C/M']
                                                   ]
                                                   +
                                                   [{'if': {'column_id': 'CONSOLIDATED_COMMENTS'},
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
                                                   ] + [
                                                       {'if': {'column_id': 'TOTAL_MARGIN',
                                                               'filter_query': '{TOTAL_MARGIN} < 20'},
                                                        'color': 'red'}
                                                        ],
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold',
                                'whiteSpace': 'normal',
                                'textAlign': 'center'
                            },
                            style_table={'overflowX': 'auto',  'overflowY': 'scroll'},
                            #style_table={'overflowX': 'auto', 'maxHeight': '400px', 'overflowY': 'scroll'},
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
        Output("vp_episodic-table", "data"),
        Output("vp_pervisit-table", "data"),
        Output("vp_episodic_selected_count", "value"),


    ],
    [
        Input("vp-mrn-selector", "value"),
        Input("vp-ins-code-selector", "value"),
        Input("vp-patient-selector", "value"),
        Input("vp-patient-status-selector", "value"),
        Input("vp-case-manager-selector", "value"),
        Input("vp-margin-slider", "value"),
        Input("vp-episode-picker", "start_date"),
        Input("vp-episode-picker", "end_date"),
        Input("vp-lupa-risk-selector", "value"),
    ],
)
def update_charts(selected_mrns,selected_ins_codes, selected_patients,selected_patient_status, selected_pccs, selected_margin, start_date, end_date, selected_lupa_risks):
    # subset data-table data

    data = chart_utils.get_loaded_data("AXXESS_API.RAW.VW_MEDICARE_MCRADV_VISITPLANNING_CURRENT_EPISODES", "DATASET")
    pervisitdata = chart_utils.get_loaded_data("AXXESS_API.RAW.MANAGEDCARE_VISITPLANNING_NOAUTH", "DATASET")

    if start_date:
        pervisitdata = pervisitdata.loc[pervisitdata["EPISODE_START_DATE"] > start_date]
        data = data.loc[data["EPISODE_START_DATE"] > start_date]
    if end_date:
        data = data.loc[data["EPISODE_END_DATE"] < end_date]
        pervisitdata = pervisitdata.loc[pervisitdata["EPISODE_END_DATE"] > start_date]
    if selected_ins_codes:
        try:
            data = data.loc[data["INS_CODE"].isin(selected_ins_codes)]
            pervisitdata = pervisitdata.loc[pervisitdata["INS_CODE"].isin(selected_ins_codes)]

        except (IndexError):
            print('IndexError')
            print(selected_ins_codes)
        except:
            print('Something else went wrong for INS_CODE')
            print(sys.exc_info())
            print(selected_ins_codes)
    if selected_patients:
        try:
            data = data.loc[data["PATIENT"].isin(selected_patients)]
            pervisitdata = pervisitdata.loc[pervisitdata["PATIENT"].isin(selected_patients)]

        except (IndexError):
            print('IndexError')
            print(selected_mrns)
        except:
            print('Something else went wrong for PATIENT')
            print(sys.exc_info())
            print(selected_mrns)
    if selected_pccs:
        try:
            data = data.loc[data["CASE_MANAGER_NAME"].isin(selected_pccs)]
            pervisitdata = pervisitdata.loc[pervisitdata["CASE_MANAGER_NAME"].isin(selected_pccs)]

        except (IndexError):
            print('IndexError')
            print(selected_mrns)
        except:
            print('Something else went wrong for CASE_MANAGER_NAME')
            print(sys.exc_info())
            print(selected_mrns)
    if selected_patient_status:
        try:
            data = data.loc[data["PATIENT_STATUS"].isin(selected_patient_status)]
            pervisitdata = pervisitdata.loc[pervisitdata["PATIENT_STATUS"].isin(selected_patient_status)]
        except (IndexError):
            print('IndexError')
            print(selected_mrns)
        except:
            print('Something else went wrong for PATIENT_STATUS')
            print(sys.exc_info())
            print(selected_mrns)
    if selected_mrns:
        try:
            data = data.loc[data["MRN"].isin(selected_mrns)]
            pervisitdata = pervisitdata.loc[pervisitdata["MRN"].isin(selected_mrns)]


        except (IndexError):
            print('IndexError')
            print(selected_mrns)
        except:
            print('Something else went wrong for MRN')
            print(sys.exc_info())
            print(selected_mrns)
    if selected_lupa_risks:
        try:
            data = data.loc[data["LUPA_RISK"].isin(selected_lupa_risks)]

        except (IndexError):
            print('IndexError')
            print(selected_mrns)
        except:
            print('Something else went wrong for MRN')
            print(sys.exc_info())
            print(selected_mrns)
    data['TOTAL_MARGIN'] = pd.to_numeric(data['TOTAL_MARGIN'].replace('nan','-100'))
    data['EARLY_MARGIN'] = pd.to_numeric(data['EARLY_MARGIN'].replace('nan', '-100'))
    data['LATE_MARGIN'] = pd.to_numeric(data['LATE_MARGIN'].replace('nan', '-100'))
    data['EARLY_LUPA_T'] = pd.to_numeric(data['EARLY_LUPA_T'].replace('nan', ''))
    data['LATE_LUPA_T'] = pd.to_numeric(data['LATE_LUPA_T'].replace('nan', ''))

    if  selected_margin <= 100:
        try:
            data = data[(data["TOTAL_MARGIN"] <= selected_margin) | (data["EARLY_MARGIN"] <=selected_margin) | (data["LATE_MARGIN"]<=selected_margin)]
            print ("total margin <= {} = {}", selected_margin, data[(data["TOTAL_MARGIN"] <= selected_margin)].shape[0])
        except (IndexError):
            print('IndexError')
            print(selected_margin)
        except:
            print('Something else went wrong for MRN')
            print(sys.exc_info())
            print(selected_margin)
    #print(data.dtypes)


    # Apply Formatting to the columns

    data['TOTAL_MARGIN'] = data['TOTAL_MARGIN'].apply(formatter_number)
    data['EARLY_MARGIN'] = data['EARLY_MARGIN'].apply(formatter_number)
    data['LATE_MARGIN'] = data['LATE_MARGIN'].apply(formatter_number)
    data['EARLY_LUPA_T'] = data['EARLY_LUPA_T'].apply(formatter_number)
    data['LATE_LUPA_T'] = data['LATE_LUPA_T'].apply(formatter_number)
    #print(data.dtypes)

    data_table  = data.sort_values(by="MRN").to_dict("records") # data.sort_values(["MRN"], axis=0, ascending=True, inplace=True).to_dict("records")
    data_table2 = pervisitdata.sort_values(by="MRN").to_dict("records") #data #data.sort_values(["MRN"], axis=0, ascending=True, inplace=True).to_dict("records")
    selected_row_count = data.shape[0]
    # update cards

    return [data_table, data_table2, selected_row_count]
