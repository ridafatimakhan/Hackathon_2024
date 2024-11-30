from flask import Flask, render_template, jsonify
import pdbufr
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data')
def get_data():
    # Path to the BUFR file
    file_path = os.path.join(os.getcwd(), 'ISAD30_EEMH_291450_291124_145805')
    
    # Columns to include in the output
    selected_columns = [
        "#1#longStationName",  # x-axis values
        "#1#windSpeed",
        "#1#totalPrecipitationOrTotalWaterEquivalent",
        "#1#dewpointTemperature",
        "#1#airTemperature",
        "#1#maximumWindGustSpeed"
    ]
    
    try:
        # Read BUFR data into a DataFrame
        df = pdbufr.read_bufr(file_path, flat=True)
        
        # Filter only the selected columns
        filtered_df = df[selected_columns]
    except KeyError as e:
        return jsonify({"error": f"Column not found: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Convert filtered DataFrame to JSON, handling NaN values
    data_json = filtered_df.to_dict(orient='records')
    for record in data_json:
        for key, value in record.items():
            if isinstance(value, float) and (pd.isna(value) or value != value):  # NaN check
                record[key] = None  # Replace NaN with None
    
    return jsonify(data_json)

@app.route('/statistics/<variable>')
def get_statistics(variable):
    # Path to the BUFR file
    file_path = os.path.join(os.getcwd(), 'ISAD30_EEMH_291450_291124_145805')
    
    try:
        # Read BUFR data into a DataFrame
        df = pdbufr.read_bufr(file_path, flat=True)
        
        # Check if the variable exists
        if variable not in df.columns:
            return jsonify({"error": f"Variable {variable} not found"}), 400
        
        # Drop NaN values and calculate statistics
        column_data = df[variable].dropna()
        stats = {
            "mean": column_data.mean(),
            "min": column_data.min(),
            "max": column_data.max(),
            "std": column_data.std()
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
