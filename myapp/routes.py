from . import app, db
from flask import Flask, render_template, redirect, url_for, request,flash, get_flashed_messages, flash
from .models import *
from flask import jsonify
from datetime import datetime
from sqlalchemy.orm import load_only
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField
from wtforms.validators import  DataRequired, Email, ValidationError
import bcrypt
from flask_bcrypt import generate_password_hash, check_password_hash
from .forms import *





logging.basicConfig(level=logging.DEBUG)
@app.route('/')
@app.route('/main')
#@login_required
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form_type = request.form.get('form_type')
    if form_type == 'country':
        return search_flights_by_country()
    elif form_type == 'city':
        return search_flights_by_city()
    else:
        # Handle invalid form type
        return render_template('error.html', message='Invalid form type')

def search_flights_by_country():
    origin_country_name = request.form.get('origin')
    destination_country_name = request.form.get('destination')
    
    # Debugging: Print out the received country names
    print("Origin Country Name:", origin_country_name)
    print("Destination Country Name:", destination_country_name)
    
    origin_country = Country.query.filter(Country.CountryName.ilike(origin_country_name)).first()
    destination_country = Country.query.filter(Country.CountryName.ilike(destination_country_name)).first()
    
    # Debugging: Print out the retrieved country objects
    print("Origin Country:", origin_country)
    print("Destination Country:", destination_country)
    
    if origin_country and destination_country:
        # Debugging: Print a message to confirm that both countries are found
        print("Both origin and destination countries found in the database")
        
        # Retrieve cities within the origin and destination countries
        origin_cities = City.query.filter_by(CountryId=origin_country.CountryId).all()
        destination_cities = City.query.filter_by(CountryId=destination_country.CountryId).all()
        
        # Retrieve airport IDs for origin and destination cities
        origin_airport_ids = [airport.AirportId for city in origin_cities for airport in city.airport]
        destination_airport_ids = [airport.AirportId for city in destination_cities for airport in city.airport]

        # Query flights based on origin and destination airports
        flights = FlightAvailability.query.filter(
                FlightAvailability.Origin.in_(origin_airport_ids),
                FlightAvailability.Destination.in_(destination_airport_ids)
                ).all()

        return render_template('search_results.html', origin_country=origin_country, destination_country=destination_country, 
                               origin_cities=origin_cities, destination_cities=destination_cities, flights=flights)
    else:
        # Debugging: Print a message if either origin or destination country is not found
        if not origin_country:
            print("Origin country not found in the database")
        if not destination_country:
            print("Destination country not found in the database")
        
        # Handle error: countries not found
        return render_template('error.html', message='Origin or destination country not found')
    
def search_flights_by_city():
    origin_city_name = request.form.get('origin')
    destination_city_name = request.form.get('destination')
    
    # Debugging: Print out the received city names
    print("Origin City Name:", origin_city_name)
    print("Destination City Name:", destination_city_name)
    
    origin_city = City.query.filter(City.CityName.ilike(origin_city_name)).first()
    destination_city = City.query.filter(City.CityName.ilike(destination_city_name)).first()
    
    # Debugging: Print out the retrieved city objects
    print("Origin City:", origin_city)
    print("Destination City:", destination_city)
    
    if origin_city and destination_city:
        # Debugging: Print a message to confirm that both cities are found
        print("Both origin and destination cities found in the database")
        
        flights = FlightAvailability.query.filter_by(Origin=origin_city.CityId, Destination=destination_city.CityId).all()
        return render_template('search_results.html', origin_city=origin_city, destination_city=destination_city, flights=flights)
    else:
        # Debugging: Print a message if either origin or destination city is not found
        if not origin_city:
            print("Origin city not found in the database")
        if not destination_city:
            print("Destination city not found in the database")
        
        # Handle error: cities not found
        return render_template('error.html', message='Origin or destination city not found')
    

