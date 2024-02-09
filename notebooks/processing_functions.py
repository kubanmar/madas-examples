from madas.utils import resolve_nested_dict
from madas.apis.api_core import api_call
from scipy.constants import electron_volt
import numpy as np
import re
import requests
from typing import List


def get_dos_values(NOMAD_response: dict) -> list:
    """
    Get total DOS per unit cell and eV from NOMAD archive dictionary.
    """
    spin_channels = []
    dos_paths = resolve_nested_dict(NOMAD_response, "archive/results/properties/electronic/dos_electronic/total")
    for path_ in dos_paths:
        norm_factor = resolve_nested_dict(NOMAD_response, f'archive{path_}/normalization_factor')
        dos = np.array(resolve_nested_dict(NOMAD_response, f'archive{path_}/value')) * norm_factor * electron_volt
        spin_channels.append(dos)
    return sum(spin_channels).tolist()
    
def get_dos_energies(NOMAD_response: dict) -> list:
    """
    Get DOS energies in eV from aNOMAD archive dictionary.
    """
    energies_path = resolve_nested_dict(NOMAD_response, "archive/results/properties/electronic/dos_electronic/energies")
    efermi = resolve_nested_dict(NOMAD_response, "archive/results/properties/electronic/dos_electronic/energy_fermi")
    dos_energies = (np.array(resolve_nested_dict(NOMAD_response, f"archive{energies_path}")) - efermi) / electron_volt
    return dos_energies.tolist()

def get_band_gap(NOMAD_response: dict) -> float:
    """
    Get minimal electronic band gap in eV from a NOMAD archive dictionary.
    """
    band_gap_data=resolve_nested_dict(NOMAD_response, "/archive/results/properties/electronic/dos_electronic/band_gap")
    def gap_from_channel(channel: dict) -> float:
        return (channel['energy_lowest_unoccupied'] - channel['energy_highest_occupied'])/electron_volt
    return min(map(gap_from_channel, band_gap_data))

def get_total_energy_eV(NOMAD_response: dict) -> float:
    """
    Get total energy of the converged calculation from NOMAD archive dictionary.
    """
    energy_path = resolve_nested_dict(NOMAD_response, "archive/workflow/0/calculation_result_ref")
    energy = resolve_nested_dict(NOMAD_response, f"archive{energy_path}/energy/total/value") / electron_volt
    return energy

def get_FHIaims_n_basis_functions(NOMAD_response: dict) -> int:
    """
    Get number of basis functions used in a FHI aims calculation.
    """
    atom_parameters = resolve_nested_dict(NOMAD_response, "archive/run/0/method/0/atom_parameters")
    n_basis_functions = 0
    for params in atom_parameters:
        n_basis_functions+=len(resolve_nested_dict(params, "x_fhi_aims_section_controlInOut_atom_species/0/x_fhi_aims_section_controlInOut_basis_func"))
    return n_basis_functions

@api_call
def get_FHIaims_kpoints(NOMAD_response: dict) -> List[int]:
    # kpoints are not parsed in the current version of the MetaInfo
    # therefore we extract them from the control.in file 
    mid = resolve_nested_dict(NOMAD_response, "archive/metadata/calc_id")
    control_in_file = requests.get(f"https://nomad-lab.eu/prod/v1/api/v1/entries/{mid}/raw/control.in").text
    kpoints = list(map(int, re.search("\s*k[_]grid\s*(\d+\s\d+\s\d+)\s*\n", control_in_file).group().strip().split()[-3:]))
    return kpoints