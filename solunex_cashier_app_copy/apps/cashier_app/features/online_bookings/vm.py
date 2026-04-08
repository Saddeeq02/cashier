from .api import get_verified_bookings, convert_patient, get_booking_patients

class OnlineBookingsVM:

    def load(self):
        return get_verified_bookings()

    def convert(self, booking_id, patient_name):
        return convert_patient(booking_id, patient_name)
    

    def get_patients(self, booking_id):
        return get_booking_patients(booking_id)