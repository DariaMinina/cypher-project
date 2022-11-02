import psycopg2 
import age

GRAPH_NAME = "nodes4"
conn = psycopg2.connect(host="0.0.0.0", port="5432", dbname="tracer", user="postgres", password="mysecretpassword")


if __name__ == "__main__":
    age.setUpAge(conn, GRAPH_NAME)
    '''
    
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                """SELECT * from cypher(%s, $$ CREATE (n:Person {name: 'Joe', title: 'Developer'}) $$) as (v agtype); """,
                (GRAPH_NAME,))
            cursor.execute(
                """SELECT * from cypher(%s, $$ CREATE (n:Person {name: 'Smith', title: 'Developer'}) $$) as (v agtype); """,
                (GRAPH_NAME,))
            cursor.execute("""SELECT * from cypher(%s, $$ 
                CREATE (n:Person {name: 'Tom', title: 'Manager'}) 
                RETURN n
                $$) as (v agtype); """, (GRAPH_NAME,))
            for row in cursor:
                print("CREATED::", row[0])

            cursor.execute("""SELECT * from cypher(%s, $$ 
                MATCH (a:Person {name: 'Joe'}), (b:Person {name: 'Smith'}) CREATE (a)-[r:workWith {weight: 5}]->(b)
                $$) as (v agtype); """, (GRAPH_NAME,))

            cursor.execute("""SELECT * from cypher(%s, $$ 
                MATCH (a:Person {name: 'Smith'}), (b:Person {name: 'Tom'}) CREATE (a)-[r:workWith {weight: 3}]->(b)
                $$) as (v agtype); """, (GRAPH_NAME,))

            # When data inserted or updated, You must commit.
            conn.commit()
        except Exception as ex:
            print(type(ex), ex)
            # if exception occurs, you must rollback all transaction. 
            conn.rollback()
            
        '''
    
    with conn.cursor() as cursor:
        try:
            print("------- [Select Vertices] --------")
            cursor.execute("""SELECT * from cypher(%s, $$ MATCH (n) RETURN n $$) as (v agtype) LIMIT 10; """, (GRAPH_NAME,))
            for row in cursor:
                vertex = row[0]
                print(vertex.id, vertex.label, vertex["name"], vertex["title"])
                print("-->", vertex)

            print(type(cursor))
            print("------- [Select Paths] --------")
            cursor.execute(
                """SELECT * from cypher(%s, $$ MATCH p=()-[:TRACE]->() RETURN p LIMIT 10 $$) as (v agtype); """,
                (GRAPH_NAME,))
            for row in cursor:
                path = row[0]
                v1 = path[0]
                e1 = path[1] # e1["weight"]
                v2 = path[2]
                print(v1.gtype, v1["name"], e1.gtype, e1.label, v2.gtype, v2["name"])
                print("-->", path)
        except Exception as ex:
            print(type(ex), ex)
            # if exception occurs, you must rollback even though just retrieving.
            conn.rollback()