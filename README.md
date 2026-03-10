# Last-Mile Delivery Routing Optimization 🚚🛵🏃‍♂️

A heuristic optimization and routing algorithm designed to solve a complex Vehicle Routing Problem with Time Windows (VRPTW) for last-mile delivery. 
*This project was developed for the LG CNS Optimization Competition (2024).*

## 📌 Overview
In modern last-mile delivery systems, efficiently bundling orders and assigning them to the right delivery riders is critical. This project implements a custom heuristic algorithm to minimize total delivery time and costs while strictly adhering to real-world constraints such as varying rider capacities, speeds, and strict delivery deadlines.

## 🚦 Problem Definition (VRPTW Variant)
The algorithm processes multiple delivery orders and assigns them to a heterogeneous fleet of riders.
* **Heterogeneous Fleet:** Utilizes different rider types (`CAR`, `BIKE`, `WALK`), each with distinct characteristics in speed, volume capacity, and base cost.
* **Time Windows:** Every order has a specific `order_time`, preparation time (`cook_time`), and a strict `deadline`.
* **Capacity Constraints:** The bundled volume of orders cannot exceed the assigned rider's maximum carrying capacity.
* **Objective:** Minimize the average delivery cost across all completed bundles while ensuring zero deadline violations.

## 🧠 Algorithm & Approach
Instead of relying solely on heavy commercial solvers, this project implements a highly customized heuristic approach to quickly generate feasible solutions within tight time limits:
* **Greedy Merge Strategy:** Iteratively evaluates pairs of single orders to form efficient delivery bundles based on geographic proximity (distance matrix) and temporal compatibility.
* **Feasibility Checking:** Built robust validation logic to continuously check for maximum volume constraints and ensure all delivery sequences meet their deadlines.
* **Iterative Improvement:** Dynamically updates bundles and tests alternative rider assignments to continuously lower the objective cost until the computation time limit is reached.

## 🛠 Tech Stack
* **Language:** Python
* **Data Processing & Math:** NumPy, JSON handling
* **Visualization:** Matplotlib (for plotting time-window scatter plots, pickup/delivery flows, and deadline tracking)

## 📈 Visualization
The project includes a custom visualization module (`routing_utils.py`) to graphically represent the routing schedules. It plots the exact time intervals from 'Ready Time' to 'Deadline' for each order, overlaid with the algorithm's selected pickup and delivery times, providing a clear visual confirmation of constraint satisfaction.

## 💡 Key Takeaways
This project showcases the ability to translate complex business rules into mathematical constraints and implement efficient algorithms from scratch. It highlights strong problem-solving skills in operations research, specifically in designing custom heuristic logic that performs reliably under computational time limits.
