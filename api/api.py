import asyncio
from typing import Optional, Dict
from flask import Flask, request
from flask_restful import Api, Resource
from dataclasses import dataclass
from src.modules.scrapper import simple_distance_scrapper

app = Flask(__name__)
api = Api(app)


@dataclass
class Query:
    origin: str
    destination: str
    string: Optional[str] = None
    distance: Optional[float] = None

    def __post_init__(self):
        self.string= f'{self.origin} x {self.destination}'.lower()

    def distance_str(self) -> str:
        return str(self.distance).replace('.',',')


class DistanceScrapper(Resource):
    _data: Dict[str|None, Query] = dict() 
    _count_request: Dict[str, int] = dict()
    _tasks: Dict[str, asyncio.Task] = dict()

    @classmethod
    async def _add_in_queue(cls, query_inst: Query) -> None:
        """Method that add a new task in the task dictionary."""
        origin = query_inst.origin
        destination = query_inst.destination
        task = asyncio.create_task(simple_distance_scrapper(origin, destination))
        await asyncio.gather(task)
        cls._data[query_inst.string].distance = task.result()  # type: ignore

    def get(self):
        """Get the origin and destination from url and return the distance."""
        origin = str(request.args.get('origin'))
        destination = str(request.args.get('destination'))
        query = Query(origin, destination)
        
        # If the query was already done at some point, then it must be saved at the data dictionary.
        if query.string in self._data.keys():
            # If the combination of origin and destiny is already present at the data dictionary, just get the distance from the dictionary and return.
            past_result: str = self._data[query.string].distance_str()
            return past_result
        else:
            # If this combination of origin and destiny was never done before, the program will register the query instance at the data dictionary, start a event loop and start the query on google.
            self._data[query.string] = query
            try:
                asyncio.run(self._add_in_queue(query))
            finally:
                result = self._data[query.string].distance_str()
                return result
        
api.add_resource(DistanceScrapper, '/route')

def run_api(port, debug=False):
    app.run(port=port, debug=debug)
