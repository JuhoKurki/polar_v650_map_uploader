# Polar V650 map update tool
Experimental tool for updating maps on the Polar V650 device.

### Prerequisites

* Python https://www.python.org/
* MapsForge map file. You can create your own map file here: https://extract.bbbike.org/. Select the format as Mapsforge OSM.

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/JuhoKurki/polar_v650_map_uploader.git
   ```
2. Install requrements
   ```sh
   pip install -r requirements
   ```

### Usage

```sh
   python mapuploader.py path/to/mapfile.map
   ```
* Establishing a connection to the device may require multiple attempts. You can try restarting the device or reconnecting the cable.
* Make sure the Polar FlowSync app is not running in the background.

### License
Distributed under the MIT License. See `LICENSE.txt` for more information.