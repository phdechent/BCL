from typing import List, Dict
import json

def read_json_to_dict(file_path: str) -> List[str]:

    with open(file_path, 'r') as f:
        json_content = json.load(f)
    
    instructions = json_content.get('instructions', [])
    output_list = []

    type_to_units = {
     "ElectricCurrent": "A",
     "Voltage": "V",
     "power": "W",
     "resistance": "Ohm",
     "TimeDimension": "hour",
     "time": "sec",
     "CRate": "C",
     "Volt": "V",
     "Ampere": "A",
     "Second": "sec",
     "Hour": "hour"
     }
    
    # Iterate through each instruction
    for instruction in instructions:
        sequence = instruction.get('sequence', [])
        sequence_output_list = []
        # Iterate through each step in the sequence
        for step in sequence:
            step_type = step.get('type', '')
            value = step.get('value', '')
            unit = step.get('unit', '')
            termination = step.get('termination', [{}])[0]
            termination_type = termination.get('type', '')
            termination_value = termination.get('value', '')
            termination_unit = termination.get('unit', '')

            # Check if value refers to a parameter
            if value in json_content['parameters']:
                value = json_content['parameters'][value]

            # Check if termination value refers to a parameter
            if termination_value in json_content['parameters']:
                termination_value = json_content['parameters'][termination_value]
            
            # Generate the instruction string
            if step_type == 'Rest':
                time = step.get('value', '')
                sequence_output_list.append(f"Rest for {time / 3600} {type_to_units.get('TimeDimension', 'hour')}")
            elif step_type == 'ElectricCurrent':
                if value > 0:
                    if termination_type == 'Voltage':
                        sequence_output_list.append(
                        f"Discharge at {value}{type_to_units.get(unit, unit)} "
                        f"until {termination_value}{type_to_units.get(termination_unit, termination_unit)}"
                        )
                    else:
                        sequence_output_list.append(
                        f"Discharge at {value}{type_to_units.get(unit, unit)} "
                        f"for {termination_value} {type_to_units.get(termination_unit, termination_unit)}"
                    )
                else:
                    if termination_type == 'Voltage':
                        sequence_output_list.append(
                        f"Charge at {-value}{type_to_units.get(unit, unit)} "
                        f"until {termination_value}{type_to_units.get(termination_unit, termination_unit)}"
                        )
                    else:
                        sequence_output_list.append(
                        f"Charge at {-value}{type_to_units.get(unit, unit)} "
                        f"for {termination_value} {type_to_units.get(termination_unit, termination_unit)}"
                        )
            elif step_type == 'Voltage':
                    if termination_type == 'ElectricCurrent':
                        sequence_output_list.append(
                        f"Hold at {value}{type_to_units.get(unit, unit)} "
                        f"until {termination_value}{type_to_units.get(termination_unit, termination_unit)}"
                        )
                    else:
                        sequence_output_list.append(
                        f"Hold at {value}{type_to_units.get(unit, unit)} "
                        f"for {termination_value}{type_to_units.get(termination_unit, termination_unit)}"
                        )
            else:
                sequence_output_list.append(
                    f"{type_to_units.get(step_type, step_type)} at {value}{type_to_units.get(unit, unit)} "
                    f"until {termination_value}{type_to_units.get(termination_unit, termination_unit)}"
                )
        if instruction.get('repeat', 1) > 1:
            for idx in range(instruction.get('repeat', 1)): # repetitions for sequences
                output_list.extend(sequence_output_list)
        else:
            output_list.append(tuple(sequence_output_list))
    return output_list