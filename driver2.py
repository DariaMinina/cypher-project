import psycopg2
import age

GRAPH_NAME = "my_graph_name"
conn = psycopg2.connect(host="0.0.0.0", port="5432", dbname="tracer", user="postgres", password="mysecretpassword")

if __name__ == "__main__":
    age.setUpAge(conn, GRAPH_NAME)

    with conn.cursor() as cursor:
        try:
            cursor.execute(
                """ SELECT * from cypher(%s, $$
	                UNWIND range(1, 10) AS i
	                MERGE (:HighOrderReqItem { name: "HORI-"+ i})
                    $$) as (a agtype); 
                """, (GRAPH_NAME,)
            )
            cursor.execute(
                """ SELECT * from cypher(%s, $$
	                UNWIND range(1, 10) AS i
	                MERGE (:LowOrderReqItem { name: "LORI-"+ i})
                    $$) as (a agtype); 
                """, (GRAPH_NAME,)
            )
            cursor.execute(
                """ SELECT * from cypher(%s, $$
	                UNWIND range(1, 10) AS i
	                MERGE (:CodeList { name: "CL-"+ i})
                    $$) as (a agtype); 
                """, (GRAPH_NAME,)
            )
            cursor.execute(
                """ SELECT * from cypher(%s, $$
	                UNWIND range(1, 10) AS i
	                MERGE (:Test { name: "T-"+ i})
                    $$) as (a agtype); 
                """, (GRAPH_NAME,)
            )
            cursor.execute(
                """ SELECT * from cypher(%s, $$
                    CREATE (:HighOrderReq {version: 1})
                    CREATE (:LowOrderReq {version: 1})
                    CREATE (:Code {version: 1})
                    CREATE (:Tests {version: 1})
                    $$) as (a agtype);
                """, (GRAPH_NAME,)
            )
            cursor.execute(
                """
                SELECT * from cypher(%s, $$
                MATCH 
	                (d1:HighOrderReq),
	                (p1:HighOrderReqItem)
                CREATE (p1) - [:IN] -> (d1)
                $$) as (a agtype);
                """, (GRAPH_NAME,)
            )
            cursor.execute(
                """
                SELECT * from cypher(%s, $$
                MATCH 
	                (d1:LowOrderReq),
	                (p1:LowOrderReqItem)
                    CREATE (p1) - [:IN] -> (d1)
                    $$) as (a agtype);
                """, (GRAPH_NAME,)
            )
            cursor.execute(
                """
                SELECT * from cypher(%s, $$
                MATCH 
                    (d1:Code),
                    (p1:CodeList)
                    CREATE (p1) - [:IN] -> (d1)
                    $$) as (a agtype);
                """, (GRAPH_NAME,)
            )
            cursor.execute(
                """
                SELECT * from cypher(%s, $$
                MATCH 
                    (d1:Tests),
                    (p1:Test)
                    CREATE (p1) - [:IN] -> (d1)
                    $$) as (a agtype);
                """, (GRAPH_NAME,)
            )
            for row in cursor:
                print("CREATED::", row[0])

            # When data inserted or updated, You must commit.
            conn.commit()
        except Exception as ex:
            print(type(ex), ex)
            # if exception occurs, you must rollback all transaction. 
            conn.rollback()


    with conn.cursor() as cursor:
        try:
            print("------- [Select Vertices] --------")
            cursor.execute("""SELECT * from cypher(%s, $$ MATCH (n) RETURN n $$) as (v agtype) LIMIT 10; """,
                           (GRAPH_NAME,)
                           )
            for row in cursor:
                vertex = row[0]
                print(vertex.id, vertex.label, vertex["name"])
                print("-->", vertex)

            # print(type(cursor))
            print("------- [Select Paths] --------")
            cursor.execute(
                """SELECT * from cypher(%s, $$ MATCH p=()-[:IN]->() RETURN p LIMIT 10 $$) as (v agtype); """,
                (GRAPH_NAME,)
            )
            for row in cursor:
                path = row[0]
                v1 = path[0]
                e1 = path[1]  # e1["weight"]
                v2 = path[2]
                print(v1.gtype, v1["name"], e1.gtype, e1.label, v2.gtype, v2["version"])
                print("-->", path)
        except Exception as ex:
            print(type(ex), ex)
            # if exception occurs, you must rollback even though just retrieving.
            conn.rollback()

    age.deleteGraph(conn, GRAPH_NAME)
    conn.close()