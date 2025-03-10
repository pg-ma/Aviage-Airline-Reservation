from myapp import db
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user



class PhoneNumber(db.Model):
    __tablename__ = 'PhoneNumber'
    PhoneNo = db.Column(db.String(50), primary_key=True)
    PCountryCode = db.Column(db.String(50), primary_key=True)
    
    UserId = db.Column(db.Integer, db.ForeignKey('User.UserId'))

    
    # Define the back reference to the Customer model
    user = db.relationship("User", back_populates="phone")


class Mail(db.Model):
    __tablename__ = 'Mail'
    MailId = db.Column(db.Integer, primary_key=True)
    Street = db.Column(db.String(100))
    City = db.Column(db.String(100))
    Province  = db.Column(db.String(100))
    PostalCode  = db.Column(db.String(100))
    Country  = db.Column(db.String(100))
    UserId = db.Column(db.Integer, db.ForeignKey('User.UserId'))

    user = db.relationship("User", back_populates="mail")
    
   

class FaxNumber(db.Model):
    __tablename__ = 'FaxNumber'
    FaxNo = db.Column(db.String(100), primary_key=True)
    FCountryCode = db.Column(db.String(50), primary_key=True)
    FAreaCode = db.Column(db.String(50), primary_key=True)

    UserId = db.Column(db.Integer, db.ForeignKey('User.UserId'))

    user = db.relationship("User", back_populates="fax")
   

# class Customer(db.Model):
#     __tablename__ = 'Customer'
#     CustomerId = db.Column(db.Integer, primary_key=True)
#     FirstName = db.Column(db.String(50), nullable=False)
#     LastName = db.Column(db.String(50), nullable=False)

#     # Define the relationships
#     phone = db.relationship("PhoneNumber", back_populates="customer")
#     fax = db.relationship("FaxNumber", back_populates="customer")
#     email = db.relationship("Email", back_populates="customer")

#     def __str__(self):
#         return f"{self.FirstName} {self.LastName}"

class User(db.Model, UserMixin):
    __tablename__ = 'User'
    UserId = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False )   


    phone = db.relationship("PhoneNumber", back_populates="user")
    fax = db.relationship("FaxNumber", back_populates="user")
    mail = db.relationship("Mail", back_populates="user") 

    #Define the relationships

    def __repr__(self):
        return f"User('{self.email}', '{self.FirstName}', '{self.LastName}')"

    def get_id(self):
        return str(self.UserId)


  

    

   
class Booking(db.Model):
    __tablename__ = 'Booking'
    BookingId = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, db.ForeignKey('User.UserId'))
    FlightId = db.Column(db.Integer, db.ForeignKey('FlightAvailability.FlightId'))
    ClassId = db.Column(db.Integer, db.ForeignKey('ClassType.ClassId'))
    StatusId = db.Column(db.Integer, db.ForeignKey('Status.StatusId'))
    Origin = db.Column(db.Integer, db.ForeignKey('FlightAvailability.Origin'))
    Destination = db.Column(db.Integer, db.ForeignKey('FlightAvailability.Destination'))
    Arrival = db.Column(db.DateTime, db.ForeignKey('FlightAvailability.Arrival'))
    Departure = db.Column(db.DateTime, db.ForeignKey('FlightAvailability.Departure'))
    BookingCity = db.Column(db.Integer, db.ForeignKey('City.CityId'))


    passengerName = db.Column(db.String(50), nullable=False)
    FlightPrice = db.Column(db.Float)
    TotalPrice = db.Column(db.Float)
    PaidAmount = db.Column(db.Float)
    Balance = db.Column(db.Float)

    user = db.relationship("User", backref="bookings")

    flight_availability = db.relationship("FlightAvailability", primaryjoin="and_(Booking.FlightId == FlightAvailability.FlightId, "
                                                                                 "Booking.Origin == FlightAvailability.Origin, "
                                                                                 "Booking.Destination == FlightAvailability.Destination, "
                                                                                 "Booking.Arrival == FlightAvailability.Arrival, "
                                                                                 "Booking.Departure == FlightAvailability.Departure)", backref="bookings")

    class_type = db.relationship("ClassType", backref="bookings")
    status = db.relationship("Status", backref="bookings")
    booking_city = db.relationship("City", backref="bookings")

    def save(self):
        db.session.add(self)
        db.session.commit()

    

class Country(db.Model):
    __tablename__ = 'Country'
    CountryId = db.Column(db.Integer, primary_key=True)
    CountryName = db.Column(db.String(50), nullable=False)

    airlines = db.relationship("Airline", back_populates="country")
    cities = db.relationship("City", back_populates="country")

    def __str__(self):
        return self.CountryName


