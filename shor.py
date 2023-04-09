import math
import numpy as np

import cirq

##Still need to implement Unitary of fan(x) = a^x mod N
##Still need to implement adder operation for qubits and Unitary Function

#Function to apply QFT dagger to the number of qubits
def qft_dagger(qubits):
    #Initialization    
    circuit = cirq.Circuit()
    n = len(qubits)
    
    # Apply Hadamard gates to all qubits
    for i in range(n):
        circuit.append(cirq.H(qubits[i]))
    
    # Apply controlled-phase gates
    for i in range(n):
        for j in range(i):
            theta = -2*np.pi/(2**(i-j))
            circuit.append(cirq.CZ(qubits[i], qubits[j])**theta)
    
    # Reverse the order of the qubits
    for i in range(n//2):
        circuit.append(cirq.SWAP(qubits[i], qubits[n-i-1]))
    
    return circuit

#Simple Function for post processing of Shor's algorithm - This is just simple implementation
def period_post_processing(r, a, N):
    if r % 2 == 0:
        #Compute x = a^(r/2) mod N
        x = pow(a, r // 2, N)

        if (x + 1) != (0 % N):
            #Compute gcd(x + 1, N) and gcd (x - 1, N)
            gcd1 = math.gcd(x + 1, N)
            gcd2 = math.gcd(x - 1, N)
            #Return the gcd1 and gcd2
            return gcd1, gcd2
        else:
            print("This is not the right period. Please find another co-prime")

    else:
        print("The period is not even. Please find another co-prime")

########Main Function########
#N = 15 as we try to factor 15 (1111) first
N = 15
a = 13 #Trying to test with a = 13

#Reminder: The number of qubits should be more than 2N but for simplicity => 4 qubits  
qubits_x = cirq.LineQubit.range(4)          #Target qubits
qubits_w = cirq.LineQubit.range(4, 8)       #Source qubits

# Create a circuit
circuit = cirq.Circuit()

# Apply Hadamard gate to the target qubits using a for loop
for qubit in qubits_x:
    circuit.append(cirq.H(qubit))
# Add an Identity gate to keep track of the empty qubits
for qubit in qubits_w:
    circuit.append(cirq.Moment([cirq.I(qubit)]))

print(circuit)    

