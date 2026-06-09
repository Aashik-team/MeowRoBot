#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/MeowRobot/blob/master/LICENSE >
#
# All rights reserved.

FROM python:latest

RUN apt-get update -y && apt-get upgrade -y && apt-get install -y ffmpeg

RUN pip3 install -U pip setuptools
RUN pip3 install -U -r requirements.txt

CMD ["python3","-m","MeowRobot"]
