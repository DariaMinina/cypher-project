import age

DSN = "host=0.0.0.0 port=5432 dbname=tracer user=postgres password=mysecretpassword"
HOST = "0.0.0.0"
PORT = 5432
DB = "tracer"
USER = "postgres"
PASSWORD = "mysecretpassword"
GRAPH_NAME = "test_graph_name"


class AgeBasicAccessor:
    ag = None

    def set_up(self):
        print("Connecting to Test Graph.....")
        self.ag = age.connect(graph=GRAPH_NAME, host=HOST, port=PORT, dbname=DB, user=USER,
                              password=PASSWORD)

    def tear_down(self):
        # Clear test data
        print("Deleting Test Graph.....")
        age.deleteGraph(self.ag.connection, self.ag.graphName)
        self.ag.close()

    def create_graph(self, num_of_nodes, type_of_nodes, name_of_nodes, type_of_parts, name_of_parts, num_of_parts):
        ag = self.ag

        # Может выбрасываться age.exceptions.SqlExcutionError, надо как-то словить
        # если такого узла не существует

        for i in range(num_of_parts):
            ag.execCypher(
                f'''
                UNWIND range(1, {num_of_nodes}) AS i 
                MERGE (:{str(type_of_nodes[i])} {{ name: \"{str(name_of_nodes[i])}-\"+ i, marker: i}}) 
                '''
            )
            ag.execCypher(
                f"CREATE (:{type_of_parts[i]} {{name: \"{str(name_of_parts[i])}\"}}) "
            )

        for i in range(num_of_parts):
            ag.execCypher(
                f""" 
                MATCH 
                    (d1:{str(type_of_parts[i])}),
                    (p1:{str(type_of_nodes[i])})
                CREATE (p1) - [:IN] -> (d1)
                """
            )

        ag.commit()

    def create_relations(self, num_of_nodes, type_of_relation, type_of_parts, type_of_nodes):
        ag = self.ag
        for i in range(len(type_of_parts) - 1):
            ag.execCypher(
                f"""
                UNWIND range (1,{num_of_nodes}) as loop
                MATCH
                    (p1:{str(type_of_nodes[i])}) - [:IN] -> (part1:{str(type_of_parts[i])}),
                    (p2:{str(type_of_nodes[i+1])}) - [:IN] -> (part2:{str(type_of_parts[i+1])})
                WHERE p1.marker = loop AND (p2.marker = loop OR p2.marker = loop + 1)
                CREATE (p1) - [:{type_of_relation}] -> (p2)
                """
            )

        ag.commit()

    def select_chains(self, type_of_nodes, type_of_relation):
        ag = self.ag
        chain = ""
        arrow = ""
        for i in range(len(type_of_nodes)):
            chain = f"{chain} {arrow} (:{type_of_nodes[i]})"
            arrow = f"- [:{type_of_relation}] ->"
        print(chain)

        cursor = ag.execCypher(
            f'''
            MATCH p={chain}
            RETURN p
            '''
        )

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
            print(" ")


if __name__ == "__main__":
    num_of_nodes = 5  # количество узлов в одной доле графа
    type_of_nodes = ["HighOrderReqItem", "LowOrderReqItem", "CodeList", "Test"]
    name_of_nodes = ["HORI", "LORI", "CL", "T"]  # название узлов в каждой из долей
    type_of_parts = ["HighOrderReq", "LowOrderReq", "Code", "Tests"]
    name_of_parts = ["HOR1", "LOR1", "C1", "T1"]
    num_of_parts = len(type_of_parts)
    type_of_relation = "TRACE"

    age_test = AgeBasicAccessor()
    age_test.set_up()
    age_test.create_graph(num_of_nodes, type_of_nodes, name_of_nodes, type_of_parts, name_of_parts, num_of_parts)
    age_test.create_relations(num_of_nodes, type_of_relation, type_of_parts, type_of_nodes)
    age_test.select_chains(type_of_nodes, type_of_relation)
    age_test.tear_down()

