from rdflib import Graph, Literal, URIRef
from rdflib import RDF, RDFS, OWL
import json
import re

g = Graph()

g.parse('omg_essence.owl', format='turtle')

prefix = dict(g.namespaces())['']

REQUEST_1 = """
            SELECT ?x
            WHERE { 
                ?x rdfs:subClassOf :Customer
            }     
            """

REQUEST_2 = """
            SELECT ?x
            WHERE { 
                ?x rdf:type owl:NamedIndividual
            }     
            """

REQUEST_3 = """
            SELECT ?x
            WHERE { 
                ?x rdfs:subClassOf :Endeavor
            }     
            """

REQUEST_4 = """
        SELECT ?x
        WHERE { 
            ?x rdf:type owl:NamedIndividual .
            ?x ?y :platform_apps
        }     
        """

REQUEST_5 = """
        SELECT ?x
        WHERE { 
            ?x rdf:type owl:NamedIndividual .
            ?x ?y :technical_task_of_advertising
        }     
        """


def save_output_file():
    with open('omg_essence_output.owl', 'wb+') as f:
        f.write(g.serialize(format='turtle'))


# quickly look up the RDFS label of something
def label(s):
    return str(g.label(s))


def normalize(name):
    return re.sub('\W', '_', name)


def ref(name):
    return URIRef(prefix + normalize(name))


def propvalue(key, prop):
    for o, p, s in g:
        if o == key and p == prop:
            return s


def add(entries):
    for e in entries:
        g.add(e)


def build_mapping():
    return dict((o, (propvalue(o, RDFS.domain), propvalue(o, RDFS.range)))
                for o, p, s in g
                if p == RDF.type and s == OWL.ObjectProperty)


mapping = build_mapping()

with open('new_data.json', 'r') as f:
    json_array = json.load(f)
    # print(json_array)
    for row in json_array:
        obj = row['Object']
        predicate = row['predicate']
        subject = row['subject']
        pred = ref(predicate)
        if pred not in mapping:
            raise Exception('Unknown predicate: ' + predicate)
        oc, sc = mapping[pred]
        add([
            (ref(obj), RDF.type, OWL.NamedIndividual),
            (ref(obj), RDF.type, oc),
            (ref(obj), RDFS.label, Literal(obj)),

            (ref(subject), RDF.type, OWL.NamedIndividual),
            (ref(subject), RDF.type, sc),
            (ref(subject), RDFS.label, Literal(subject)),

            (ref(obj), pred, ref(subject))
        ])


def execute(query):
    res = g.query(f"PREFIX : <{prefix}> " + query)
    if len(res.vars) == 1:
        return list(map(lambda x: x[res.vars[0]], res))
    else:
        return list(res)


customer = execute(REQUEST_1)
print('All customer kernels: ', customer, '\n')

individual = execute(REQUEST_2)
print('All named individuals: ', individual, '\n')

solution = execute(REQUEST_3)
print('All endeavor kernels: ', solution, '\n')

request_4 = execute(REQUEST_4)
print('All stakeholders provide this: ', request_4, '\n')

request_5 = execute(REQUEST_5)
print('who demands it: ', request_5, '\n')

save_output_file()
