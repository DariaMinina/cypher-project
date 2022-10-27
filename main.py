from provider import Provider
import random

random.seed(60)


def read_from_data():
    provider_template = Provider("cypher/")
    start_query = "SELECT * from cypher('my_graph_name', $$\n"
    result = provider_template.get("create_without_nodes")
    end_query = "$$) as (a agtype);\n"
    with open("create2.txt", "w") as f:
        f.write(start_query + result + end_query)


def make_random_create_without_nodes():
    start_query = "SELECT * from cypher('my_graph_name', $$\n"
    end_query = "$$) as (a agtype);\n"
    with open("test.txt", "w") as f:
        f.write(start_query)
        for num in range(10):
            f.write(
                f'CREATE (HORI{num}:HighOrderReqItem {{name: \'HighOrderReqItem{num}\', part: \'HighOrderReq\'}})\n'
            )
            f.write(
                f'CREATE (LORI{num}:LowOrderReqItem {{name: \'LowOrderReqItem{num}\', part: \'LowOrderReq\'}})\n'
            )
            f.write(
                f'CREATE (CL{num}:CodeList {{name: \'CL{num}\', part: \'Code\'}})\n'
            )
            f.write(
                f'CREATE (CL{num}:CodeList {{name: \'T{num}\', part: \'Tests\'}})\n'
            )

        f.write(end_query)


if __name__ == "__main__":
    # read_from_data()
    make_random_create_without_nodes()
