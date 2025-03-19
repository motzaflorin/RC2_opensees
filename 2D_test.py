from openseespy.opensees import *

from math import asin, sqrt

# Two dimensional Frame: Eigenvalue & Static Loads

# only eigen analysis done
#  etabs model is 2d_model_portal


# REFERENCES:
# used in verification by SAP2000:
# SAP2000 Integrated Finite Element Analysis and Design of Structures, Verification Manual,
# Computers and Structures, 1997. Example 1.
# and seismo-struct (Example 10)
# SeismoStruct, Verification Report For Version 6, 2012. Example 11.


# set some properties
wipe()

model('Basic', '-ndm', 2)

# properties

#    units kip, ft

numBay = 2
numFloor = 2

bayWidth = 5
storyHeights = [3, 3]

E = 33000 * 1000 #(kN / m2)
massX = (650+500) / 1000 # kN
m_node_1 = (650+500) / 1000 # kN
m_node_2 = (375+500) / 1000 # kN
m_node_3 = (650+100) / 1000 # kN
m_node_4 = (375+1000) / 1000 # kN
massX_2 = [0,0,0,m_node_1,m_node_3,m_node_1,m_node_2,m_node_4,m_node_2]
M = 0.
coordTransf = "Linear"  # Linear, PDelta, Corotational
massType = "-lMass"  # -lMass, -cMass

beams = ['BeamSec','BeamSec']
eColumn = ['ColSec1','ColSec1','ColSec1','ColSec1']
iColumn = ['ColSec2','ColSec2']
columns = [eColumn, iColumn, eColumn]

WSection = {
    'BeamSec': [0.08, 0.001066],
    'ColSec1': [0.09, 0.000675],
    'ColSec2': [0.09, 0.000675]
}

nodeTag = 1


# procedure to read
def ElasticBeamColumn(eleTag, iNode, jNode, sectType, E, transfTag, M, massType):
    found = 0

    prop = WSection[sectType]

    A = prop[0]
    I = prop[1]
    element('elasticBeamColumn', eleTag, iNode, jNode, A, E, I, transfTag, '-mass', M, massType)


# add the nodes
#  - floor at a time
yLoc = 0.
for j in range(0, numFloor + 1):

    xLoc = 0.
    for i in range(0, numBay + 1):
        node(nodeTag, xLoc, yLoc)
        xLoc += bayWidth
        nodeTag += 1

    if j < numFloor:
        storyHeight = storyHeights[j]

    yLoc += storyHeight

# fix first floor
fix(1, 1, 1, 1)
fix(2, 1, 1, 1)
fix(3, 1, 1, 1)

# rigid floor constraint & masses
# Starting node tag
nodeTag = 1
nodeTagR = 5  # Node for the rigid floor constraint (starting at node 5 for the 1st floor)

# Iterate over the floors and bays to assign masses and constraints
for j in range(0, numFloor + 1):
    for i in range(0, numBay + 1):

        # Ensure we are within the 9 nodes
        if nodeTag <= 9:
            # Get the mass for the current node from the list
            massValueX = massX_2[nodeTag - 1]  # List is 0-indexed, so subtract 1

            # Assign mass to the current node (assuming massX is the mass in the X direction)
            mass(nodeTag, massValueX, 1.0e-10, 1.0e-10)  # Adjust as needed for other directions (Y, Z)

            # If this node is not the rigid floor node, apply the equalDOF constraint
            if nodeTag != nodeTagR:
                equalDOF(nodeTagR, nodeTag, 1)  # Apply equalDOF to tie the nodes together (rigid floor)

        # Increment nodeTag for the next node
        nodeTag += 1

    # Update nodeTagR for the next floor's rigid node
    nodeTagR += 1  # Move to the next floor's rigid node

# add the columns
# add column element
geomTransf(coordTransf, 1)
eleTag = 1
for j in range(0, numBay + 1):

    end1 = j + 1
    end2 = end1 + numBay + 1
    thisColumn = columns[j]

    for i in range(0, numFloor):
        secType = thisColumn[i]
        ElasticBeamColumn(eleTag, end1, end2, secType, E, 1, M, massType)
        end1 = end2
        end2 += numBay + 1
        eleTag += 1

# add beam elements
for j in range(1, numFloor + 1):
    end1 = (numBay + 1) * j + 1
    end2 = end1 + 1
    secType = beams[j - 1]
    for i in range(0, numBay):
        ElasticBeamColumn(eleTag, end1, end2, secType, E, 1, M, massType)
        end1 = end2
        end2 = end1 + 1
        eleTag += 1

# calculate eigenvalues & print results
numEigen = 3
eigenValues = eigen(numEigen)
PI = 2 * asin(1.0)

#
# apply loads for static analysis & perform analysis
#

# timeSeries('Linear', 1)
# pattern('Plain', 1, 1)
# load(22, 20.0, 0., 0.)
# load(19, 15.0, 0., 0.)
# load(16, 12.5, 0., 0.)
# load(13, 10.0, 0., 0.)
# load(10, 7.5, 0., 0.)
# load(7, 5.0, 0., 0.)
# load(4, 2.5, 0., 0.)
#
# integrator('LoadControl', 1.0)
# algorithm('Linear')
# analysis('Static')
# analyze(1)

# determine PASS/FAILURE of test
ok = 0

#
# print pretty output of comparisons
#

#               SAP2000   SeismoStruct
comparisonResults = [[0.143, 0.049, 0.009, 0.008, 0.006, 0.005, 0.004],
                     [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
print("\n\nPeriod Comparisons:")
print('{:>10}{:>15}{:>15}{:>15}'.format('Period', 'OpenSees', 'SAP2000', 'SeismoStruct'))

# formatString {%10s%15.5f%15.4f%15.4f}
for i in range(0, numEigen):
    lamb = eigenValues[i]
    period = 2 * PI / sqrt(lamb)
    print('{:>10}{:>15.5f}{:>15.4f}{:>15.4f}'.format(i + 1, period, comparisonResults[0][i], comparisonResults[1][i]))
    resultOther = comparisonResults[0][i]
    if abs(period - resultOther) > 9.99e-5:
        ok - 1

# printModel()