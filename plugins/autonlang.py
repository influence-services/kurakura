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

rout = {}

def _pneumatics(tag, instructions, dontAppend = False):
    port = int(tag.find("port").text)
    call_rout = tag.find("call")
    _local_instructions = []
    if call_rout:
        routine = rout[call_rout.text]
        if not dontAppend:
            instructions.extend(routine)
        else:
            _local_instructions.extend(routine)
    if tag.find("state").text == "on":
        if not dontAppend:
            instructions.append("digitalWrite(" + str(port) + ", HIGH);")
        else:
            _local_instructions.append("digitalWrite(" + str(port) + ", HIGH);")
    else:
        if not dontAppend:
            instructions.append("digitalWrite(" + str(port) + ", LOW);")
        else:
            _local_instructions.append("digitalWrite(" + str(port) + ", LOW);")
    if dontAppend:
        return _local_instructions

def _groups(tag, instructions, routines, dontAppend = False):
    time = TransformTimeToMS(tag.find("time").text)
    groups = tag.find_all("group")
    call_rout = tag.find("call")
    _local_instructions = []
    if call_rout:
        routine = routines[call_rout.text]
        if not dontAppend:
            instructions.extend(routine)
        else:
            _local_instructions.extend(routine)
    if not tag.find("rotate") and not tag.find("move"):
        for x in range(len(groups)):
            dir = groups[x].find("dir").text
            percent = 127 * (math.floor(int(groups[x].find("speed").text[0:-1])) / 100)
            flipped = percent
            if dir == "rev":
                flipped = -percent
            if not dontAppend:
                instructions.append(groups[x].find("name").text + ".move(" + str(flipped) + ");")
            else:
                _local_instructions.append(groups[x].find("name").text + ".move(" + str(flipped) + ");")
        instructions.append(time)
        for x in range(len(groups)):
            if not dontAppend:
                instructions.append(groups[x].find("name").text + ".move(0);")
            else:
                _local_instructions.append(groups[x].find("name").text + ".move(0);")
    elif tag.find("move"):
        dir = tag.find("move").text
        percent = 127 * (math.floor(int(tag.find("speed").text[:-1])) / 100)
        flipped = percent
        if dir == "rev":
            flipped = -percent
        for x in range(len(groups)):
            if not dontAppend:
                instructions.append(groups[x].find("name").text + ".move(" + str(flipped) + ");")
            else:
                _local_instructions.append(groups[x].find("name").text + ".move(" + str(flipped) + ");")
        if not dontAppend:
            instructions.append(time)
        else:
            _local_instructions.append(time)
        for x in range(len(groups)):
            if not dontAppend:
                instructions.append(groups[x].find("name").text + ".move(0);")
            else:
                _local_instructions.append(groups[x].find("name").text + ".move(0);")
    else:
        left = groups[0]
        right = groups[1]
        rotation = tag.find("rotate").text
        percent = 127 * (math.floor(int(tag.find("speed").text[:-1])) / 100)
        if rotation == "left":
            if not dontAppend:
                instructions.append(left.find("name").text + ".move(" + str(-percent) + ");")
                instructions.append(right.find("name").text + ".move(" + str(percent) + ");")
            else:
                _local_instructions.append(left.find("name").text + ".move(" + str(-percent) + ");")
                _local_instructions.append(right.find("name").text + ".move(" + str(percent) + ");")
        elif rotation == "right":
            if not dontAppend:
                instructions.append(left.find("name").text + ".move(" + str(percent) + ");")
                instructions.append(right.find("name").text + ".move(" + str(-percent) + ");")
            else:
                _local_instructions.append(left.find("name").text + ".move(" + str(percent) + ");")
                _local_instructions.append(right.find("name").text + ".move(" + str(-percent) + ");")
        if not dontAppend:
            instructions.append(time)
            instructions.append(left.find("name").text + ".move(0);")
            instructions.append(right.find("name").text + ".move(0);")
        else:
            _local_instructions.append(time)
            _local_instructions.append(left.find("name").text + ".move(0);")
            _local_instructions.append(right.find("name").text + ".move(0);")
    if dontAppend:
        return _local_instructions

def _routine(tag, instructions):
    name = tag.find("name").text
    rout[name] = []
    for child in tag.children:
        if child.name == "pneumatics":
            rout[name].extend(_pneumatics(child, rout[name], True))
        elif child.name == "groups":
            rout[name].extend(_groups(child, rout[name], rout, True))

def TransformIntoCalls(parsed):
    global rout
    soup = BeautifulSoup(parsed, "html.parser")
    instructions = []
    for tag in soup.contents:
        if tag.name == "def":
            _routine(tag, instructions)
        if tag.name == "pneumatics":
            _pneumatics(tag, instructions)
        elif tag.name == "groups":
            _groups(tag, instructions, rout)
    return "\n".join(instructions)




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
