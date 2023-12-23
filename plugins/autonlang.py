import ast
from spenx import Parser
from bs4 import BeautifulSoup
import re
import math

def TransformTimeToMS(time):
    matched = re.match(r"([0-9]+)([a-z])", time)
    time = int(matched.group(1))
    unit = matched.group(2)
    if unit == "s":
        return "pros::delay(" + str(time * 1000) + ");"
    elif unit == "m":
        return "pros::delay(" + str(time * 1000 * 60) + ");"
    elif unit == "ms":
        return "pros::delay(" + str(time) + ");"
    return "pros::delay(" + str(time * 1000) + ");"

def TransformIntoCalls(parsed):
    soup = BeautifulSoup(parsed, "html.parser")
    instructions = []
    if soup.find("framework").text == "pros":
        for tag in soup.find_all():
            if tag.name == "groups":
                time = TransformTimeToMS(tag.find("time").text)
                groups = tag.find_all("group")
                if tag.find("move"):
                    dir = tag.find("move").text
                    percent = 127 * (math.floor(int(tag.find("speed").text[:-1])) / 100)
                    flipped = percent
                    if dir == "rev":
                        flipped = -percent
                    for x in range(len(groups)):
                        instructions.append(groups[x].find("name").text + ".move(" + str(flipped) + ");")
                    instructions.append(time)
                    for x in range(len(groups)):
                        instructions.append(groups[x].find("name").text + ".move(0);")
                else:
                    left = groups[0]
                    right = groups[1]
                    rotation = tag.find("rotate").text
                    percent = 127 * (math.floor(int(tag.find("speed").text[:-1])) / 100)
                    if rotation == "left":
                        instructions.append(left.find("name").text + ".move(" + str(-percent) + ");")
                        instructions.append(right.find("name").text + ".move(" + str(percent) + ");")
                    elif rotation == "right":
                        instructions.append(left.find("name").text + ".move(" + str(percent) + ");")
                        instructions.append(right.find("name").text + ".move(" + str(-percent) + ");")
                    instructions.append(time)
                    instructions.append(left.find("name").text + ".move(0);")
                    instructions.append(right.find("name").text + ".move(0);")
        return "\n".join(instructions)
    else:
        raise Exception("Unsupported framework " + soup.find("framework").text + ": Only pros is supported")




def TransformJade(node, content):
    if type(node) == ast.Expr:
        if type(node.value) == ast.Call:
            parser = Parser()
            if type(node.value.func) == ast.Attribute:
                if node.value.func.attr == "include_auton":
                    if node.value.args[0].s.endswith(".aula"):
                        with open(node.value.args[0].s, "r", encoding="utf-8") as f:
                            parsed = parser.parse(f.read())
                            return {
                                'content' : TransformIntoCalls(parsed),
                                'header'  : ""
                            }
            elif node.value.func.id == "include_auton":
                if node.value.args[0].s.endswith(".aula"):
                    with open(node.value.args[0].s, "r", encoding="utf-8") as f:
                        parsed = parser.parse(f.read())
                        return {
                            'content' : TransformIntoCalls(parsed),
                            'header'  : ""
                        }
    return True

Transformers = [
    TransformJade
]