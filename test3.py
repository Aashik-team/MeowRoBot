import re
content = open('MeowRobot/modules/welcome.py').read()
if 'from MeowRobot.modules.sql import users_sql as user_sql' not in content and 'import MeowRobot.modules.sql.users_sql as user_sql' not in content:
    print("Users sql not imported in welcome.py")
