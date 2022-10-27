import psycopg2 
import age

GRAPH_NAME = "nodes4"
conn = psycopg2.connect(host="0.0.0.0", port="5432", dbname="tracer", user="postgres", password="mysecretpassword")

age.setUpAge(conn, GRAPH_NAME)