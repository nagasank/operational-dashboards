app.layout = ddk.App([
    ddk.Sidebar(
        foldable=True,
        children=[
            ddk.Logo(src=app.get_asset_url("your-logo.png")),
            ddk.Title('Sidebar Menu'),
            ddk.ControlCard(),
            ddk.Menu([
                ddk.CollapsibleMenu(
                    title='Monetary Data',
                    default_open=False,
                    children=[
                        dcc.Link(
                            [
                                ddk.Icon(icon_name='money-check'),
                                'Monetary Base'
                            ], href='/'),
                            dcc.Link([
                                ddk.Icon(icon_name='chart-line'),
                                'Money Velocity'
                            ], href='/'),
                            dcc.Link([
                                ddk.Icon(icon_name='piggy-bank'),
                                'Reserves'
                            ], href='/'),
                            dcc.Link([
                                ddk.Icon(icon_name='hand-holding-usd'),
                                'Borrowings'
                            ], href='/'),

                    ]
                ),
                dcc.Link([ddk.Icon(icon_name='code-branch'), 'Conditions'], href='/'),
                dcc.Link([ddk.Icon(icon_name='university'), 'Investment'], href='/'),
                dcc.Link([ddk.Icon(icon_name='asterisk'), 'Other'], href='/'),
            ]),
        ]
    ),

    ddk.SidebarCompanion([
        ddk.Card(
            width=50,
            children=[
                ddk.CardHeader(title='Performance'),
                ddk.Graph(figure={
                    'data': [{
                        'x': [1, 2, 3, 4],
                        'y': [4, 1, 6, 9],
                        'line': {'shape': 'spline'}
                    }]
                })
            ]
        ),
        ddk.Card(
            width=50,
            children=[
                ddk.CardHeader(title='Outlook'),
                ddk.Graph(figure={
                    'data': [{
                        'x': [1, 2, 3, 4],
                        'y': [4, 1, 6, 9],
                        'line': {'shape': 'spline'}
                    }]
                })
            ]
        )

    ]),
])