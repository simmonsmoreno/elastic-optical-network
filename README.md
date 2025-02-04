# Elastic Optical Network Simulator

## Overview

This project involves developing and testing an Elastic Optical Network (EON) simulator using Python. The simulator includes features such as dynamic lightpath requests, spectrum allocation algorithms (First Fit and Best Gap), and network topology management. The primary goal is to evaluate the efficiency and performance of EONs under various traffic conditions and network topologies.

## Features

- **Network Topology Management**: Utilizes the NetworkX library to create and manipulate graph representations of network topologies.
- **Dynamic Lightpath Requests**: Generates and processes lightpath requests based on exponential distributions for arrival times and durations.
- **Spectrum Allocation Algorithms**: Implements First Fit and Best Gap algorithms to allocate spectrum slots efficiently.
- **Simulation of NSFNET Topology**: Provides simulations based on the NSFNET topology to analyze network performance under realistic conditions.
- **Blocking Probability Calculation**: Evaluates the blocking probability of lightpath requests to measure network efficiency.
- **Resource Management**: Dynamically manages transmitters, receivers, and spectrum slots during simulations.
- **Graphical User Interface (GUI)**: Offers a GUI for easier configuration and visualization of simulations using Tkinter.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/simmonsmoreno/elastic-optical-network.git
   ```
2. Navigate to the project directory:
   ```sh
   cd elastic-optical-network
   ```
3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Run the simulator script:
   ```sh
   python main.py
   ```
2. The script will generate lightpath requests, allocate spectrum using the specified algorithm, and output the simulation results, including the blocking probability and resource utilization.

## Project Structure

```
```
## Project Structure

### unicv-version/
- **basic_version.py**: Basic example of packet generator and packet sink.
- **cinco_nos_version.py**: Simulation with a network of 5 nodes.
- **components/**: Contains various components used in the simulation.
    - **light_path_control.py**: Implements the control logic for lightpath allocation.
    - **light_path_generator.py**: Generates lightpath requests.
    - **light_path_request.py**: Defines the LightPathRequest class.
    - **packet_sink.py**: Receives packets and collects statistics.
- **nsfnet_version.py**: Simulation based on the NSFNET topology.
- **README.md**: Documentation for the unicv-version.
- **teste.py**: Provides a GUI for the simulator using Tkinter.

### uva-version/
- **checkSlots.py**: Script to check available slots.
- **eon-basic-version/**: Basic version of the EON simulator.
    - **elastic-optical-network.py**: Main script for the basic version.
- **eon-red-14-nodos-version/**: Version with a 14-node network.
    - **elastic-optical-network.py**: Main script for the 14-node version.
- **eon-red-5-nodos-version/**: Version with a 5-node network.
    - **Components.py**: Contains various components used in the simulation.
    - **example.py**: Example script for the 5-node version.
- **README.md**: Documentation for the uva-version.
- **test.py**: Test script for the uva-version.
```
```
```

### Descriptions:

- **unicv-version/**: Contains the main versions of the EON simulator.
  - **basic_version.py**: Basic example of packet generator and packet sink.
  - **cinco_nos_version.py**: Simulation with a network of 5 nodes.
  - **components/**: Contains various components used in the simulation.
    - **light_path_control.py**: Implements the control logic for lightpath allocation.
    - **light_path_generator.py**: Generates lightpath requests.
    - **light_path_request.py**: Defines the LightPathRequest class.
    - **packet_sink.py**: Receives packets and collects statistics.
  - **nsfnet_version.py**: Simulation based on the NSFNET topology.
  - **teste.py**: Provides a GUI for the simulator using Tkinter.

## Spectrum Allocation Algorithms

### First Fit

The First Fit algorithm searches for the first available sequence of spectrum slots that can accommodate the requested lightpath. It is fast but may lead to spectrum fragmentation.

### Best Gap

The Best Gap algorithm searches for the smallest available sequence of spectrum slots that can accommodate the requested lightpath. It is more efficient in terms of spectrum utilization but is computationally intensive.

## Results and Analysis

The simulator outputs key metrics such as blocking probability and resource utilization. These metrics help in evaluating the performance and efficiency of the EON under different traffic conditions and network topologies.

## Conclusion

This project demonstrates the potential of Elastic Optical Networks in improving spectrum utilization and reducing blocking probability. The implemented simulator provides a valuable tool for studying EONs and testing various spectrum allocation algorithms.

## Future Work

- Implement additional spectrum allocation algorithms.
- Incorporate energy efficiency metrics.
- Extend the simulator to support larger and more complex network topologies.
- Develop a graphical user interface (GUI) for easier configuration and visualization of simulations.

## Acknowledgements

This project was developed as part of the final year coursework for the Bachelor's degree in Computer Engineering at the University of Cape Verde. Special thanks to the professors and staff at the University of Valladolid for their guidance and support during the mobility period.
