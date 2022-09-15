import os
import requests
from urllib import parse

from flask import Flask, jsonify, request, Response, stream_with_context
from flask_restx import Api, Resource

from qwc_services_core.auth import auth_manager, optional_auth, get_auth_user
from qwc_services_core.permissions_reader import PermissionsReader
from qwc_services_core.runtime_config import RuntimeConfig
from qwc_services_core.tenant_handler import TenantHandler

# Flask application
app = Flask(__name__)
# Flask-RESTPlus Api
api = Api(app, version='1.0', title='External link proxy server API',
          description="""External link proxy server.""",
          default_label='External link proxy     server operations', doc='/api/'
          )

# disable verbose 404 error message
app.config['ERROR_404_HELP'] = False

auth = auth_manager(app, api)

# create tenant handler
tenant_handler = TenantHandler(app.logger)


@api.route('/<program>/', defaults={'path': ''})
@api.route('/<program>/<path:path>')
@api.response(404, 'Link not found or permission error')
class ExternalLinkProxy(Resource):

    @api.doc('get_link')
    @optional_auth
    def get(self, program, path):
        config_handler = RuntimeConfig("ext", app.logger)
        config = config_handler.tenant_config(tenant_handler.tenant())

        link = self.__get_link(config, get_auth_user(), program, path, request.args)
        req = requests.get(link, stream=True, timeout=config.get('get_link_timeout', 10))
        return self.__get_response(req)

    @api.doc('post_link')
    @optional_auth
    def post(self, program, path):
        config_handler = RuntimeConfig("ext", app.logger)
        config = config_handler.tenant_config(tenant_handler.tenant())

        link = self.__get_link(config, get_auth_user(), program, path, request.args)
        headers={'content-type': request.headers['content-type']}
        req = requests.post(link, stream=True, timeout=config.get('post_link_timeout', 30), data=request.form, headers=headers)
        return self.__get_response(req)

    def __get_link(self, config, identity, program, path, args):
        tenant = tenant_handler.tenant()
        permissions_handler = PermissionsReader(tenant, app.logger)
        permitted_resources = permissions_handler.resource_permissions(
            'external_links', identity, program
        )
        if not permitted_resources:
            app.logger.warning("Identity %s is not allowed to open link for program %s" % (identity, program))
            api.abort(404, 'Unable to open link')

        program_map = config.resources().get("external_links", [])
        link = None
        for entry in program_map:
            if entry["name"] == program:
                link = entry["url"]
                break
        if not link:
            app.logger.warning("No link configured for program %s" % (program))
            api.abort(404, 'Unable to open link')
        parts = parse.urlsplit(link)
        query = dict(parse.parse_qsl(parts.query))
        for key in query:
            query[key] = query[key].replace('$tenant$', tenant)
            query[key] = query[key].replace('$username$', identity)
        query.update(args)
        parts = parts._replace(query=parse.urlencode(query))

        if path:
            parts = parts._replace(path=os.path.dirname(parts.path) + "/" + path)

        link = parts.geturl()
        api.logger.info("Proxying " + link)
        return link

    def __get_response(self, req):
        response = Response(stream_with_context(req.iter_content(chunk_size=1024)), status=req.status_code)
        # Inherit content-type and content-disposition from response of proxied request
        for name in ['content-type', 'content-disposition']:
            if name in req.headers:
                response.headers[name] = req.headers[name]
        return response


""" readyness probe endpoint """
@app.route("/ready", methods=['GET'])
def ready():
    return jsonify({"status": "OK"})


""" liveness probe endpoint """
@app.route("/healthz", methods=['GET'])
def healthz():
    return jsonify({"status": "OK"})


# local webserver
if __name__ == '__main__':
    print("Starting external link service...")
    app.run(host='localhost', port=5023, debug=True)
