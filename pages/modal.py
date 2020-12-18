import dash_design_kit as ddk
import dash_html_components as html
import dash_core_components as dcc
import chart_utils
from app import app, redis_instance
from dash.dependencies import Input, Output, State
import dash
import json
import dash_enterprise_auth

def custom_input_layout(data, patient, task, date):
    children = html.Div(
        children=[
            dcc.Markdown("**Select a task**"),
            html.P("Select a patient"),
            ddk.ControlItem(
                dcc.Dropdown(
                    id="selected-patient",
                    options=[
                        {"label": i, "value": i}
                        for i in sorted([i for i in data["PATIENT"].unique() if i])
                    ],
                    placeholder="Select a patient...",
                    value=patient,
                ),
            ),
            html.P("Select a task for the patient"),
            ddk.ControlItem(
                dcc.Dropdown(
                    id="task-selection",
                    placeholder="Select a task...",
                    disabled=task is None,
                    value=task,
                ),
            ),
            html.P("Select a date for the task"),
            ddk.ControlItem(
                dcc.Dropdown(
                    id="task-date",
                    placeholder="Select a date...",
                    disabled=date is None,
                    value=date,
                ),
            ),
        ],
    )

    return children

def fixed_input_layout(data, selected_rows):
    children = html.Div(
        children=[
            # This div only exists to preserve components with
            # certain IDs so that there are not errors retrieving the
            # selection if it's a custom input
            html.Div(
                children=[
                    dcc.Dropdown(id=i)
                    for i in ["selected-patient", "task-selection", "task-date"]
                ],
                style={"display": "none"},
            ),
            dcc.Markdown("**Take bulk action on selected rows**"),
            html.Div(
                ddk.DataTable(
                    columns=[
                        {"name": i.replace("_", " ").title(), "id": i}
                        for i in data.columns
                    ],
                    page_action="native",
                    page_size=10,
                    data=selected_rows,
                ),
                style={"overflow": "scroll"},
            ),
        ]
    )
    return children


def take_action_layout(data, clinician, status, disabled=False):
    layout = html.Div(
        children=[
            dcc.Markdown("**Update data for the selected task**"),
            html.P("Change assignee"),
            ddk.ControlItem(
                dcc.Dropdown(
                    id="task-assignee",
                    options=[
                        {"label": i, "value": i}
                        for i in sorted([i for i in data["ASSIGNED_TO"].unique() if i])
                        if i
                    ],
                    placeholder="Change task assignee...",
                    value=clinician,
                    disabled=disabled,
                ),
            ),
            html.P("Update task status"),
            ddk.ControlItem(
                dcc.Dropdown(
                    id="task-status",
                    options=[
                        {"label": i, "value": i}
                        for i in sorted([i for i in data["STATUS"].unique() if i])
                    ],
                    placeholder="Change task status...",
                    value=status,
                    disabled=disabled,
                ),
            ),
            html.P("Add a comment"),
            ddk.ControlItem(
                dcc.Input(
                    id="action-items",
                    type="text",
                    placeholder="Type comment here",
                    disabled=disabled,
                ),
            ),
            ddk.ControlItem(
                html.Button(
                    "Submit", id="submit-action", n_clicks=0, style={"margin": "auto"},
                ),
            ),
            html.Div(id="success-message", style={"text-align": "center"},),
        ],
    )

    return layout


