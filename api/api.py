from typing import Optional
import asyncio
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
    ip_addr: Optional[str] = None
    string: Optional[str] = None
    distance: Optional[float] = None
    def __post_init__(self):
        self.string= f'{self.origin}x{self.destination}'.lower()

    def distance_str(self):
        return str(self.distance).replace('.',',').lower()

class DistanceScrapper(Resource):
    _data = dict()
    _count_request = dict()
    _tasks = dict()
    @property
    def data(self):
        return self._data
    
    async def _add_in_queue(self, query_inst) -> None:
        origin = query_inst.origin
        destination = query_inst.destination
        task = asyncio.create_task(simple_distance_scrapper(origin, destination))
        self._tasks[query_inst] = task

    async def get(self):
        """Get the origin and destination from url and return the distance."""
        origin = str(request.args.get('origin'))
        destination = str(request.args.get('destination'))
        ip_addr = request.remote_addr
        query = Query(origin, destination, ip_addr)
        
        if query.string not in self._data.keys():
            self._data[query.string] = query
            if self._count_request.get(ip_addr,0) >= 2:
                await self._add_in_queue(query)
                results = await asyncio.gather(*self._tasks.values())
                for query, result in zip(self._tasks.keys(), results):
                    self._data[query].distance = result
                return query.distance_str()
        else:
            past_result = self._data[query.string].distance_str()
            print('\n\n\n\n\n\nRESULTADO: \n\n\n\n\n', past_result)
            return past_result


api.add_resource(DistanceScrapper, '/route')

async def run_api(port, debug=True):
    app.run(port=port, debug=debug)
