from datetime import datetime
s = datetime.strptime("20091229050936", "%Y%m%d%H%M%S")
print("{:%H:%M %d %B %Y (UTC)}".format(s))