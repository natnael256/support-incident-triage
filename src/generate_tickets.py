"""
This will be used to generate synthetic support tickets for Alpine Trail Co. 
"""

import json
import random
from datetime import datetime, timedelta

from faker import faker

fake = Faker()


SERVICE = ["checkout","inventory", "bike-builder", "tour-booking", "account", "shipping","mobile-app"]


