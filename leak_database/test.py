import phonenumbers

# line='41580595959'

# parsed_number=phonenumbers.parse(line, "CH")

# print(parsed_number)

# line="@BADBOYS RecorDs.:8/20/2016 12:00:00 AM::"

# print(line.split(":"))
# print(line[-2:-1])
# print(line[-2]  == ":" and line.split(":")[-1] == "\n")

r_email ="daniel.van.elewout@gmail.com"

_=r_email.split("@")[1].split(".")

a=_[-1]
b=_[-2]

print(a,b)