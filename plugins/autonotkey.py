import ast
from spenx import Parser
from bs4 import BeautifulSoup
import re
import math


rout = {}

def _pneumatics(tag, instructions, dontAppend = False):
    _local_instructions = []
    port = int(tag.find("port").text)
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
    groups = tag.find_all("group")
    _local_instructions = []
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
    if dontAppend:
        return _local_instructions

maps = {
    "R1": "E_CONTROLLER_DIGITAL_R1",
    "R2": "E_CONTROLLER_DIGITAL_R2",
    "L1": "E_CONTROLLER_DIGITAL_L1",
    "L2": "E_CONTROLLER_DIGITAL_L2",
    "up": "E_CONTROLLER_DIGITAL_UP",
    "down": "E_CONTROLLER_DIGITAL_DOWN",
    "left": "E_CONTROLLER_DIGITAL_LEFT",
    "right": "E_CONTROLLER_DIGITAL_RIGHT",
    "A": "E_CONTROLLER_DIGITAL_A",
    "B": "E_CONTROLLER_DIGITAL_B",
    "X": "E_CONTROLLER_DIGITAL_X",
    "Y": "E_CONTROLLER_DIGITAL_Y"
}

def TransformIntoCalls(parsed):
    global rout
    soup = BeautifulSoup(parsed, "html.parser")
    instructions = ["while (true) {"]
    for tag1 in soup.contents:
        if tag1.name == "on":
            isSingle = False
            if tag1.find("single"):
                isSingle = True
            if isSingle:
                instructions.append("if (controller_get_digital_new_press(E_CONTROLLER_MASTER, " + maps[tag1.find("button").text] + ")) {")
            else:
                instructions.append("if (controller_get_digital(E_CONTROLLER_MASTER, " + maps[tag1.find("button").text] + ")) {")
            for tag in tag1.children:
                if tag.name == "pneumatics":
                    _pneumatics(tag, instructions)
                elif tag.name == "groups":
                    _groups(tag, instructions, rout)
            instructions.append("}")
        elif tag1.name == "drive":
            leftGroup = tag1.find("left")
            rightGroup = tag1.find("right")
            driveType = tag1.find("type").text
            instructions.append("int left = controller_get_analog(E_CONTROLLER_MASTER, E_CONTROLLER_ANALOG_LEFT_Y);")
            instructions.append("int right = controller_get_analog(E_CONTROLLER_MASTER, E_CONTROLLER_ANALOG_RIGHT_Y);")
            instructions.append("int singleX = controller_get_analog(E_CONTROLLER_MASTER, E_CONTROLLER_ANALOG_LEFT_X);")
            instructions.append("int singleY = controller_get_analog(E_CONTROLLER_MASTER, E_CONTROLLER_ANALOG_LEFT_Y);")
            names = {
                "frontLeft": leftGroup.find("front").text,
                "backLeft": leftGroup.find("back").text,
                "frontRight": rightGroup.find("front").text,
                "backRight": rightGroup.find("back").text
            }
            if driveType == "double" or driveType == "tank":
                instructions.append(names["frontLeft"] + ".move(left);")
                instructions.append(names["backLeft"] + ".move(left);")
                instructions.append(names["frontRight"] + ".move(right);")
                instructions.append(names["backRight"] + ".move(right);")
            elif driveType == "single":
                instructions.append(names["frontLeft"] + ".move(singleY + singleX);")
                instructions.append(names["backLeft"] + ".move(singleY + singleX);")
                instructions.append(names["frontRight"] + ".move(singleY - singleX);")
                instructions.append(names["backRight"] + ".move(singleY - singleX);")
    instructions.extend(["pros::delay(20);", "}"])
    return "\n".join(instructions)




def TransformJade(node, content):
    if type(node) == ast.Expr:
        if type(node.value) == ast.Call:
            parser = Parser()
            if type(node.value.func) == ast.Attribute:
                if node.value.func.attr == "include_notkey":
                    if node.value.args[0].s.endswith(".nkey"):
                        with open(node.value.args[0].s, "r", encoding="utf-8") as f:
                            parsed = parser.parse(f.read())
                            return {
                                'content' : TransformIntoCalls(parsed),
                                'header'  : ""
                            }
            elif node.value.func.id == "include_notkey":
                if node.value.args[0].s.endswith(".nkey"):
                    with open(node.value.args[0].s, "r", encoding="utf-8") as f:
                        parsed = parser.parse(f.read())
                        return {
                            'content' : TransformIntoCalls(parsed),
                            'header'  : ""
                        }
    return False

Transformers = [
    TransformJade
]
