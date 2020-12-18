import dash_design_kit as ddk
import dash_html_components as html
import chart_utils
import redis
import os
import pandas as pd


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
                            filter_action="native",
                            page_action="native",
                            page_size=10,
                            row_selectable="multi",
                            id=tableid,
                            style_cell={'fontSize': 12, 'font-family': 'sans-serif'},
                            style_table={'overflowX': 'auto'},
                        ),
                        style={"overflow": "scroll"}
                    ),
                ]
            ),
        ]
    )
    return children


if __name__ == "__main__":
    redis_instance = redis.StrictRedis.from_url(os.environ.get("REDIS_URL", "redis://127.0.0.1:6379"))
    arrfreport = chart_utils.get_loaded_data("AR_ROLL_FORWARD_REPORT", "DATASET")
    vw_bc_rap = chart_utils.get_loaded_data("VW_BILLINGCENTER_RAP", "DATASET")
    vw_bc_fin = chart_utils.get_loaded_data("VW_BILLINGCENTER_FINAL", "DATASET")
    ub_billing_per = chart_utils.get_loaded_data("UNBILLED_BILLING_PERIODS", "DATASET")
    unbilled_rev = chart_utils.get_loaded_data("UNBILLED_REVENUE", "DATASET")
    unbilled_man_claims = chart_utils.get_loaded_data("UNBILLED_MANAGED_CLAIMS", "DATASET")
    billing_batch_rep = chart_utils.get_loaded_data("BILLING_BATCH_REPORT", "DATASET")

    patient_status_arr = chart_utils.get_options(arrfreport, "PATIENT_STATUS")
    # discipline_arr = chart_utils.get_options(authorizations_data, "DISCIPLINE")
    # auth_type_arr = chart_utils.get_options(authorizations_data, "AUTHORIZATION_TYPE")
    payor_arr = chart_utils.get_options(arrfreport, "PAYOR")
    patient_arr = chart_utils.get_options(arrfreport, "PATIENT")
    remove_cols = ['BRANCH', 'COLUMN_MAPPING', 'COLUMN_PARAMETERS']

    print(type(arrfreport))
    print(type(arrfreport["MRN"]))
    gl_mrn = arrfreport["MRN"].tolist() + vw_bc_rap["MRN"].tolist() + vw_bc_fin["MRN"].tolist() + vw_bc_fin[
        "MRN"].tolist() + ub_billing_per["MRN"].tolist() + unbilled_rev["MRN"].tolist() + unbilled_man_claims[
                 "MRN"].tolist() + billing_batch_rep["MRN"].tolist()
    # df = gl_mrn,index=['MRN'])
    # gl_mrn_arr = chart_utils.get_options(gl_mrn, "MRN")
    print(type(gl_mrn))
    print(len(gl_mrn))
    gl_mrn = list(set(gl_mrn))
    print(len(gl_mrn))
    df = pd.DataFrame(gl_mrn, columns=['MRN'])
    print(df)
    #    gl_mrn = gl_mrn.unique()
    #print(gl_mrn.shape)
    #print(gl_mrn)
