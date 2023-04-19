import math
import numpy as np

import cirq
from typing import Callable, Iterable, List, Optional, Sequence, Union

##Still need to implement Unitary of fan(x) = a^x mod N
##Still need to implement adder operation for qubits and Unitary Function

# adder implementation from Google
class Adder(cirq.ArithmeticGate):
    """Quantum addition."""
    def __init__(
        self,
        target_register: [int, Sequence[int]],
        input_register: Union[int, Sequence[int]],
    ):
        self.target_register = target_register
        self.input_register = input_register

    def registers(self) -> Sequence[Union[int, Sequence[int]]]:
        return self.target_register, self.input_register

    def with_registers(
        self, *new_registers: Union[int, Sequence[int]]
    ) -> 'Adder':
        return Adder(*new_registers)

    def apply(self, *register_values: int) -> Union[int, Iterable[int]]:
        return sum(register_values)
    def _circuit_diagram_info_(self, args: cirq.CircuitDiagramInfoArgs):
        wire_symbols = [' + ' for _ in range(len(self.input_register)+len(self.target_register))]
        return cirq.CircuitDiagramInfo(wire_symbols=tuple(wire_symbols))

# modular exponentiation circuit from Google
class ModularExp(cirq.ArithmeticGate):
    """Quantum modular exponentiation.

    This class represents the unitary which multiplies base raised to exponent
    into the target modulo the given modulus. More precisely, it represents the
    unitary V which computes modular exponentiation x**e mod n:

        V|y⟩|e⟩ = |y * x**e mod n⟩ |e⟩     0 <= y < n
        V|y⟩|e⟩ = |y⟩ |e⟩                  n <= y

    where y is the target register, e is the exponent register, x is the base
    and n is the modulus. Consequently,

        V|y⟩|e⟩ = (U**e|y)|e⟩

    where U is the unitary defined as

        U|y⟩ = |y * x mod n⟩      0 <= y < n
        U|y⟩ = |y⟩                n <= y
    """
    def __init__(
        self,
        target: Sequence[int],
        exponent: Union[int, Sequence[int]],
        base: int,
        modulus: int
    ) -> None:
        if len(target) < modulus.bit_length():
            raise ValueError(
                f'Register with {len(target)} qubits is too small for modulus'
                f' {modulus}'
            )
        self.target = target
        self.exponent = exponent
        self.base = base
        self.modulus = modulus

    def registers(self) -> Sequence[Union[int, Sequence[int]]]:
        return self.target, self.exponent, self.base, self.modulus

    def with_registers(
        self, *new_registers: Union[int, Sequence[int]]
    ) -> 'ModularExp':
        """Returns a new ModularExp object with new registers."""
        if len(new_registers) != 4:
            raise ValueError(
                f'Expected 4 registers (target, exponent, base, '
                f'modulus), but got {len(new_registers)}'
            )
        target, exponent, base, modulus = new_registers
        if not isinstance(target, Sequence):
            raise ValueError(
                f'Target must be a qubit register, got {type(target)}'
            )
        if not isinstance(base, int):
            raise ValueError(
                f'Base must be a classical constant, got {type(base)}'
            )
        if not isinstance(modulus, int):
            raise ValueError(
              f'Modulus must be a classical constant, got {type(modulus)}'
            )
        return ModularExp(target, exponent, base, modulus)

    def apply(self, *register_values: int) -> int:
        """Applies modular exponentiation to the registers.

        Four values should be passed in.  They are, in order:
          - the target
          - the exponent
          - the base
          - the modulus

        Note that the target and exponent should be qubit
        registers, while the base and modulus should be
        constant parameters that control the resulting unitary.
        """
        assert len(register_values) == 4
        target, exponent, base, modulus = register_values
        if target >= modulus:
            return target
        return (target * base**exponent) % modulus

    def _circuit_diagram_info_(
      self, args: cirq.CircuitDiagramInfoArgs
    ) -> cirq.CircuitDiagramInfo:
        """Returns a 'CircuitDiagramInfo' object for printing circuits.

        This function just returns information on how to print this operation
        out in a circuit diagram so that the registers are labeled
        appropriately as exponent ('e') and target ('t').
        """
        assert args.known_qubits is not None
        wire_symbols = [f't{i}' for i in range(len(self.target))]
        e_str = str(self.exponent)
        if isinstance(self.exponent, Sequence):
            e_str = 'e'
            wire_symbols += [f'e{i}' for i in range(len(self.exponent))]
        wire_symbols[0] = f'ModularExp(t*{self.base}**{e_str} % {self.modulus})'
        return cirq.CircuitDiagramInfo(wire_symbols=tuple(wire_symbols))



# Unitary operation. Computes a^x mod 15
def unitary_modulo_15(a, power):
    if a not in [2, 4, 7, 8, 11, 13]:
        raise ValueError("'a' must be 2, 4, 7, 8, 11, 13")
    U = cirq.Circuit()

    

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
#N = 15
#a = 13 #Trying to test with a = 13

#Reminder: The number of qubits should be more than 2N but for simplicity => 4 qubits  
#qubits_x = cirq.LineQubit.range(4)          #Target qubits
#qubits_w = cirq.LineQubit.range(4, 8)       #Source qubits

# Create a circuit
#circuit = cirq.Circuit()

# Apply Hadamard gate to the target qubits using a for loop
    #for qubit in qubits_x:
#circuit.append(cirq.H(qubit))
# Add an Identity gate to keep track of the empty qubits
    #for qubit in qubits_w:
#circuit.append(cirq.Moment([cirq.I(qubit)]))

#print(circuit)    

def make_order_finding_circuit(x: int, n: int) -> cirq.Circuit:
    """Returns quantum circuit which computes the order of x modulo n.

    The circuit uses Quantum Phase Estimation to compute an eigenvalue of
    the following unitary:

        U|y⟩ = |y * x mod n⟩      0 <= y < n
        U|y⟩ = |y⟩                n <= y

    Args:
        x: positive integer whose order modulo n is to be found
        n: modulus relative to which the order of x is to be found

    Returns:
        Quantum circuit for finding the order of x modulo n
    """
    L = n.bit_length()
    target = cirq.LineQubit.range(L)
    exponent = cirq.LineQubit.range(L, 3 * L + 3)

    # Create a ModularExp gate sized for these registers.
    mod_exp = ModularExp([2] * L, [2] * (2 * L + 3), x, n)

    return cirq.Circuit(
        cirq.X(target[L - 1]),
        cirq.H.on_each(*exponent),
        mod_exp.on(*target, *exponent),
        cirq.qft(*exponent, inverse=True),
        cirq.measure(*exponent, key='exponent'),
    )

n = 15
x = 7
circuit = make_order_finding_circuit(x, n)
print(circuit)

