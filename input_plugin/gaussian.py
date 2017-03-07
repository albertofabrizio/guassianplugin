# -*- coding: utf-8 -*-
import os
import shutil

from aiida.orm.calculation.job import JobCalculation
from aiida.orm.data.parameter import ParameterData
from aiida.orm.data.structure import StructureData
from aiida.common.datastructures import CalcInfo, CodeInfo
from aiida.common.exceptions import InputValidationError
from aiida.common.utils import classproperty

class GaussianCalculation(JobCalculation):
    """
    Input plugin for Gaussian. This just creates a input from StructureData and
    parameters:
"""
    def _init_internal_params(self):
        super(GaussianCalculation, self)._init_internal_params()

        # Name of the default output parser
#        self._default_parser = 'gaussian.GaussianBaseParser'

        # Default input and output files
        self._DEFAULT_INPUT_FILE  = 'aiida.com'
        self._DEFAULT_OUTPUT_FILE = 'aiida.log'
        self._DEFAULT_ERROR_FILE  = 'aiida.err'

    @classproperty
    def _use_methods(cls):
        retdict = JobCalculation._use_methods
        retdict.update({
            "structure": {
               'valid_types': StructureData,
               'additional_parameter': None,
               'linkname': 'structure',
               'docstring': "A structure to be processed",
               },
            "parameters": {
               'valid_types': ParameterData,
               'additional_parameter': None,
               'linkname': 'parameters',
               'docstring': "Parameters used to describe the calculation",
               },
            })
        return retdict

    def _prepare_for_submission(self,tempfolder,inputdict):
        import numpy as np

        try:
            struct = inputdict.pop(self.get_linkname('structure'))
        except KeyError:
            raise InputValidationError("no structure is specified for this calculation")
        if not isinstance(struct, StructureData):
            raise InputValidationError("struct is not of type StructureData")

        try:
            code = inputdict.pop(self.get_linkname('code'))
        except KeyError:
            raise InputValidationError("no code is specified for this calculation")

        atoms = struct.get_ase()

     
        parameters = inputdict.pop(self.get_linkname('parameters'), None)
        if parameters is None:
            parameters = ParameterData(dict={})
        if not isinstance(parameters, ParameterData):
            raise InputValidationError("parameters is not of type ParameterData")
        par = parameters.get_dict()

        charge= par.pop('CHARGE', '0')
        cpus=par.pop ('CPUS','1')
        mult= par.pop(' MULTIPLICITY', '1')
        basis = par.pop('BASIS','6-31G')
        jobtype = par.pop('JOB_TYPE','SP')
        dft_d=par.pop('DFT_D','FALSE')
        total=par.pop('MEM_TOTAL', '7500')
        method=par.pop('METHOD', 'HF')
        convergence=par.pop('SCF_CONVERGENCE', 'Tight')
        title=par.pop('TITLE', 'A generic title')
        cycles=par.pop('SCF_MAX_CYCLES', '50')
        integral=par.pop('INTEGRAL','Integral(Grid=UltraFine)') # Note this default will generated a pruned a grid with 99,590 points
        unrestricted=par.pop('UNRESTRICTED', 'R')
        add_cell = par.pop('add_cell',False)


        input_filename = tempfolder.get_abs_path(self._DEFAULT_INPUT_FILE)
        with open(input_filename,'w') as f:
            f.write('%Mem={}mb\n'.format(total))
            f.write('#p {}{}/{} {} {}\n'.format(unrestricted,method,basis,jobtype,integral))
            if dft_d != 'FALSE':
                f.write('EmpiricalDispersion={}\n'.format(dft_d))
            f.write('\n')
            f.write('{}\n'.format(title))
            f.write('\n')
            f.write('{} {}\n'.format(charge,mult))
            for i,atom_type in enumerate(atoms.get_chemical_symbols()):
                f.write(' {} {} {} {}\n'.format(atom_type,
                                               atoms.get_positions()[i][0],
                                               atoms.get_positions()[i][1],
                                               atoms.get_positions()[i][2]))
            f.write('\n')
            f.flush()


        self._default_commandline_params = []

        commandline_params = self._default_commandline_params

        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.retrieve_list = [self._DEFAULT_OUTPUT_FILE,
                                  self._DEFAULT_ERROR_FILE]
        calcinfo.retrieve_singlefile_list = []

        codeinfo = CodeInfo()
        codeinfo.cmdline_params = commandline_params
        codeinfo.stdin_name = self._DEFAULT_INPUT_FILE
        codeinfo.stdout_name = self._DEFAULT_OUTPUT_FILE
        codeinfo.stderr_name = self._DEFAULT_ERROR_FILE
        codeinfo.code_uuid = code.uuid
        calcinfo.codes_info = [codeinfo]

        return calcinfo

    def convert_to_uppercase(item_in_dict):
        """
        This method recursively goes through a dictionary
        and converts all the keys to uppercase.
        On the fly, it also converts the values (if strings) to upppercase
        """
       
        try:
            for key in item_in_dict.keys():
                item_in_dict[key.upper()] = convert_to_uppercase(item_in_dict.pop(key))
        except AttributeError:
            try:
                return item_in_dict.upper()
            except AttributeError:
                return item_in_dict
        return item_in_dict

