import datetime
import json
import os
import pandas as pd
from celery import Celery
import redis
from celery.schedules import crontab
import random
from dash_design_kit import datasets
import numpy as np
import snowflake.connector
from snowflake.connector import DictCursor
import sqlalchemy 
from SnowflakeConnection import SnowflakeConnection

# We define our celery broker as well as our redis instance in the following two lines.
celery_app = Celery("Celery App", broker=os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")+'/4')
redis_instance = redis.StrictRedis.from_url(os.environ.get("REDIS_URL", "redis://127.0.0.1:6379"))

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # celery periodic task
    # This command invokes a celery task at an interval of every 1 hour. You can change this.
    #crontab(hour=7, minute=30, day_of_week=1)
    #sender.add_periodic_task(crontab(hour=11, minute=30, day_of_week='mon-fri'), update_data.s(), name="Update data")
    #sender.add_periodic_task(7200, update_data.s(), name="Update_data")
    sender.add_periodic_task(crontab(hour='*/1', minute=0), update_data.s(), name="update_data")

@celery_app.task
def update_data():
    """TODO:  Change all names to fully qualified names"""
    table_names = [
        #"ACTUAL_CLAIMS",
        "ADJUSTMENT_REPORT",
        "ADMISSIONS",
        "AR_ROLL_FORWARD_REPORT",
        "CLAIM_ACTIVITY",
        "DDE_TIMELYFILING",
        "DELETED_PATIENTS",
        "HOME_QACENTER",
        "HOSPITALIZATION_LOGS",
        "LENGTH_OF_STAY_CERT",
        "MANAGED_AGED_AR_EXPANDED",
        "MEDICARE_AGED_AR_EXPANDED",
        "MONTH_END_AR",
        "PATIENTADMISSIONS_INTERNAL_REFERRAL_SOURCE",
        "PATIENTS_NONADMISSIONS",
        "PATIENTS_PENDINGADMISSIONS",
        "PATIENT_ROSTER",
        "PATIENT_SOC_CERTPERIOD",
        "PHYSICIAN_ORDER_HISTORY",
        "REFERRAL_LOG",
        "SCHEDULEREPORTS_DETAILS",
        "SCHEDULEREPORTS_VISITSBYSTATUS",
        "UNBILLED_VISITS",
        "VIEW_ORDERSMANAGEMENT_ORDERSPENDINGMDS",
        "VIEW_ORDERSTOBESENT",
        #VIEWS CREATED
        "VW_ACTUAL_CLAIMS",
        "VW_AUTHORIZATIONS",
        "VW_BILLINGCENTER_FINAL",
        "VW_BILLINGCENTER_RAP",
        "VW_BILLING_BATCH_REPORT",
        "VW_CLAIMS_BY_STATUS",
        "VW_MANAGED_AR",
        "VW_MEDICARE_AGED_AR",
        "VW_MEDICARE_HMO_PAYMENT",
        "VW_MISSING_AUTHORIZATIONS",
        "VW_ORDERS_HISTORY_FULL",
        "VW_OUTSTANDING_CLAIMS",
        "VW_PATIENT_ROSTER",
        "VW_UNBILLED_BILLING_PERIODS",
        "VW_UNBILLED_MANAGED_CLAIMS",
        "VW_UNBILLED_REVENUE",
        "VW_VISITSBYSTATUS_TASK_CATEGORY",
        "AXXESS_API.RAW.VW_ALLPAYOR_EPISODE_BILLING_TIMELYFILING",
        "AXXESS_API.RAW.VW_ALLPAYOR_BILLING_CLAIMS_DETAILS",
        "AXXESS_API.USER_INPUTS.VW_PENDING_ORDERS_TF_SIMPLE",
        "AXXESS_API.RAW.MEDICARE_MCRADV_VISITPLANNING_NOAUTH",
        "AXXESS_API.RAW.MANAGEDCARE_VISITPLANNING_NOAUTH",
        "AXXESS_API.RAW.VW_MEDICARE_MCRADV_LUPA_RISK",
        "AXXESS_API.RAW.VW_MEDICARE_MCRADV_VISITPLANNING_CURRENT_EPISODES"
    ]
    # To do: loop over table names and set table name as the app-data
    reportsdataobj = SnowflakeConnection(account=os.environ.get('SNOWSQL_ACCOUNT'))
    for t in table_names:
        df = pd.DataFrame()
        df = reportsdataobj.get_dfbytable('HNTS_REVENUE_CYCLE', 'RAW', t)
        # In the following command, we are saving the updated dataframe to redis as a JSON string after appending a new row.
        redis_instance.hset(t, "DATASET", json.dumps(df.to_dict("records")))
    reportsdataobj.conn.close()
