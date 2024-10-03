import serial

class GPSHandler:
    def __init__(self, port='/dev/ttyUSB1', baudrate=115200):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        self.count_online = 0

    def is_online(self):
        return True if self.count_online > 5 else False


    def get_location(self):
        self.serial.write(b'AT+CGPSINFO\r')
        response = self.serial.read(1000).decode('utf-8')
        lines = response.split('\r\n')
        try:
            for line in lines:
                if line.startswith('$GPRMC'):
                    self.count_online += 1
                    lat, lng = self.parse_gprmc(line)
                    if lat and lng:
                        return lat, lng
                elif line.startswith('$GPGGA'):
                    self.count_online += 1
                    lat, lng = self.parse_gpgga(line)
                    if lat and lng:
                        return lat, lng
                elif line.startswith('$GPGLL'):
                    self.count_online += 1
                    lat, lng = self.parse_gpgll(line)
                    if lat and lng:
                        return lat, lng
            self.count_online -= 1
            return None, None 
        except:
            self.count_online -= 1
            return None, None 

    def parse_gprmc(self, line):
        parts = line.split(',')
        if len(parts) > 6 and parts[2] == 'A':  
            lat = self.convert_to_degrees(parts[3], parts[4])
            lng = self.convert_to_degrees(parts[5], parts[6])
            return lat, lng
        return None, None

    def parse_gpgga(self, line):
        parts = line.split(',')
        if len(parts) > 5 and parts[6] == '1':
            lat = self.convert_to_degrees(parts[2], parts[3])
            lng = self.convert_to_degrees(parts[4], parts[5])
            return lat, lng
        return None, None

    def parse_gpgll(self, line):
        parts = line.split(',')
        if len(parts) > 5 and parts[6] == 'A':
            lat = self.convert_to_degrees(parts[1], parts[2])
            lng = self.convert_to_degrees(parts[3], parts[4])
            return lat, lng
        return None, None

    def convert_to_degrees(self, value, direction):
        degrees = float(value[:2])
        minutes = float(value[2:])
        decimal_degrees = degrees + (minutes / 60)
        if direction in ['S', 'W']:
            decimal_degrees = -decimal_degrees
        return decimal_degrees

# gps = GPSHandler('/dev/ttyUSB1',115200)
# while True:
#     lat, lng = gps.get_location()
#     print(gps.is_online())
#     if lat and lng:
#         print(f"Latitude: {lat}, Longitude: {lng}")
#     else:
#         print("No valid GPS data found")
