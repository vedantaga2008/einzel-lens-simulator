import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [inputs, setInputs] = useState({
        spacings: '',
        thicknesses: '',
        diameter: '',
        voltages: '',
        angle: '',
        offset: '',
        energy: '',
        numDatapoints: ''
    });
    const [focalLength, setFocalLength] = useState('');
    const [plotImage, setPlotImage] = useState('');

    const handleChange = (event) => {
        const { name, value } = event.target;
        setInputs(inputs => ({ ...inputs, [name]: value }));
    };

    const handleFocalLengthCalculation = async (event) => {
        event.preventDefault();
        try {
            const response = await axios.post('http://localhost:5000/calculate_focal_length', {
                spacings: inputs.spacings,
                thicknesses: inputs.thicknesses,
                diameter: inputs.diameter,
                voltages: inputs.voltages
            });
            setFocalLength(`System Focal Length: ${response.data.focal_length} meters`);
        } catch (error) {
            console.error('Error fetching focal length:', error);
        }
    };

    const handleRayPlotting = async (event) => {
        event.preventDefault();
        try {
            const response = await axios.post('http://localhost:5000/plot_ray', {
                spacings: inputs.spacings,
                thicknesses: inputs.thicknesses,
                diameter: inputs.diameter,
                voltages: inputs.voltages,
                angle: inputs.angle,
                offset: inputs.offset,
                energy: inputs.energy,
                numDatapoints: inputs.numDatapoints
            });
            setPlotImage(response.data.image);
        } catch (error) {
            console.error('Error plotting ray:', error);
        }
    };

    return (
        <div>
            <h1>Einzel Lens Simulator</h1>
            <form>
                <label>
                    Spacings (comma-separated, in meters):
                    <input type="text" name="spacings" value={inputs.spacings} onChange={handleChange} />
                </label>
                <label>
                    Thicknesses (comma-separated, in meters):
                    <input type="text" name="thicknesses" value={inputs.thicknesses} onChange={handleChange} />
                </label>
                <label>
                    Aperture Diameter (in meters):
                    <input type="text" name="diameter" value={inputs.diameter} onChange={handleChange} />
                </label>
                <label>
                    Voltages (comma-separated, in volts):
                    <input type="text" name="voltages" value={inputs.voltages} onChange={handleChange} />
                </label>
                <label>
                    Electron Release Angle (in radians):
                    <input type="text" name="angle" value={inputs.angle} onChange={handleChange} />
                </label>
                <label>
                    Electron Release Offset (in meters):
                    <input type="text" name="offset" value={inputs.offset} onChange={handleChange} />
                </label>
                <label>
                    Electron Release Energy (in electron volts):
                    <input type="text" name="energy" value={inputs.energy} onChange={handleChange} />
                </label>
                <label>
                    Number of Datapoints:
                    <input type="text" name="numDatapoints" value={inputs.numDatapoints} onChange={handleChange} />
                </label>
                <button onClick={handleFocalLengthCalculation}>Calculate Focal Length</button>
                <button onClick={handleRayPlotting}>Plot Ray Path</button>
            </form>
            {focalLength && <p>{focalLength}</p>}
            {plotImage && <img src={plotImage} alt="Electron Ray Trace" />}
        </div>
    );
}

export default App;
