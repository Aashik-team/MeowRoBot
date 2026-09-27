import re

content = open('MeowRobot/modules/welcome.py').read()
if 'sql.update_user(new_mem.id' not in content:
    # Let's add it to handle_new_member
    pass
