from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from simulation import Chip  # Assume simulation.py is in the same directory and properly structured

app = Flask(__name__)
cors = CORS(app)

@app.route('/calculate_focal_length', methods=['POST'])
def calculate_focal_length():
    try:
        data = request.json
        spacings = list(map(float, data['spacings']))
        thicknesses = list(map(float, data['thicknesses']))
        diameters = float(data['diameter'])
        voltages = list(map(float, data['voltages']))

        chip = Chip(spacings, thicknesses, diameters)
        focal_length = chip.get_system_focal_length(voltages)

        return jsonify({"focal_length": focal_length})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400

@app.route('/plot_ray', methods=['POST'])
def plot_ray():
    try:
        data = request.json
        angle = float(data['angle'])
        offset = float(data['offset'])
        energy = float(data['energy'])
        voltages = list(map(float, data['voltages']))
        num_datapoints = int(data['num_datapoints'])

        spacings = list(map(float, data['spacings']))
        thicknesses = list(map(float, data['thicknesses']))
        diameter = float(data['diameter'])

        chip = Chip(spacings, thicknesses, diameter)
        buf = BytesIO()
        chip.plot_custom_ray(angle, offset, energy, voltages, num_datapoints)
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return jsonify({'image': 'data:image/png;base64,' + image_base64})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