@app.route('/book/<int:flight_id>/<string:arrival>/<string:departure>/<int:origin>/<int:destination>')
@login_required
def book(flight_id, arrival, departure, origin, destination):
    # Convert arrival and departure strings to datetime objects
    arrival_datetime = datetime.strptime(arrival, '%Y-%m-%d %H:%M:%S')
    departure_datetime = datetime.strptime(departure, '%Y-%m-%d %H:%M:%S')

    # Query the FlightAvailability instance based on the provided keys
    flight_availability = FlightAvailability.query.get((flight_id, arrival_datetime, departure_datetime, origin, destination))
    if not flight_availability:
        return "Flight details not found", 404

    # Retrieve origin and destination airport taxes and currencies
    origin_airport_tax = flight_availability.origin_airport.AirportTax
    origin_currency = flight_availability.origin_airport.cities.currencies[0].LocalCurrency
    destination_airport_tax = flight_availability.destination_airport.AirportTax
    destination_currency = flight_availability.destination_airport.cities.currencies[0].LocalCurrency

    # Retrieve exchange rate from the database
    exchange_rate = Currency.query.filter_by(ForeignCurrency=destination_currency, LocalCurrency=origin_currency).first()
    if exchange_rate:
        converted_destination_tax = destination_airport_tax * exchange_rate.ExchangeRate
    else:
        return "Exchange rate not found", 404

    return render_template('book.html', flight_availability=flight_availability, 
                           origin_airport_tax=origin_airport_tax,
                           origin_currency=origin_currency,
                           converted_destination_tax=converted_destination_tax)

@app.route('/pay_partial', methods=['POST'])
@login_required
def pay_partial():
    try:
        logging.debug("Retrieving form data for partial payment...")
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        class_type = request.form['class_type'].lower()
        partial_amount = request.form.get('partial_amount', '0').replace(',', '')
        total_price = request.form.get('total_price', '0').replace(',', '')
        balance = request.form.get('balance', '0').replace(',', '')

        logging.debug(f"Received partial amount (string): {partial_amount}")
        logging.debug(f"Received total price (string): {total_price}")
        logging.debug(f"Received balance (string): {balance}")

        partial_amount = float(partial_amount) if partial_amount else 0
        total_price = float(total_price) if total_price else 0
        balance = float(balance) if balance else 0

        logging.debug(f"Converted partial amount: {partial_amount}")
        logging.debug(f"Converted total price: {total_price}")
        logging.debug(f"Converted balance: {balance}")

        flight_id = int(request.form['flight_id'])
        arrival = request.form['arrival']
        departure = request.form['departure']
        origin = int(request.form['origin'])
        destination = int(request.form['destination'])

        passenger_name = f"{first_name} {last_name}"
        arrival_datetime = datetime.strptime(arrival, '%Y-%m-%d %H:%M:%S')
        departure_datetime = datetime.strptime(departure, '%Y-%m-%d %H:%M:%S')

        # Check if the departure is within 30 days
        current_datetime = datetime.now()
        days_difference = (departure_datetime - current_datetime).days

        logging.debug(f"Current datetime: {current_datetime}")
        logging.debug(f"Departure datetime: {departure_datetime}")
        logging.debug(f"Days difference: {days_difference}")

        if days_difference <= 30:
            flash('Partial payment is only allowed for flights departing more than 30 days from now.', 'error')
            logging.error("Partial payment not allowed, departure date is within 30 days.")
            return render_template('book.html', error='Partial payment is only allowed for flights departing more than 30 days from now.')

        flight_availability = FlightAvailability.query.get((flight_id, arrival_datetime, departure_datetime, origin, destination))
        if not flight_availability:
            flash('Flight not found', 'error')
            logging.error("Flight not found with the provided details.")
            return render_template('book.html', error='Flight not found with the provided details.')

        logging.debug("Flight availability retrieved successfully.")

        class_type_obj = ClassType.query.filter_by(ClassTypeName=class_type.capitalize()).first()
        booked_status = Status.query.filter_by(Status='Booked').first()
        UserFirstName = User.query.filter_by(FirstName=current_user.FirstName).first()
        UserLastName = User.query.filter_by(LastName=current_user.LastName).first()

        user_name = f"{UserFirstName} {UserLastName}"

        if not class_type_obj or not booked_status:
            flash('Invalid class type or booking status', 'error')
            logging.error(f"Invalid class type '{class_type}' or booking status 'Booked'.")
            return render_template('book.html', error='Invalid class type or booking status.')

        logging.debug(f"Class type: {class_type_obj.ClassId}, Status: {booked_status.StatusId}")

        origin_city = flight_availability.origin_airport.cities
        if origin_city and origin_city.currencies:
            currency = origin_city.currencies[0]
            origin_currency = currency.LocalCurrency if currency else 'USD'
        else:
            origin_currency = 'USD'

        logging.debug(f"Currency used: {origin_currency}")

        new_booking = Booking(
            FlightId=flight_id,
            ClassId=class_type_obj.ClassId,
            StatusId=booked_status.StatusId,
            Origin=origin,
            Destination=destination,
            Arrival=arrival_datetime,
            Departure=departure_datetime,
            FlightPrice=flight_availability.FlightPrice,
            TotalPrice=total_price,
            PaidAmount=partial_amount,
            Balance=balance,
            BookingCity=flight_availability.origin_airport.CityId,
            UserId=current_user.UserId,
            passengerName=passenger_name
        )

        if class_type == 'business':
            if flight_availability.AvailSeatsBC > 0:
                flight_availability.AvailSeatsBC -= 1
                flight_availability.BookedSeatsBC += 1
            else:
                flash('No available seats in business class', 'error')
                return render_template('book.html', error='No available seats in business class.')
        elif class_type == 'economy':
            if flight_availability.AvailSeatsEC > 0:
                flight_availability.AvailSeatsEC -= 1
                flight_availability.BookedSeatsEC += 1
            else:
                flash('No available seats in economy class', 'error')
                return render_template('book.html', error='No available seats in economy class.')

        db.session.add(new_booking)
        db.session.commit()

        logging.debug("Partial payment booking saved successfully and seat counts updated.")

        flash('Partial payment booking successful!', 'success')

        return render_template('partial_payment.html', flight=flight_availability,
                               passenger_name=passenger_name, class_type=class_type.capitalize(),
                               origin_currency=origin_currency,
                               total_price=total_price,
                               partial_amount=partial_amount, balance=balance,
                               status=booked_status.Status, booking_id=new_booking.BookingId)
    except Exception as e:
        db.session.rollback()
        flash(str(e), 'error')
        logging.error(f"Exception occurred: {e}")
        return render_template('book.html', error=str(e))

