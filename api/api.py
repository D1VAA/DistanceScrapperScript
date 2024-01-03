from typing import Dict
from flask import Flask, Response, request, jsonify
from flask_restful import Api, Resource
from src.modules.scrapper import simple_distance_scrapper

app = Flask(__name__)
api = Api(app)


class DistanceScrapper(Resource):
    def get(self) -> Response:
        """Get the origin and destination from url and return the distance."""
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        origin = str(origin)
        destination = str(destination)

        result: Dict = {'result': simple_distance_scrapper(origin ,destination)}
        return jsonify(result)

api.add_resource(DistanceScrapper, '/route')

def run_server(port=3000):
    app.run(port=port, debug=True)
