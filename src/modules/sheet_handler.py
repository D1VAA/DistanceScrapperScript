from typing import Literal, List, Dict
import pandas as pd
from pandas import Series

class InvalidFileType(Exception):
    pass
class SheetHandler:
    def __init__(self, 
                 path: str, 
                 option: Literal[1, 2],
                 origin: str="Origem", 
                 destination: str="Destino"):
        self._combination: Dict[str, List] = {}
        self._opt = {1: self._permutation, 2: self._compare}
        self._path = path
        self._origin = origin
        self._destination = destination
        self._file_check()
        self._columns_reader()
        self._opt[option]() 
        
    def _permutation(self):
        """Method that create a dictionary with all the destinations to each origin. (No size limitation)."""
        for o in self.origin:
            self._combination[o] = []
            for d in self.destination:
                self._combination[o].append(d)
            
    def _compare(self):
        """Method to create the dictionary with origin and destination line by line from the dataframe."""
        if len(self.origin) == len(self.destination):
            for o, d in zip(self.origin, self.destination):
                if o in self._combination.keys() and d not in self._combination[o]:
                    self._combination[o].append(d)
                elif o not in self._combination.keys():
                    self._combination[o] = [d]
        else:
            raise TypeError("Option not allowed!\nDifferent number of origins and destinations.")

    def _file_check(self) -> None:
        """Method to open and read file."""
        if self._path.endswith('xlsx'):
            self.dataframe = pd.read_excel(self._path)
        elif self._path.endswith('.csv'):
            self.dataframe = pd.read_csv(self._path)
        else:
            raise InvalidFileType('The program does not recognize the file type: ', self._path.split('.')[-1])

    def _columns_reader(self) -> None:
        """Read the columns that contain the origin cities and destinations cities"""
        if hasattr(self, 'dataframe') and isinstance(self.dataframe, pd.DataFrame):
            self._origin_col = self.dataframe[self._origin]
            self._destination_col = self.dataframe[self._destination]
        else:
            print("Could not read the dataframe.")
    
    @property
    def cities_combination(self):
        """Return the dictionary with the origins and destinations."""
        return self._combination

    @property
    def origin(self) -> Series:
        """Return the Origin dataframe column"""
        if self._origin_col is not None:
            return self._origin_col
        else:
            raise TypeError('The program could not return the origin column.')
    
    @property
    def destination(self) -> Series:
        """Return the destination dataframe column"""
        if self._destination_col is not None:
            return self._destination_col
        else:
            raise TypeError('The program could not return the destination column.')
        