@app.route('/pay_full', methods=['POST'])
@login_required
def pay_full():
    try:
        # Retrieve form data
        logging.debug("Retrieving form data...")
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        class_type = request.form['class_type'].lower()  # Ensure case-insensitive match
        total_price = float(request.form['total_price'])
        flight_id = int(request.form['flight_id'])
        arrival = request.form['arrival']
        departure = request.form['departure']
        origin = int(request.form['origin'])
        destination = int(request.form['destination'])

        logging.debug(f"Form data retrieved: {first_name} {last_name}, Class: {class_type}, Total Price: {total_price}")

        # Concatenate first_name and last_name to create passengerName
        passenger_name = f"{first_name} {last_name}"

        # Convert dates
        arrival_datetime = datetime.strptime(arrival, '%Y-%m-%d %H:%M:%S')
        departure_datetime = datetime.strptime(departure, '%Y-%m-%d %H:%M:%S')

        logging.debug(f"Parsed dates: Arrival - {arrival_datetime}, Departure - {departure_datetime}")

        # Retrieve the FlightAvailability record
        flight_availability = FlightAvailability.query.get((flight_id, arrival_datetime, departure_datetime, origin, destination))
        if not flight_availability:
            flash('Flight not found', 'error')
            logging.error("Flight not found with the provided details.")
            return render_template('book.html', error='Flight not found with the provided details.')

        logging.debug("Flight availability retrieved successfully.")

        # Log all available class types and statuses
        available_class_types = ClassType.query.all()
        available_statuses = Status.query.all()

        logging.debug(f"Available class types: {[ct.ClassTypeName.lower() for ct in available_class_types]}")
        logging.debug(f"Available statuses: {[status.Status for status in available_statuses]}")

        # Retrieve necessary references
        class_type_obj = ClassType.query.filter_by(ClassTypeName=class_type.capitalize()).first()
        booked_status = Status.query.filter_by(Status='Booked').first()
        UserFirstName = User.query.filter_by(FirstName=current_user.FirstName).first()
        UserLastName = User.query.filter_by(LastName=current_user.LastName).first()

        user_name = f"{UserFirstName} {UserLastName}"

        if not class_type_obj or not booked_status:
            flash('Invalid class type or booking status', 'error')
            logging.error(f"Invalid class type '{class_type}' or booking status 'Booked'.")
            return render_template('book.html', error='Invalid class type or booking status.')

        logging.debug(f"Class type: {class_type_obj.ClassId}, Status: {booked_status.StatusId}")

        # Retrieve currency information from the origin city
        origin_city = flight_availability.origin_airport.cities
        if origin_city and origin_city.currencies:
            origin_currency = origin_city.currencies[0].LocalCurrency
        else:
            origin_currency = 'USD'

        logging.debug(f"Currency used: {origin_currency}")

        # Create a new Booking record with the status set to 'Booked'
        new_booking = Booking(
            FlightId=flight_id,
            ClassId=class_type_obj.ClassId,
            StatusId=booked_status.StatusId,  # Set status directly to 'Booked'
            Origin=origin,
            Destination=destination,
            Arrival=arrival_datetime,
            Departure=departure_datetime,
            FlightPrice=flight_availability.FlightPrice, 
            TotalPrice=total_price,
            PaidAmount=total_price,
            Balance=0.0,
            BookingCity=flight_availability.origin_airport.CityId,  # Set BookingCity to the origin city
            UserId=current_user.UserId,  # Assign the current user's ID
            passengerName=passenger_name  # Set passengerName
        )

        # Adjust seats based on class type
        if class_type == 'business':
            if flight_availability.AvailSeatsBC > 0:
                flight_availability.AvailSeatsBC -= 1
                flight_availability.BookedSeatsBC += 1
            else:
                flash('No available seats in business class', 'error')
                return render_template('book.html', error='No available seats in business class.')
        elif class_type == 'economy':
            if flight_availability.AvailSeatsEC > 0:
                flight_availability.AvailSeatsEC -= 1
                flight_availability.BookedSeatsEC += 1
            else:
                flash('No available seats in economy class', 'error')
                return render_template('book.html', error='No available seats in economy class.')

        # Save the new booking and updated flight availability
        db.session.add(new_booking)
        db.session.commit()

        logging.debug("Booking saved successfully and seat counts updated.")

        flash('Booking successful!', 'success')

        # Render the flight details template with the booking details
        return render_template('flight_details.html', flight=flight_availability,
                               passenger_name=passenger_name, class_type=class_type.capitalize(), 
                               origin_currency=origin_currency,  # Pass the correct currency
                               total_price=total_price, status=booked_status.Status, booking_id=new_booking.BookingId)
    except Exception as e:
        db.session.rollback()  # Rollback the session in case of error
        flash(str(e), 'error')
        logging.error(f"Exception occurred: {e}")
        return render_template('book.html', error=str(e))




