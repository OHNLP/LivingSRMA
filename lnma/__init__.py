import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_compress import Compress

db = SQLAlchemy()

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    # Compress the request to reduce file size
    Compress(app)

    # print(app.config)
    # bind db
    db.init_app(app)
    migrate = Migrate(app, db)

    # use [[ ]] instead of {{ }} for jinja2
    app.jinja_env.variable_start_string = '[['
    app.jinja_env.variable_end_string = ']]'

    # put all settings for jinja2 and other access
    from lnma import settings
    app.config['settings'] = settings

    if test_config is not None:
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # load blueprints
    from lnma import bp_index
    from lnma import bp_auth
    from lnma import bp_sysmgr
    from lnma import bp_portal
    from lnma import bp_project
    from lnma import bp_collector
    from lnma import bp_screener
    from lnma import bp_importer
    from lnma import bp_analyzer
    from lnma import bp_pub
    from lnma import bp_rplt
    from lnma import bp_study
    from lnma import bp_extractor
    from lnma import bp_exporter
    from lnma import bp_pdfworker
    from lnma import bp_webfonts

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # bind user
    @login_manager.user_loader
    def load_user(user_id):
        return bp_auth.user_loader(user_id)

    @login_manager.request_loader
    def request_loader(request):
        return bp_auth.request_loader(request)

    # apply the blueprints to the app
    app.register_blueprint(bp_index.bp)
    app.register_blueprint(bp_auth.bp)
    app.register_blueprint(bp_sysmgr.bp)
    app.register_blueprint(bp_portal.bp)
    app.register_blueprint(bp_project.bp)
    app.register_blueprint(bp_collector.bp)
    app.register_blueprint(bp_screener.bp)
    app.register_blueprint(bp_importer.bp)
    app.register_blueprint(bp_analyzer.bp)
    app.register_blueprint(bp_pub.bp)
    app.register_blueprint(bp_rplt.bp)
    app.register_blueprint(bp_study.bp)
    app.register_blueprint(bp_extractor.bp)
    app.register_blueprint(bp_exporter.bp)
    app.register_blueprint(bp_pdfworker.bp)
    app.register_blueprint(bp_webfonts.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    # app.add_url_rule("/", endpoint="index")

    return app
