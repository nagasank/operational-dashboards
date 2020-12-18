import dash
from dash.dependencies import Input, Output
import dash_design_kit as ddk
import dash_core_components as dcc
import dash_html_components as html
import os
import tasks

from app import app
import pages

server = app.server
app.title = "Daily Standup"

update_redis_flag = os.environ.get('UPDATE_REDIS_FLAG')
if not update_redis_flag:
    update_redis_flag = input("Update Redis: Y/N ? -  ")
if update_redis_flag.upper() in ('YES', 'Y'):
    tasks.update_data()
else:
    print("skipping call to update redis cache")

app.layout = ddk.App(
    children=[
        ddk.Header(
            children=[
                dcc.Link(
                    href=app.get_relative_path("/"),
                    children=[ddk.Logo(src=app.get_relative_path("/assets/hnts.png"))],
                ),
                ddk.Title("Daily Standup"),
                html.Div(
                    [
                        html.P(
                             "Powered by",
                             style={"float": "left", 'fontSize': 10, "margin-bottom":"0px"},
                        ),
                        html.Img(
                            src=app.get_asset_url("his.png"),
                            style={
                                "width": "130px",
                                "float": "left",
                                "margin-top": "0px",
                                "margin-left": "5px"
                            }
                        )
                    ]
                ),


            ],
            style={"backgroundColor": "var(--accent_positive)"}
        ),
        ddk.Sidebar([
            ddk.Menu([
                dcc.Link(
                    href=app.get_relative_path('/'),
                    children='Home'
                ),
                dcc.Link(
                    href=app.get_relative_path('/census'),
                    children='Census'
                ),
                dcc.Link(
                    href=app.get_relative_path('/orders'),
                    children='Orders'
                ),
                dcc.Link(
                    href=app.get_relative_path('/authorizations'),
                    children='Authorizations'
                ),

                dcc.Link(
                    href=app.get_relative_path('/bd'),
                    children='Business Development'
                ),
                dcc.Link(
                    href=app.get_relative_path('/qa'),
                    children='Quality Assurance'
                ),
                dcc.Link(
                    href=app.get_relative_path('/billing'),
                    children='Billing'
                ),
            ]),
        ]),
        dcc.Location(id='url', refresh=False),
        ddk.SidebarCompanion(html.Div(id='content'))
    ],
    show_editor=True 
)

@app.callback(
    Output("content", "children"), [Input("url", "pathname")], prevent_initial_call=True
)
def display_content(pathname):
    page_name = app.strip_relative_path(pathname)
    if not page_name:
        # getting executed twice once for page and once for link home
        return pages.home.layout()
    elif page_name == "census":
        #return
        return pages.census.layout()
    elif page_name == "orders":
        #return
        return pages.orders.layout()
    elif page_name == "authorizations":
        #return
        return pages.authorizations.layout()
    elif page_name == "billing":
        return pages.billing.layout()
    elif page_name == "qa":
        return
        #return pages.qa.layout()
    elif page_name == "bd":
        return 
        #return pages.bd.layout()
    else:
        return "404"

if __name__ == "__main__":
    app.run_server(debug=True, threaded=True)
