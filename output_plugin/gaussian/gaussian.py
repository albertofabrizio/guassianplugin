# -*- coding: utf-8 -*-
from aiida.orm.calculation.job.qchem import QchemCalculation
from aiida.orm.data.parameter import ParameterData
from aiida.parsers.plugins.qchem import QchemBaseParser


class BasicQchemParser(QchemBaseParser):
    """
    Parse the output of Qchem.
    """
    pass
#    def __init__(self,calc):
        # check for valid input
#       self._check_calc_compatibility(calc)
#       super(BasicQchemParser, self).__init__(calc)
#       self._get_output_nodes(output_path, error_path)

#   def _check_calc_compatibility(self,calc):
#       from aiida.common.exceptions import ParsingError
#       if not isinstance(calc, QchemCalculation):
#           raise ParsingError("Input calc must be a QchemCalculation")

#   def _get_output_nodes(self, output_path, error_path):
#       """
#       Extracts output nodes from the standard output and standard error
#       files.
#       """
#       from aiida.orm.data.array.trajectory import TrajectoryData
#       import re

#       state= 'qchem-scf-module'
#       step = None
#       scale = None
#       with open(output_path) as f:
#           lines = [x.strip('\n') for x in f.readlines()]

#       result_dict = dict()
#       trajectory = None
#       for line in lines:
#           if ('Total energy in the final basis set' in line):
#               result_dict['energy']=line.split()[8]
#               continue

#       return [('parameters', ParameterData(dict=result_dict))]