# ------------ This callback interprets the values selected in                  -------
# ------------ the modal dropdown and is intended to pass them to the database. -------
@app.callback(
    Output("success-message", "children"),
    [Input("submit-action", "n_clicks")],
    [
        State("task-assignee", "value"),
        State("task-status", "value"),
        State("action-items", "value"),
        State("selected-patient", "value"),
        State("task-selection", "value"),
        State("task-date", "value"),
    ],
)
def submit_request(
    n_clicks,
    new_assignee,
    new_status,
    new_comment,
    selected_patient,
    selected_task,
    selected_date,
):
    """
    Interprets rows input and performs an action on the database by manipulating
    the existing rows and attaching a new status, new assignee, and new comment.
    """
    if n_clicks:
        if not new_assignee and new_status:
            return dcc.Markdown("*INVALID: No inputs provided.*")
        elif not new_assignee:
            return dcc.Markdown("*INVALID: Input a new assignee.*")
        elif not new_status:
            return dcc.Markdown("*INVALID: Input a new status.*")

        if selected_patient:
            data = chart_utils.get_loaded_data()
            selected_rows = data.loc[
                (data["PATIENT"] == selected_patient)
                & (data["SCHEDULED_DATE"] == selected_date)
                & (data["TASK"] == selected_task)
            ].to_dict("records")
        else:
            # The selected rows to perform an operation on are loaded in as records from Redis.
            selected_rows = json.loads(redis_instance.hget("selected_rows", "DATASET"))

        print(selected_rows)
        username = dash_enterprise_auth.get_username()
        userdata = dash_enterprise_auth.get_user_data()

        for record in selected_rows:
            record['NEW_ASSIGNEE'] = new_assignee
            record['NEW_STATUS'] = new_status
            record['NEW_COMMENT'] = new_comment 
            record['USERNAME'] = username 
            record['USERDATA'] = userdata 

        # Perform database updating task on selected rows HERE
        chart_utils.update_data(selected_rows)

        return dcc.Markdown("*Action successfully completed.*")


# ---------------------------------------------------------------------------------------


@app.callback(
    [
        Output("modal-div", "children"),
        Output("expand-modal", "children"),
        Output("expand-modal-2", "children"),
    ],
    [Input("data-table", "selected_rows")],
    [State("data-table", "data")],
)
def populate_modal(selected_ids, table_rows):
    """
    Populate modal input rows based on the selected row from the table.
    """

    data = chart_utils.get_loaded_data("SCHEDULEREPORTS_VISITSBYSTATUS","DATASET")
    selected_rows = None

    if selected_ids:
        selected_rows = [table_rows[i] for i in selected_ids]

        count = len(selected_ids)
        # Autofill the dropdowns if one row is selected
        if count == 1:
            input_layout = custom_input_layout(
                data,
                selected_rows[0]["PATIENT"],
                selected_rows[0]["TASK"],
                selected_rows[0]["SCHEDULED_DATE"],
            )
            action_layout = take_action_layout(
                data, selected_rows[0]["ASSIGNED_TO"], selected_rows[0]["STATUS"],
            )
            button_text = ("Take action (1 patient selected)",)
        # Display the selected rows in a table if many rows are selected
        else:
            input_layout = fixed_input_layout(data, selected_rows)
            action_layout = take_action_layout(data, None, None)
            button_text = ("Bulk action ({} patients selected)".format(count),)
    # Display empty dropdowns if no rows are selected
    else:
        input_layout = custom_input_layout(data, None, None, None)
        action_layout = take_action_layout(data, None, None)
        button_text = "Take action"

    redis_instance.hset("selected_rows", "DATASET", json.dumps(selected_rows))
    modal_content = ddk.ControlCard(children=[input_layout, action_layout])
    return modal_content, button_text, button_text


@app.callback(
    [Output("task-selection", "options"), Output("task-selection", "disabled")],
    [Input("selected-patient", "value")],
)
def select_patient(selected_patient):
    """
    Populate task options based on patient selected
    """
    if selected_patient:
        data = chart_utils.get_loaded_data()
        data = data.loc[data["PATIENT"] == selected_patient]

        return [{"label": x, "value": x} for x in data["TASK"].unique()], False

    return [], True


@app.callback(
    [Output("task-date", "options"), Output("task-date", "disabled")],
    [Input("task-selection", "value"), Input("selected-patient", "value")],
)
def select_date(selected_task, selected_patient):
    """
    Populate date options based on task selected
    """
    if selected_task:
        data = chart_utils.get_loaded_data()
        data = data.loc[data["PATIENT"] == selected_patient]
        data = data.loc[data["TASK"] == selected_task]

        return (
            [{"label": x, "value": x} for x in data["SCHEDULED_DATE"].unique()],
            False,
        )

    return [], True