@app.route('/pay_balance', methods=['POST'])
@login_required
def pay_balance():
    try:
        # Retrieve form data
        logging.debug("Retrieving form data for paying balance...")
        booking_id = int(request.form['booking_id'])
        pay_amount = float(request.form.get('pay_amount', '0').replace(',', ''))
        total_price = float(request.form.get('total_price', '0').replace(',', ''))

        # Fetch the booking
        booking = Booking.query.get(booking_id)
        if not booking:
            flash('Booking not found', 'error')
            logging.error("Booking not found with the provided details.")
            return redirect(url_for('index'))

        logging.debug("Booking retrieved successfully.")

        # Update the balance
        new_balance = booking.Balance - pay_amount
        booking.PaidAmount += pay_amount
        booking.Balance = new_balance

        logging.debug(f"Updated balance: {new_balance}, Paid Amount: {booking.PaidAmount}")

        # Update status if balance is zero or less
        if new_balance <= 0:
            booked_status = Status.query.filter_by(Status='Booked').first()
            if booked_status:
                booking.StatusId = booked_status.StatusId
                logging.debug(f"Status updated to 'Booked'.")
            else:
                logging.error("Status 'Booked' not found.")
                flash('Error updating booking status.', 'error')
                return redirect(url_for('index'))

        db.session.commit()

        logging.debug("Payment processed successfully and booking updated.")

        flash('Balance payment successful!', 'success')
        return redirect(url_for('partial_payment', booking_id=booking_id))
    except Exception as e:
        db.session.rollback()
        flash(str(e), 'error')
        logging.error(f"Exception occurred: {e}")
        return redirect(url_for('index'))






