import pandas as pd
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

from app import app, user_data
import tradelib as tl


def serve_layout():
    return html.Div(
                [
                    html.Div(
                        [
                            html.Div(id='selected_trade', style={'visibility': 'hidden'}),
                            html.Div(
                                [
                                    html.H5('Select Position To Close:', style={'margin-bottom': '10px'}),
                                    dash_table.DataTable(
                                        id='open_table2',
                                        columns=tl.open_trade_dict,
                                        data=tl.read_trades(user_data['diary_file'], 'open', dict_output=True),
                                        style_table={
                                            'height': '102px',
                                            'overflow-y': 'scroll',
                                        },
                                        style_cell_conditional=[
                                            {
                                                'if': {'column_id': c},
                                                'text-align': 'center'
                                            } for c in ['pair', 'direction']

                                        ],
                                        row_selectable='single',
                                        selected_rows=[0],
                                        style_as_list_view=True,
                                        style_cell={'padding': '5px'},
                                        style_header={'background-color': 'white', 'font-weight': 'bold'}
                                    )
                                ],
                                className='pretty_container seven columns',
                                style={'margin-left': '0', 'padding-top': '5px'}
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H5('Close Position:', style={'margin-bottom': '20px'}),
                                            html.Button('Close', id='close_trade_button', style={'margin-top': '10px'})
                                        ],
                                        style={'justify-content': 'space-between', 'display': 'flex'}
                                    ),

                                    html.Div(
                                        [
                                            html.Pre('Exit Price: \t', style={'line-height': '2.5'}),
                                            dcc.Input(id='exit', placeholder=0, type='number', min=0,
                                                      style={'width': '30%'}),
                                        ],
                                        style={'display': 'flex',  # 'justify-content': 'space-between',
                                               'vertical-align': 'center'}
                                    ),
                                    html.P('Note:', style={'margin-top': '0', 'margin-bottom': '0'}),
                                    dcc.Input(id='note', style={'width': '100%'}, value='')
                                ],
                                className='pretty_container five columns',
                                style={'margin-right': '0', 'margin-left': '0', 'padding-top': '5px'}
                            )
                        ],
                        className='row flex-display',
                    ),
                    html.Div(
                        [
                            html.H5('Closed Trades:'),
                            dash_table.DataTable(
                                id='closed_table',
                                columns=tl.closed_trade_dict,
                                data=tl.read_trades(user_data['diary_file'], 'closed', dict_output=True),
                                style_table={
                                  'height': '270px',
                                  'overflow-y': 'scroll'
                                },
                                # You can use style conditional to color profitable and losing trades!
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'text-align': 'center'
                                    } for c in ['pair', 'direction', 'type']
                                ],
                                style_data_conditional=[
                                    {
                                        'if': {
                                            'column_id': 'P/L (%)',
                                            'filter_query': '{P/L (%)} > 0',
                                        },
                                        'backgroundColor': '#3D9970',
                                        'color': 'white',
                                    },
                                    {
                                        'if': {
                                            'column_id': 'P/L (%)',
                                            'filter_query': '{P/L (%)} < 0',
                                        },
                                        'backgroundColor': '#A83232',
                                        'color': 'white',
                                    }
                                ],
                                style_as_list_view=True,
                                style_cell={'padding': '5px'},
                                style_header={'background-color': 'white', 'font-weight': 'bold'}
                            )
                        ],
                        className='pretty_container twelve columns',
                        style={'margin-top': '0', 'padding-top': '5px'}
                    )

                ],
            )


@app.callback([Output('closed_table', 'data'),
               Output('open_table2', 'data'),
               Output('close_trade_button', 'style')],
              [Input('close_trade_button', 'n_clicks')],
              [State('open_table2', 'selected_rows'),
               State('exit', 'value'),
               State('note', 'value')])
def close_trade(clicks, selected_row, close, note):
    record_file = user_data['diary_file']
    if clicks is None:
        closed_trades = tl.read_trades(record_file, 'closed', dict_output=True)
        open_trades = tl.read_trades(record_file, 'open', dict_output=True)

    elif close is None:
        closed_trades = tl.read_trades(record_file, 'closed', dict_output=True)
        open_trades = tl.read_trades(record_file, 'open', dict_output=True)
        style = {'color': '#fc3003', 'border-color': '#fc3003'}
    else:
        # Retrieve the trade that we want to close:
        open_trades = tl.read_trades(record_file, 'open')
        trade = open_trades.iloc[selected_row]
        # NOTE that trade is still a df and not a series, because we put a list inside iloc

        # Compute features of the closed trade:
        closed_trade = tl.fill_trade(trade, close, note)
        # Write the trade to the records:
        tl.write_trade_to_records(record_file, 'closed', closed_trade)
        # Remove the open trade from the open trade records:
        tl.remove_trade_from_records(record_file, selected_row[0])
        # Update the running average features:
        tl.update_user_data(closed_trade)

        closed_trades = tl.read_trades(record_file, 'closed', dict_output=True)
        open_trades = tl.read_trades(record_file, 'open', dict_output=True)

        style = {}

    return closed_trades, open_trades, style
