import openseespy.opensees as ops
import numpy as np

# Initialize model
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Define geometry
width = 5.0  # m
height = 3.0  # m
column_width = 0.3  # m
beam_height = 0.4  # m
beam_width = 0.2  # m

# Create nodes
ops.node(1, 0.0, 0.0)
ops.node(2, width, 0.0)
ops.node(3, 0.0, height)
ops.node(4, width, height)

# Fix base nodes
ops.fix(1, 1, 1, 1)
ops.fix(2, 1, 1, 1)

# Define materials
fc = -30.0  # Concrete compressive strength (MPa)
fy = 420.0  # Steel yield strength (MPa)
E = 200000.0  # Steel elastic modulus (MPa)

# Use Concrete02 material for concrete
ops.uniaxialMaterial('Concrete02', 1, fc, -0.002, fc*0.1, -0.01)

# Use Steel02 material for reinforcement
ops.uniaxialMaterial('Steel02', 2, fy, E, 0.01, 18, 0.925, 0.15)

# Create fiber sections
ops.section('Fiber', 1)
ops.patch('rect', 1, 10, 10, -0.15, -0.15, 0.15, 0.15)  # Core concrete
ops.layer('straight', 2, 3, 0.0001, 0.15, 0.15, 0.15, -0.15)  # Top reinforcement
ops.layer('straight', 2, 3, 0.0001, -0.15, 0.15, -0.15, -0.15)  # Bottom reinforcement

ops.section('Fiber', 2)
ops.patch('rect', 1, 10, 20, -0.1, -0.2, 0.1, 0.2)  # Core concrete
ops.layer('straight', 2, 3, 0.0001, 0.1, 0.2, 0.1, -0.2)  # Top reinforcement
ops.layer('straight', 2, 3, 0.0001, -0.1, 0.2, -0.1, -0.2)  # Bottom reinforcement

# Create elements

# Define geometric transformation
ops.geomTransf('Linear', 1)  # Linear geometric transformation with tag 1
# Define nonlinear beam-column elements
ops.element('nonlinearBeamColumn', 1, 1, 3, 5, 1, 1, '-integration', 'Lobatto')
ops.element('nonlinearBeamColumn', 2, 2, 4, 5, 1, 1, '-integration', 'Lobatto')
ops.element('nonlinearBeamColumn', 3, 3, 4, 5, 2, 1, '-integration', 'Lobatto')

# EIGEN Analysis
num_modes = 3  # Number of modes to compute
eigenvalues = ops.eigen(num_modes)
# for mode in range(1, num_modes + 1):
#     for node in node_tags:
#         eigenvector = ops.nodeEigenvector(node, mode)
#         # Store or process the eigenvector as needed
print("2D reinforced concrete frame model created successfully.")



