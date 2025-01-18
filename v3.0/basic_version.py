"""
Simple example of PacketGenerator and PacketSink from the Components module.
Create two exponential rate packet generators and connect them to a sink.
"""
import simpy
from random import expovariate
from components.light_path_generator import LightPathGenerator
from components.packet_sink import PacketSink

def distDuration():
    """Exponential arrival distribution for generators."""
    return expovariate(1/6)  # The duration of the lightpath is calculated as a random variable of exponential type with mean 6

def run_simulation(duration):
    """Run the simulation with the given duration."""
    env = simpy.Environment()  # Create the SimPy environment

    # Create the packet generator and the sink
    ps = PacketSink(env, debug=True)  # Enable debugging for simple output
    pg1 = LightPathGenerator(env, 1, duration, load=0.5)

    # Connect the packet generator to the sink
    pg1.out = ps

    try:
        env.run()  # Run the simulation
    except Exception as e:
        print(f"An error occurred during the simulation: {e}")

def main():
    """Main function to run the simulation."""
    while True:
        try:
            duration = float(input('Duration >> '))
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    run_simulation(duration)

if __name__ == "__main__":
    main()