@app.route('/partial_payment/<int:booking_id>', methods=['GET'])
@login_required
def partial_payment(booking_id):
    try:
        # Fetch the booking details
        booking = Booking.query.get(booking_id)
        if not booking:
            flash('Booking not found', 'error')
            logging.error("Booking not found with the provided details.")
            return redirect(url_for('index'))

        flight_availability = FlightAvailability.query.get((booking.FlightId, booking.Arrival, booking.Departure, booking.Origin, booking.Destination))
        if not flight_availability:
            flash('Flight availability not found', 'error')
            logging.error("Flight availability not found with the provided details.")
            return redirect(url_for('index'))

        logging.debug("Booking and flight availability retrieved successfully.")

        # Retrieve currency information from the associated city and currency
        origin_city = flight_availability.origin_airport.cities
        if origin_city and origin_city.currencies:
            currency = origin_city.currencies[0]  # Assuming the first currency is the correct one
            origin_currency = currency.LocalCurrency if currency else 'USD'
        else:
            origin_currency = 'USD'  # Default to USD if no currency is found

        logging.debug(f"Currency used: {origin_currency}")

        # Use the total price from the booking to ensure consistency
        total_price = booking.TotalPrice
        logging.debug(f"Total Price: {total_price}")

        return render_template('partial_payment.html', 
                               flight=flight_availability,
                               passenger_name=booking.passengerName,
                               class_type=ClassType.query.get(booking.ClassId).ClassTypeName,
                               origin_currency=origin_currency,
                               total_price=total_price,
                               partial_amount=booking.PaidAmount,
                               balance=booking.Balance,
                               status=Status.query.get(booking.StatusId).Status,
                               booking_id=booking.BookingId)
    except Exception as e:
        flash(str(e), 'error')
        logging.error(f"Exception occurred: {e}")
        return redirect(url_for('index'))






    
@app.route('/manage_booking')
@login_required
def manage_booking():
    try:
        # Retrieve all bookings from the database
        bookings = Booking.query.all()

        # Render the manage_booking template with booking data
        return render_template('manage_booking.html', bookings=bookings)
    except Exception as e:
        flash(f"Error retrieving bookings: {str(e)}", 'error')
        logging.error(f"Exception occurred while retrieving bookings: {e}")
        return redirect(url_for('index'))
    
@app.route('/view_flight_details/<int:booking_id>')
@login_required
def view_flight_details(booking_id):
    try:
        # Retrieve booking details from the database using booking_id
        booking = Booking.query.get(booking_id)

        if not booking:
            flash('Booking not found', 'error')
            logging.error(f"Booking not found with ID: {booking_id}")
            return redirect(url_for('manage_booking'))  # Redirect to manage_booking if booking not found

        # Pass necessary variables to the flight_details.html template
        return render_template('flight_details.html', 
                               flight=booking.flight_availability,
                               passenger_name=booking.passengerName,
                               class_type=booking.class_type.ClassTypeName,
                               status=booking.status.Status,
                               booking_id=booking.BookingId)  # Ensure booking_id is passed
    except Exception as e:
        flash(str(e), 'error')
        logging.error(f"Exception occurred: {e}")
        return redirect(url_for('manage_booking'))

    
