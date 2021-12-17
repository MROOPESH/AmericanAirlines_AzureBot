#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "eb3d741f-cf2d-47a1-ba40-50e4888ba29d")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "Bbc7Q~DhshhnU7S_xeVQ~rYkKI5.2xtsJylnw")
