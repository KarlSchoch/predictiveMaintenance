from flask import Flask, render_template
from utilities import table_data, mileage_forecast

app = Flask(__name__)

@app.route("/")
def home():
    table_data = table_data()
    seven_days = mileage_forecast('seven')
    thirty_days = mileage_forecast('thirty')
    
    return render_template(
        'main.html', 
        seven_days=seven_days.to_html(classes='data', header="true", index=False),
        thirty_days=thirty_days.to_html(classes='data', header="true", index=False)
        )

if __name__ == '__main__':
    #app.run() 
    app.run('0.0.0.0', debug=True) # allow external access