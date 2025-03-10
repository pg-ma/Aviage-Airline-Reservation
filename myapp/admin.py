from flask_admin.contrib.sqla import ModelView
from myapp.models import *
from flask_admin import Admin
from datetime import datetime
from flask import  redirect, request, flash, url_for
from werkzeug.exceptions import HTTPException

admin = Admin()
class CustomUserView(ModelView):
    
    column_list = ['FirstName', 'LastName', 'email', 'password' ]

#Custom views
class CustomPhoneNumberView(ModelView):
    column_list = ['PCountryCode', 'PhoneNo','user']

class CustomMailView(ModelView):
    column_list = ['MailId', 'Street', 'City', 'Province', 'PostalCode', 'Country', 'user']


class CustomFaxNumberView(ModelView):
    
    column_list = ['FCountryCode', 'FAreaCode', 'FaxNo',  'user']    

# class CustomCustomerView(ModelView):
#     form_columns = ['FirstName', 'LastName']
#     column_list = ['FirstName', 'LastName']

class CustomCountryView(ModelView):
    form_columns = ['CountryName']
    column_list = ['CountryId', 'CountryName']


class CustomAirlineView(ModelView):
    form_columns = ['AirlineId', 'AirlineName', 'country']
    column_list = ['AirlineId', 'AirlineName', 'country']

class CustomBookingView(ModelView):
    form_columns = ['passengerName', 'flight_availability', 'class_type', 'status', 'booking_city',
                    'FlightPrice', 'TotalPrice', 'PaidAmount', 'Balance']
    
    column_list = ['passengerName', 'flight_availability', 'class_type', 'status', 'booking_city',
                    'FlightPrice', 'TotalPrice', 'PaidAmount', 'Balance']
    

class CustomFlightAvailabilityView(ModelView):
    column_list = [
        'FlightId', 'Departure', 'Arrival', 'flight', 
        'origin_airport', 'destination_airport', 
        'FlightPrice', 'AvailSeatsBC', 'BookedSeatsBC', 
        'AvailSeatsEC', 'BookedSeatsEC'
    ]
    form_columns = [
        'Departure', 'Arrival', 'flight', 
        'origin_airport', 'destination_airport', 
        'FlightPrice', 'AvailSeatsBC', 'BookedSeatsBC', 
        'AvailSeatsEC', 'BookedSeatsEC'
    ]

    

    

    




class CustomFlightView(ModelView):
    form_columns = ['IsBusinessClassAvail', 'IsSmokingAllowed', 'airline']
    column_list = ['IsBusinessClassAvail', 'IsSmokingAllowed', 'airline']

class CustomCityView(ModelView):
    form_columns = ['CityName', 'country', 'currencies']
    column_list = ['CityId', 'CityName', 'country', 'currencies']

class CustomCurrencyView(ModelView):
    form_columns = [ 'ForeignCurrency', 'LocalCurrency', 'ExchangeRate']
    column_list = [ 'ForeignCurrency', 'LocalCurrency', 'ExchangeRate']




class CustomAirportView(ModelView):
    form_columns = ['AirportName', 'AirportTax', 'cities']
    column_list = ['AirportId', 'AirportName', 'AirportTax', 'cities']

class CustomClassTypeView(ModelView):
    form_columns = ['ClassTypeName']
    column_list = ['ClassId', 'ClassTypeName']

class CustomStatusView(ModelView):
    form_columns = ['Status']
    column_list = ['StatusId', 'Status']

    def on_model_change(self, form, model, is_created):
        if is_created:
            # Print information about the newly created instance
            print("New instance created:")
            print(model) 






admin.add_view(CustomPhoneNumberView(PhoneNumber, db.session))
admin.add_view(CustomMailView(Mail, db.session))
admin.add_view(CustomFaxNumberView(FaxNumber, db.session))
# admin.add_view(CustomCustomerView(Customer, db.session))
admin.add_view(CustomUserView(User, db.session))
admin.add_view(CustomCountryView(Country, db.session))
admin.add_view(CustomCityView(City, db.session))
admin.add_view(CustomAirportView(Airport, db.session))
admin.add_view(CustomAirlineView(Airline, db.session))
admin.add_view(CustomFlightView(Flight, db.session))
#admin.add_view(CustomFlightAvailabilityView(FlightAvailability, db.session))
admin.add_view(CustomFlightAvailabilityView(FlightAvailability, db.session, endpoint='flightavailability'))







admin.add_view(CustomCurrencyView(Currency, db.session))

admin.add_view(CustomClassTypeView(ClassType, db.session))
admin.add_view(CustomStatusView(Status, db.session))

admin.add_view(CustomBookingView(Booking, db.session))

