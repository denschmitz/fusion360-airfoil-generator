import json
import random
import matplotlib.pyplot as plt

# Load airfoil data from JSON file
with open('airfoils.json', 'r') as file:
    airfoils = json.load(file)

# Number of airfoils to plot
#num_airfoils_to_plot = 5
num_airfoils_to_plot = len(airfoils)

# Ensure the number to plot does not exceed available airfoils
num_airfoils_to_plot = min(num_airfoils_to_plot, len(airfoils))

# Randomly select airfoils to plot
selected_airfoils = random.sample(list(airfoils.keys()), num_airfoils_to_plot)

# Create a plot for each selected airfoil
for airfoil_name in selected_airfoils:
    coordinates = airfoils[airfoil_name]
    if coordinates:
        x, y = zip(*coordinates)  # Unzip coordinates into x and y lists
        plt.figure()
        plt.plot(x, y, marker='o')
        plt.title(f'Airfoil: {airfoil_name}')
        plt.xlabel('x-coordinate')
        plt.ylabel('y-coordinate')
        plt.grid(True)
        plt.axis('equal')  # Ensure the aspect ratio is equal
        plt.show()
    else:
        print(f'No coordinates found for {airfoil_name}')

pass