class Airline(db.Model):
    __tablename__ = 'Airline'
    AirlineId = db.Column(db.Integer, primary_key=True)
    AirlineName = db.Column(db.String(50), nullable=False)
    CountryId = db.Column(db.Integer, db.ForeignKey('Country.CountryId'), nullable=False)
    
    country = db.relationship("Country", back_populates="airlines")
    flights = db.relationship("Flight", back_populates="airline")

    def __str__(self):
        return self.AirlineName

class FlightAvailability(db.Model):
    __tablename__ = 'FlightAvailability'
    FlightId = db.Column(db.Integer, db.ForeignKey('Flight.FlightId'), primary_key=True)
    Arrival = db.Column(db.DateTime, primary_key=True)
    Departure = db.Column(db.DateTime, primary_key=True)
    Origin = db.Column(db.Integer, db.ForeignKey('Airport.AirportId'), primary_key=True)
    Destination = db.Column(db.Integer, db.ForeignKey('Airport.AirportId'), primary_key=True)
    FlightPrice = db.Column(db.Float, nullable=False)
    AvailSeatsBC = db.Column(db.Integer)
    BookedSeatsBC = db.Column(db.Integer)
    AvailSeatsEC = db.Column(db.Integer)
    BookedSeatsEC = db.Column(db.Integer)

    # Define relationships
    flight = db.relationship("Flight", back_populates="availabilities")
    origin_airport = db.relationship("Airport", foreign_keys=[Origin], backref="departures")
    destination_airport = db.relationship("Airport", foreign_keys=[Destination], backref="arrivals")

    def __str__(self):
        arrival_str = self.Arrival.strftime("%Y-%m-%d %H:%M:%S")
        departure_str = self.Departure.strftime("%Y-%m-%d %H:%M:%S")
        origin_airport_name = self.origin_airport.AirportName
        destination_airport_name = self.destination_airport.AirportName
        return f"Flight ID: {self.FlightId}, Arrival: {arrival_str}, Departure: {departure_str}, Origin: {origin_airport_name}, Destination: {destination_airport_name}"



        

        
    
    
    

class Flight(db.Model):
    __tablename__ = 'Flight'
    FlightId = db.Column(db.Integer, primary_key=True)
    AirlineId = db.Column(db.Integer, db.ForeignKey('Airline.AirlineId'))
    IsBusinessClassAvail = db.Column(db.Boolean, nullable=False)
    IsSmokingAllowed = db.Column(db.Boolean, nullable=False)
    
    airline = db.relationship("Airline", back_populates="flights")
    availabilities = db.relationship("FlightAvailability", back_populates="flight")

    def __str__(self):
        return f"Flight Number: {self.FlightId} {self.airline}"

city_currency_association = db.Table(
    'city_currency',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('foreign_currency', db.String(3), db.ForeignKey('Currency.ForeignCurrency'), nullable=True),
    db.Column('local_currency', db.String(3), db.ForeignKey('Currency.LocalCurrency'), nullable=True),
    db.Column('city_id', db.Integer, db.ForeignKey('City.CityId'), nullable=True)
)
class Currency(db.Model):
    __tablename__ = 'Currency'
    ForeignCurrency = db.Column(db.String(3), primary_key=True)
    LocalCurrency = db.Column(db.String(3), primary_key=True)
    ExchangeRate = db.Column(db.Float, nullable=False)

class City(db.Model):
    __tablename__ = 'City'
    CityId = db.Column(db.Integer, primary_key=True)
    CityName = db.Column(db.String(50), nullable=False)
    CountryId = db.Column(db.Integer, db.ForeignKey('Country.CountryId'), nullable=False)

    currencies = db.relationship('Currency',
                                  secondary=city_currency_association,
                                  primaryjoin=(city_currency_association.c.city_id == CityId),
                                  secondaryjoin=(city_currency_association.c.foreign_currency == Currency.ForeignCurrency) & 
                                                (city_currency_association.c.local_currency == Currency.LocalCurrency),
                                  backref='cities')
    
    country = db.relationship("Country", back_populates="cities")
    airport = db.relationship("Airport", back_populates="cities")
    


    def __str__(self):
        return self.CityName








class Airport(db.Model):
    __tablename__ = 'Airport'
    AirportId = db.Column(db.Integer, primary_key=True)
    AirportName = db.Column(db.String(50), nullable=False)
    AirportTax = db.Column(db.Float, nullable=False)
    CityId = db.Column(db.Integer, db.ForeignKey('City.CityId'), nullable=True)

    cities = db.relationship("City", back_populates="airport")

    def __str__(self):
        return self.AirportName

class ClassType(db.Model):
    __tablename__ = 'ClassType'
    ClassId = db.Column(db.Integer, primary_key=True)
    ClassTypeName = db.Column(db.String(20), nullable=False)

    def __str__(self):
        return self.ClassTypeName

   

class Status(db.Model):
    __tablename__ = 'Status'
    StatusId = db.Column(db.Integer, primary_key=True)
    Status = db.Column(db.String(20), nullable=False)

    def __str__(self):
        return self.Status
   


