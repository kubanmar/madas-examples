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
    try:
        dos_paths = resolve_nested_dict(NOMAD_response, "archive/results/properties/electronic/dos_electronic/total")
    except TypeError:
        dos_paths = resolve_nested_dict(NOMAD_response, "archive/results/properties/electronic/dos_electronic/0/total")
    for path_ in dos_paths:
        path_ = path_[1:] if path_.startswith("#/") else path_
        norm_factor = resolve_nested_dict(NOMAD_response, f'archive{path_}/normalization_factor', fail_on_key_error=True)
        dos = np.array(resolve_nested_dict(NOMAD_response, f'archive{path_}/value', fail_on_key_error=True)) * norm_factor * electron_volt
        spin_channels.append(dos)
    return sum(spin_channels).tolist()
    
def get_dos_energies_vbm(NOMAD_response: dict) -> list:
    """
    Get DOS energies in eV from a NOMAD archive dictionary, normalized such that E=0 is at the VBM.
    """
    dos_results = resolve_nested_dict(NOMAD_response, "archive/results/properties/electronic/dos_electronic")
    if isinstance(dos_results, list):
        dos_results=dos_results[0]
    energies_path = resolve_nested_dict(dos_results, "energies")
    energies_path = energies_path[1:] if energies_path.startswith("#/") else energies_path
    efermi_0 = resolve_nested_dict(dos_results, "band_gap/0/energy_highest_occupied")
    try:
        efermi_1 = resolve_nested_dict(dos_results, "band_gap/1/energy_highest_occupied")
        efermi = max([efermi_0, efermi_1])
    except IndexError:
        efermi = efermi_0
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
    energy = resolve_nested_dict(NOMAD_response, "archive/run/0/calculation/0/energy/total/value") / electron_volt
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

def get_FHIaims_kpoints(NOMAD_response: dict) -> List[int]:
    return resolve_nested_dict(NOMAD_response, "archive/run/0/method/0/x_fhi_aims_controlInOut_k_grid")