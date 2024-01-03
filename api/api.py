from typing import Dict
from flask import Flask, request
from flask_restful import Api, Resource
from src.modules.scrapper import simple_distance_scrapper

app = Flask(__name__)
api = Api(app)


class DistanceScrapper(Resource):
    _data = {}
    def _add_data(self, origin, destination, distance): 
        string = f'{origin}x{destination}'.lower()
        self._data[string] = distance
    
    def get(self):
        """Get the origin and destination from url and return the distance."""
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        origin = str(origin)
        destination = str(destination)
        string = f'{origin}x{destination}'.lower()
        if string in self._data:
            return self._data[string]
        else:
            distance = simple_distance_scrapper(origin ,destination)
            distance_str = str(distance).replace('.',',')
            self._add_data(origin, destination, distance_str)
            return distance_str.lower()


api.add_resource(DistanceScrapper, '/route')

def run_server(port=3000):
    app.run(port=port)
