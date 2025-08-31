## check your respected ODBC Driver here
import pyodbc, platform
print("Python:", platform.architecture())
print("Installed ODBC drivers:", pyodbc.drivers())
