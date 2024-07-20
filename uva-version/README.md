# Elastic Optical Network Simulator

## Overview

This project focuses on the development and testing of an Elastic Optical Network (EON) simulator using Python. The simulator incorporates key features such as dynamic lightpath requests, spectrum allocation algorithms (First Fit and Best Gap), and network topology management. The primary goal is to evaluate the efficiency and performance of EONs under various traffic conditions and network topologies.

## Features

- **Network Topology Management**: Uses the NetworkX library to create and manipulate graph representations of network topologies.
- **Dynamic Lightpath Requests**: Generates and processes lightpath requests based on exponential distributions for arrival times and durations.
- **Spectrum Allocation Algorithms**: Implements First Fit and Best Gap algorithms to allocate spectrum slots efficiently.
- **Simulation of NSFNET Topology**: Provides simulations based on the NSFNET topology to analyze network performance under realistic conditions.
- **Blocking Probability Calculation**: Evaluates the blocking probability of lightpath requests to measure network efficiency.
- **Resource Management**: Manages transmitters, receivers, and spectrum slots dynamically during simulations.

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

eon-basic-version/
  - elastic-optical-network.py
eon-red-14-nodos-version/
  - elastic-optical-network.py
eon-red-5-nodos-version/
  - Components.py
  - example.py
README.md
checkSlots.py
test.py

### Descriptions:

eon-basic-version/: Contains the basic version of the EON simulator.
elastic-optical-network.py: Main script for the basic EON simulation.
eon-red-14-nodos-version/: Contains the version of the EON simulator for a network with 14 nodes.
elastic-optical-network.py: Main script for the 14-node EON simulation.
eon-red-5-nodos-version/: Contains the version of the EON simulator for a network with 5 nodes.
Components.py: Defines various components used in the simulation.
example.py: Example script demonstrating the use of the components.
README.md: Project documentation.
checkSlots.py: Contains functions for slot checking algorithms (First Fit and Best Gap).
test.py: Script for testing and visualizing paths in a graph.

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