@app.route('/cancel_flight/<int:booking_id>', methods=['POST'])
@login_required
def cancel_flight(booking_id):
    try:
        # Retrieve the booking record
        booking = Booking.query.get(booking_id)
        if not booking:
            flash('Booking not found', 'error')
            logging.error(f"Booking not found with ID: {booking_id}")
            return redirect(url_for('manage_booking'))

        # Check the class type and adjust seats accordingly
        flight_availability = booking.flight_availability
        if booking.class_type.ClassTypeName.lower() == 'business':
            flight_availability.AvailSeatsBC += 1
            flight_availability.BookedSeatsBC -= 1
        elif booking.class_type.ClassTypeName.lower() == 'economy':
            flight_availability.AvailSeatsEC += 1
            flight_availability.BookedSeatsEC -= 1

        # Change the status to "Canceled"
        canceled_status = Status.query.filter_by(Status='Canceled').first()
        if not canceled_status:
            flash('Cancellation status not found', 'error')
            logging.error("Cancellation status not found.")
            return redirect(url_for('manage_booking'))

        booking.StatusId = canceled_status.StatusId

        # Save the updated booking and flight availability
        db.session.commit()

        logging.debug("Booking canceled and seat counts updated.")

        flash('Flight canceled successfully!', 'success')
        return redirect(url_for('view_flight_details', booking_id=booking_id))
    except Exception as e:
        db.session.rollback()  # Rollback the session in case of error
        flash(str(e), 'error')
        logging.error(f"Exception occurred while canceling flight: {e}")
        return redirect(url_for('manage_booking'))
    
@app.route('/profile')
@login_required
def profile():
    user = User.query.get(current_user.UserId)
    if user:
        phone_numbers = PhoneNumber.query.filter_by(UserId=user.UserId).all()
        fax_numbers = FaxNumber.query.filter_by(UserId=user.UserId).all()
        mails = Mail.query.filter_by(UserId=user.UserId).all()
        return render_template('profile.html', user=user, phone_numbers=phone_numbers, fax_numbers=fax_numbers, mails=mails)
    else:
        flash('User not found', 'error')
        return redirect(url_for('index'))

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        # Retrieve form data
        street = request.form.get('street')
        city = request.form.get('city')
        province = request.form.get('province')
        postal_code = request.form.get('postal_code')
        country = request.form.get('country')
        phone_no = request.form.get('phone_no')
        pcountry_code = request.form.get('pcountry_code')
        fax_no = request.form.get('fax_no')
        fcountry_code = request.form.get('fcountry_code')
        farea_code = request.form.get('farea_code')

        # Update or create Mail record
        mail = Mail.query.filter_by(UserId=current_user.UserId).first()
        if not mail:
            mail = Mail(UserId=current_user.UserId)
            db.session.add(mail)
        mail.Street = street
        mail.City = city
        mail.Province = province
        mail.PostalCode = postal_code
        mail.Country = country

        # Update or create PhoneNumber record
        phone = PhoneNumber.query.filter_by(UserId=current_user.UserId).first()
        if not phone:
            phone = PhoneNumber(UserId=current_user.UserId)
            db.session.add(phone)
        phone.PhoneNo = phone_no
        phone.PCountryCode = pcountry_code

        # Update or create FaxNumber record
        fax = FaxNumber.query.filter_by(UserId=current_user.UserId).first()
        if not fax:
            fax = FaxNumber(UserId=current_user.UserId)
            db.session.add(fax)
        fax.FaxNo = fax_no
        fax.FCountryCode = fcountry_code
        fax.FAreaCode = farea_code

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))

    else:
        # Fetch existing data
        user = User.query.get(current_user.UserId)
        mail = Mail.query.filter_by(UserId=current_user.UserId).first()
        phone = PhoneNumber.query.filter_by(UserId=current_user.UserId).first()
        fax = FaxNumber.query.filter_by(UserId=current_user.UserId).first()

        return render_template('update_profile.html', user=user, mail=mail, phone=phone, fax=fax)


    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            FirstName=form.FirstName.data,
            LastName=form.LastName.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('signin'))
    return render_template('signup.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
    return render_template('signin.html', form=form)
    
@app.route('/signout', methods=['GET', 'POST'])
@login_required
def signout():
    logout_user()
    return redirect(url_for('signin'))






















    


