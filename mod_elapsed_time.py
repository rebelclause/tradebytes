import math

def elapsed_time(time_in_seconds=0, floor=True):
    if time_in_seconds != 0:
        weeks = math.fmod(time_in_seconds / (3600 * 24 * 7), 4)
        days = math.fmod(time_in_seconds / (3600 * 24), 7)
        hours = math.fmod(time_in_seconds / 3600, 24)
        minutes = math.fmod(time_in_seconds / 60, 60)
        seconds = math.fmod(time_in_seconds, 60)
        if floor:
            return {'input_in_seconds': time_in_seconds, 'weeks': math.floor(weeks), 'days': math.floor(days), 'hours': math.floor(hours), 'minutes':math.floor(minutes), 'seconds': math.floor(seconds)}
        return {'input_in_seconds': time_in_seconds, 'weeks': weeks, 'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds}
    return None


if __name__ == '__main__':
    # the function neither distracts on conditon of the input interval (it's always seconds), nor does it impose a safety limit such that the number of seconds you enter to convert is calculated and rejected if results would be more than 4 weeks, 7 days, 24 hours, 60 minutes and 60 seconds; the function is simple, designed mainly as a helper where upper limits of time are known, but conversion is useful; easy enough to add longer cycles or subtract them, or change the input params to include other unit standard, with the function internals providing unit conversion before mod slicing the entered value...
    print(elapsed_time(30))
    print(elapsed_time(60))
    print(elapsed_time(90))
    print(elapsed_time(3600))
    print(elapsed_time(3720))
    print(elapsed_time(36030))
    print(elapsed_time(363063))
    print(elapsed_time(3210123456, floor=False))
    print(elapsed_time(3210123456))
    print(elapsed_time(3236306201))