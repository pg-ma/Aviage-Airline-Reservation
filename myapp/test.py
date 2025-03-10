from . import app, db
from flask import Flask, render_template, redirect, url_for, request,flash, get_flashed_messages, flash
from .models import *
from flask import jsonify
from datetime import datetime

flight_availabilities = FlightAvailability.query.all()
for flight_availability in flight_availabilities:
    print(flight_availability)