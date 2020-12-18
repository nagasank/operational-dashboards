import sys
import os
import json
import snowflake.connector
from snowflake.connector import DictCursor
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
import pandas as pd

class SnowflakeConnection(object):
    """
        This class can be used to get snowflake connection object by passing in credential details
        Args:
            account (str): Snowflake account name. For example: aws_cas2
            config_file (str): Name of the file that contains snowflake credentials and context settings
            auth_type (str): basic or sso. For basic auth_type, connect using username and password.
                                For sso auth type, connect using username and password for Identity Provider (OKTA)

        Attributes:
          Required:
              account (str): Snowflake account name. For example: aws_cas2
              config_file (str): Name of the file that contains snowflake credentials and context settings
              auth_type (str): basic or sso. For basic auth_type, connect using username and password.
                                For sso auth type, connect using username and password for Identity Provider (OKTA)
    """

    def __init__(self,
                 account,
                 config_file='',
                 auth_type='basic',
                 connector_type='snowflake_connector'
                ):
        """
        Initialize api_info with api credentials based on context set
        """
        self.account = account
        self.config_file = config_file
        self.auth_type = auth_type
        self.connector_type = connector_type
        self._get_credentials()
        self._set_connection()

    def _get_credentials(self):
        """
        get snowflake credentials - Populate this from a config file
        """
        if self.config_file:
            with open(self.config_file) as f:
                config_str = f.read()
                credentials_dict = json.loads(config_str)
                self.credentials = credentials_dict[self.account][self.auth_type]
        else:
            self.credentials = {
                "account": os.environ.get('SNOWSQL_ACCOUNT'),
                "user": os.environ.get('SNOWSQL_USER'),
                "password": os.environ.get('SNOWSQL_PWD')
            }

    def fetch_pandas_sqlalchemy(self, sql):
        rows = pd.DataFrame()
        print(sql)
        for chunk in pd.read_sql_query(sql, self.conn, chunksize=500000):
            rows = pd.concat([rows,chunk])
        return rows

    def _set_connection(self):
        if self.auth_type == 'basic' and self.connector_type == 'snowflake_connector':
            self.conn = snowflake.connector.connect(
            user=self.credentials['user'],
            password=self.credentials['password'],
            account=self.credentials['account'])
        if self.auth_type == 'basic' and self.connector_type == 'snowflake_sqlalchemy':
            engine = create_engine(URL(
                account=self.credentials['account'],
                user=self.credentials['user'],
                password=self.credentials['password']))
            self.conn = engine.connect()

    def get_dfbytable(self,
                        db_name='HNTS_REVENUE_CYCLE',
                        schema_name='RAW',
                        table_name='SCHEDULEREPORTS_VISITSBYSTATUS'):
        """change sqltext to use sqlalchemy native functions """
        if table_name.count('.') == 2:
            sqltext = f"""SELECT * FROM {table_name}"""
        elif table_name.count('.') == 1:
            sqltext = f"""SELECT * FROM {db_name}.{table_name}"""
        else:
            sqltext = f"""SELECT * FROM {db_name}.{schema_name}.{table_name}"""
        if self.connector_type == 'snowflake_sqlachemy':
            df = self.fetch_pandas_sqlalchemy(sqltext)
        else:
            df = pd.read_sql(sqltext,self.conn)
        df = df.astype(str)
        return df

    def get_dfbysql(self, sqltext):
        if self.connector_type == 'snowflake_sqlachemy':
            df = self.sf_conn.fetch_pandas_sqlalchemy(sqltext)
        else:
            df = pd.read_sql(sqltext,self.conn)
        df = df.astype(str)
        return df

if __name__ == '__main__':
    reportsdataobj = SnowflakeConnection(account='ada72490')
    df = reportsdataobj.get_dfbytable('HNTS_REVENUE_CYCLE', 'RAW', 'SCHEDULEREPORTS_VISITSBYSTATUS')
    #print(df)
    print(df.columns)
    df = df[df['STATUS'].isin(['Not Yet Started', 'Saved'])]
    print(df.info())
    df_agg = df.groupby(['STATUS', 'TASK']).size().reset_index(name='COUNTS')
    df = df.astype(str)
    print(df.head(10))
    print(df.info())
    print(df_agg)
    print(df.shape[0])
    print(df_agg['COUNTS'].sum())
    df = reportsdataobj.get_dfbysql("""
            select split_part(MRN, '-', 1) as Insurance_code
            , *
            from HNTS_REVENUE_CYCLE.RAW.PATIENT_ROSTER""")
    print(df.columns)
    print(df.shape)