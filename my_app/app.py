# Import Dependencies
import pandas
from shiny import App, render, ui
from table_data import table_data
table_data = table_data()

# Define Functions
def mileage_projection(date_projection:str = 'seven') -> pandas.DataFrame:
    # Import queried data
    df = table_data

    # Create Informational Columns
    df['Oil Change'] = df[f'{date_projection}_day_mileage'] >= df['next_oil_change']
    df['Brake Pads'] = df[f'{date_projection}_day_mileage'] >= df['next_brake_pad']
    df['Assigned Officer'] = df['officer_first'] + " " + df['officer_last']

    # Filter df to only include values that require maintenance
    df = df[(df['Oil Change'] == True) | (df['Brake Pads'] == True)]

    return df[['vin', 'make', 'model', 'year', 'mileage', 'Assigned Officer', 'Oil Change', 'Brake Pads']]

def format_table(df:pandas.DataFrame):
    table = df.\
        style.\
        hide(axis='index').\
        set_table_attributes(
            'class="dataframe shiny-table table"'
        ).\
        background_gradient(
            cmap='YlOrRd',
            vmin=False, vmax=True, 
            subset=['Oil Change', 'Brake Pads']
        )
    print(type(table))
    return table

# UI
app_ui = ui.page_fluid(
    ui.h2("Fleet Maintenance Tracker"),
    ui.h4("Maintenance due within Seven Days"),
    ui.output_table('seven_day_maint'),
    ui.h4("Maintenance due within Thirty Days"),
    ui.output_table('thirty_day_maint'),
)

# Server
def server(input, output, session):
    @output
    @render.table
    def seven_day_maint():        
        df = mileage_projection(date_projection = 'seven')
        return format_table(df)

    @output
    @render.table
    def thirty_day_maint():
        df = mileage_projection(date_projection = 'thirty')
        return format_table(df)

app = App(app_ui, server)
