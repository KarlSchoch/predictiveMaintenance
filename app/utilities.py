# Import dependencies
import pandas as pd

def table_data():
    # Read in data
    maintenance_guidance = pd.read_csv('./data/maintenance_guidance.csv')
    maintenance_log = pd.read_csv('./data/maintenance_log.csv')
    mileage_log = pd.read_csv('./data/mileage_log.csv')
    vehicle_assignment = pd.read_csv('./data/vehicle_assignment.csv')

    # Clean data
    mileage_log['date'] = pd.to_datetime(mileage_log['date'])

    # Create maintenance schedule
    ## Aggregate tables
    vehicle_profile = mileage_log[['vin','make','model','year']].drop_duplicates()
    maintenance_schedule = maintenance_log.\
        merge(vehicle_profile,on='vin').\
            merge(maintenance_guidance, on=['make','model','year'])
    ## Caclulate next scheduled maintenance
    maintenance_schedule['next_oil_change'] = maintenance_schedule['oil_change_mileage'] + maintenance_schedule['oil_change_frequency']
    maintenance_schedule['next_brake_pad'] = maintenance_schedule['brake_pad_mileage'] + maintenance_schedule['brake_pad_frequency']
    maintenance_schedule = maintenance_schedule[['vin','make','model','year','next_oil_change','next_brake_pad']]

    # Calculate Daily Average Mileage
    ## Calculate min and max dates
    daily_mileage = mileage_log.\
        groupby('vin')[['date','mileage']].\
            agg(['max','min'])
    oneday = pd.Timedelta(days=1)
    daily_mileage = ( 
            daily_mileage['mileage']['max'] - daily_mileage['mileage']['min'] 
            ) / (
                (
                    daily_mileage['date']['max'] - daily_mileage['date']['min']
                ) / oneday 
            )
    ## Create data frame containing min and max dates
    daily_mileage = pd.DataFrame(
        data = list(
            zip(
                [x for x in daily_mileage.index],
                [x for x in daily_mileage]
            )
        ),
        columns=['vin', 'daily_mileage']
        )
    
    # Calculate whether vehicle requires maintenance
    ## Aggregate datasets
    idx = mileage_log.groupby(['vin'])['date'].transform(max) == mileage_log['date']
    agg = mileage_log[idx][['date','vin','mileage']].\
        merge(maintenance_schedule, on='vin').\
            merge(daily_mileage, on='vin').\
                merge(vehicle_assignment, on='vin')
    ## Calculate projected mileage over the next seven and thirty days
    agg['seven_day_mileage'] = agg['mileage'] + ( 7 * agg['daily_mileage'] )
    agg['thirty_day_mileage'] = agg['mileage'] + ( 30 * agg['daily_mileage'] )
    
    return agg

def mileage_forecast(date_projection:str = 'seven') -> pd.DataFrame:
    # Import queried data
    df = table_data()

    # Create Informational Columns
    df['Oil Change'] = df[f'{date_projection}_day_mileage'] >= df['next_oil_change']
    df['Brake Pads'] = df[f'{date_projection}_day_mileage'] >= df['next_brake_pad']
    df['Assigned Officer'] = df['officer_first'] + " " + df['officer_last']

    # Filter df to only include values that require maintenance
    df = df[(df['Oil Change'] == True) | (df['Brake Pads'] == True)]

    return df[['vin', 'make', 'model', 'year', 'mileage', 'Assigned Officer', 'Oil Change', 'Brake Pads']]