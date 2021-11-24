from flask_script import Manager

from application import app
from command import auto_build

manager = Manager(app)

manager.add_command('auto_build', auto_build.manager)

if __name__ == '__main__':
    manager.run()
