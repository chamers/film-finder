from networkx import edges
import streamlit as st
import pandas as pd
from sparql_processor import run_sparql_query
from streamlit_agraph import Config, Node, Edge, agraph


st.title("Film Finder")

film_name = st.text_input("Enter the name of a film")

if st.button("Search"):

    if not film_name:
        st.write("Please enter a film name.")

    else:
        ask_results = run_sparql_query(
            sparql_param=film_name,
            sparql_file="./sparql_queries/film_title_ask.sparql"
        )

        if ask_results and ask_results.get("boolean"):
            st.write("Film found! Displaying details...")

            results = run_sparql_query(
                sparql_param=film_name,
                sparql_file="./sparql_queries/film_details_with_number.sparql"
            )

            if results and results["results"]["bindings"]:

                columns = ["title", "runtime", "directorLabel", "countryLabel"]
                table_data = []

                for result in results["results"]["bindings"]:
                    row_data = {}

                    for column in columns:
                        row_data[column] = result.get(column, {}).get("value", "-")

                    table_data.append(row_data)

                table_data = pd.DataFrame(table_data)
                st.dataframe(table_data)

                film_number = results["results"]["bindings"][0].get(
                    "filmNumber", {}
                ).get("value", "0")

                st.write("Number of film results: " + film_number)

            else:
                st.write("Film found, but no details were returned.")
            
            graph = run_sparql_query(film_name, "./sparql_queries/film_construct.sparql")
            nodes = {}
            edges = []
            for binding in graph["results"]["bindings"]:
                subject = binding["s"]["value"]
                predicate = binding["p"]["value"]
                obj = binding["o"]["value"]

                if subject not in nodes:
                    subject_node = Node(id=subject, label=subject)
                    nodes[subject] = subject_node

                if obj not in nodes:
                    obj_node = Node(id=obj, label=obj)
                    nodes[obj] = obj_node

                edge = Edge(source=subject, target=obj, label=predicate)
                edges.append(edge)

            config = Config(width=800, height=600, directed=True, physics=True, hierarchical=True,       nodeHighlightBehavior=True)
            agraph(nodes=list(nodes.values()), edges=edges, config=config)

        else:
            st.write("No results found for the entered film name.")