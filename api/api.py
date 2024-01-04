import asyncio
from typing import Optional, List, Dict
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

    def distance_str(self):
        return str(self.distance).replace('.',',')

class DistanceScrapper(Resource):
    _data: Dict[str|None, Query] = dict()
    _count_request: Dict[str, int] = dict()
    _tasks: Dict[str, asyncio.Task] = dict()

    @classmethod
    async def _add_in_queue(cls, query_inst) -> None:
        origin = query_inst.origin
        destination = query_inst.destination
        task = asyncio.create_task(simple_distance_scrapper(origin, destination))
        await task
        cls._data[query_inst.string].distance = task.result()

    @classmethod
    async def _run_tasks(cls) -> List:
        tasks_list: List[asyncio.Task] = list(cls._tasks.values())
        results = await asyncio.gather(*tasks_list)
        return results

    @classmethod
    async def _manage_requests(cls, query) -> None:
        await cls._add_in_queue(query)
        # results = await cls._run_tasks()

        # keys_to_remove = list(cls._tasks.keys())
        
        # for query_string, result in zip(cls._tasks.keys(), results):
        #     print("Resultado,", result)
        #     cls._data[query_string].distance = result
        
        # for query_string in keys_to_remove:
        #     del cls._tasks[query_string]
    
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
            # If this combination of origin and destiny was never done before, then the program register the query instance at the data dictionary.
            self._data[query.string] = query
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._manage_requests(query))
            finally:
                result = self._data[query.string].distance_str()
                loop.close()
            return result
        
api.add_resource(DistanceScrapper, '/route')

def run_api(port, debug=True):
    app.run(port=port, debug=debug)
