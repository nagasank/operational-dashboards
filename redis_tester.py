import redis
import json
import os
import pandas as pd

def print_sorted_list(data, rows=0, columns=0, ljust=10):
    """
    Prints sorted item of the list data structure formated using
    the rows and columns parameters
    """

    if not data:
        return

    if rows:
        # column-wise sorting
        # we must know the number of rows to print on each column
        # before we print the next column. But since we cannot
        # move the cursor backwards (unless using ncurses library)
        # we have to know what each row with look like upfront
        # so we are basically printing the rows line by line instead
        # of printing column by column
        lines = {}
        for count, item in enumerate(sorted(data)):
            lines.setdefault(count % rows, []).append(item)
        for key, value in sorted(lines.items()):
            for item in value:
                print (item.ljust(ljust)),
            #print()
    elif columns:
        # row-wise sorting
        # we just need to know how many columns should a row have
        # before we print the next row on the next line.
        for count, item in enumerate(sorted(data), 1):
            print (item.ljust(ljust)),
            if count % columns == 0:
                print()
    else:
        print (sorted(data)) # the default print behaviour

def get_loaded_data(app_name='app-data', redis_key='DATASET'):
    redis_data = redis_instance.hget(app_name, redis_key)
    if redis_data:
        data = json.loads(redis_data)
    else:
        data = {}
    return pd.DataFrame(data)


###layout helper
def get_options(df, column_name):
    df.fillna("", inplace=True)
    options_arr = [{'label': val1, 'value': val1} for val1 in sorted(df[column_name].unique()) if val1]
    return options_arr


if __name__ == "__main__":
    # load data for display

    redis_instance = redis.StrictRedis.from_url(os.environ.get("REDIS_URL", "redis://127.0.0.1:6379"))
    '''
    orders_history_data = get_loaded_data("VW_ORDERS_HISTORY_FULL", "DATASET")
    print(orders_history_data.shape[0])
    pending_df = orders_history_data.loc[orders_history_data["DATA_SOURCE_ARRAY"].str.contains(r'ORDERSPENDINGMDS', na=True)]
    history_df = orders_history_data.loc[
        orders_history_data["DATA_SOURCE_ARRAY"].str.contains(r'ORDERSHISTORY', na=True)]
    tbs_df = orders_history_data.loc[
        orders_history_data["DATA_SOURCE_ARRAY"].str.contains(r'ORDERSTOBESENT', na=True)]
    print(history_df.shape[0])
    print(pending_df.shape[0])
    print(tbs_df.shape[0])
    #test for options passing
    options = get_options(orders_history_data, "TYPE")
    print(options)  '''

    arreport = get_loaded_data("AR_ROLL_FORWARD_REPORT", "DATASET")

    print(arreport.shape[0])
    print(arreport.columns.to_list())
    print_sorted_list(arreport.columns.to_list(),25,1)

    auths = get_loaded_data("VW_AUTHORIZATIONS", "DATASET")

    print(auths.shape[0])
    print(auths.columns.to_list())
    print_sorted_list(auths.columns.to_list(), 25, 1)