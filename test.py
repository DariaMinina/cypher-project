import age
from age.models import Vertex

DSN = "host=0.0.0.0 port=5432 dbname=tracer user=postgres password=mysecretpassword"
HOST = "0.0.0.0"
PORT = 5432
DB = "tracer"
USER = "postgres"
PASSWORD = "mysecretpassword"
GRAPH_NAME = "test_graph_name"


class AgeBasicAccessor:
    ag = None
    def setUp(self):
        print("Connecting to Test Graph.....")
        self.ag = age.connect(graph=GRAPH_NAME, host=HOST, port=PORT, dbname=DB, user=USER,
                              password=PASSWORD)

    def tearDown(self):
        # Clear test data
        print("Deleting Test Graph.....")
        age.deleteGraph(self.ag.connection, self.ag.graphName)
        self.ag.close()

    def testExec(self):
        ag = self.ag
        # Create and Return single column
        cursor = ag.execCypher("CREATE (n:Person {name: %s, title: 'Developer'}) RETURN n", params=('Andy',))
        for row in cursor:
            print(Vertex, type(row[0]))

        # Create and Return multi columns
        cursor = ag.execCypher("CREATE (n:Person {name: %s, title: %s}) RETURN id(n), n.name", cols=['id', 'name'],
                               params=('Jack', 'Manager'))
        row = cursor.fetchone()
        print(row[0], row[1])
        ag.commit()

    def createGraph(self):
        ag = self.ag

        # Может выбрасываться age.exceptions.SqlExcutionError, надо как-то словить
        # если такого узла не существует

        ag.execCypher("UNWIND range(1, 5) AS i MERGE (:HighOrderReqItem { name: \"HORI-\"+ i, marker: i}) ")
        ag.execCypher("UNWIND range(1, 5) AS i MERGE (:LowOrderReqItem { name: \"LORI-\"+ i, marker: i}) ")
        ag.execCypher("UNWIND range(1, 5) AS i MERGE (:CodeList { name: \"CL-\"+ i, marker: i}) ")
        ag.execCypher("UNWIND range(1, 5) AS i MERGE (:Test { name: \"T-\"+ i, marker: i}) ")
        ag.execCypher("CREATE (:HighOrderReq {name: \"HOR1\"}) CREATE (:LowOrderReq {name: \"LOR1\"}) CREATE (:Code {name: \"C1\"}) CREATE (:Tests {name: \"T1\"})")
        ag.execCypher(
            """ 
            MATCH 
	            (d1:HighOrderReq),
	            (p1:HighOrderReqItem)
            CREATE (p1) - [:IN] -> (d1)
            """
        )
        ag.execCypher(
            """ 
            MATCH 
                (d1:LowOrderReq),
                (p1:LowOrderReqItem)
            CREATE (p1) - [:IN] -> (d1)
            """
        )
        ag.execCypher(
            """ 
            MATCH 
                (d1:Code),
                (p1:CodeList)
            CREATE (p1) - [:IN] -> (d1)
            """
        )
        ag.execCypher(
            """ 
            MATCH 
                (d1:Tests),
                (p1:Test)
            CREATE (p1) - [:IN] -> (d1)
            """
        )

        ag.execCypher(
            """
            UNWIND range (1,5) as loop
            MATCH
                (p1:HighOrderReqItem),
                (p2:LowOrderReqItem)
            WHERE p1.marker = loop AND (p2.marker = loop OR p2.marker = loop + 1)
            CREATE (p1) - [:TRACE] -> (p2)
            """
        )

        ag.execCypher(
            """
            UNWIND range (1,5) as loop
            MATCH
                (p1:LowOrderReqItem),
                (p2:CodeList)
            WHERE p1.marker = loop AND (p2.marker = loop OR p2.marker = loop + 1)
            CREATE (p1) - [:TRACE] -> (p2)
            """
        )

        ag.execCypher(
            """
            UNWIND range (1,5) as loop
            MATCH
                (p1:CodeList),
                (p2:Test)
            WHERE p1.marker = loop AND (p2.marker = loop OR p2.marker = loop + 1)
            CREATE (p1) - [:TRACE] -> (p2)
            """
        )

        ag.commit()

        cursor = ag.execCypher("MATCH p=(p1:HighOrderReqItem) - [l:TRACE] ->  (p2:LowOrderReqItem) - [:TRACE] -> (p3:CodeList) - [:TRACE] -> (p4:Test) RETURN p")

        count = 0
        for row in cursor:
            path = row[0]
            indent = ""
            for e in path:
                if e.gtype == age.TP_VERTEX:
                    print(indent, e.label, e["name"])
                elif e.gtype == age.TP_EDGE:
                    print(indent, e.label)
                else:
                    print(indent, "Unknown element.", e)

                count += 1
                indent += " >"


if __name__ == "__main__":
    age_test =  AgeBasicAccessor()
    age_test.setUp()
    # age_test.testExec()
    age_test.createGraph()
    # age_test.tearDown()


