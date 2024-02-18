import datetime


def check_trip_type_via_start_date(trip_time):
    print('current Time is : ', datetime.date.today())
    print('trip start date is : ', trip_time)
    if trip_time < datetime.date.today() or trip_time == datetime.date.today():
        print('time is greater or equal')
        return False
    print('current time is greater')
    return True