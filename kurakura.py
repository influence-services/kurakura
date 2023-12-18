import ast
import os
import sys
import shutil
from simple_chalk import chalk
import io
from halo import Halo
import requests as req
import time
import subprocess
import zipfile
import types
import traceback as tb
import json


code = None
tree = None
content = ""
header = "#pragma once;\n"
inFunction = False

print(chalk.bold.magenta("くらくら!") + " " + chalk.bold.blue("BETA"))
print(
    chalk.cyanBright(
        "You are on the beta branch.\nThis branch is unstable, but will be updated based on bugs.\nA stable, public release will be available next season!"
    )
)

if not os.path.isfile("plugins.json"):
    print(chalk.bold.red("Plugins file doesn't exist."))
    open("plugins.json", "w").write("{}")
    print(chalk.bold.green("Created plugins file."))
else:
    print(chalk.bold.green("Plugins file exists."))

plugins = json.loads(open("plugins.json", "r").read())


def readSpecifiedLine(file, line):
    return io.open(file, mode="r", encoding="utf-8").readlines()[line - 1]


def detailExceptionByType(exctype):
    if exctype == "NameError":
        return (
            "Unknown variable name! Make sure you reference only variables that exist."
        )
    elif exctype == "SyntaxError":
        return "Invalid syntax! Try checking your code."
    elif exctype == "TypeError":
        return "Invalid type! Make sure you assign only valid types to variables."
    elif exctype == "IndentationError":
        return "Invalid indentation! Make sure you indent your code properly."
    elif exctype == "AttributeError":
        return "Invalid attribute! Make sure you reference only attributes that exist."
    elif exctype == "ValueError":
        return "Invalid value! Make sure you assign only valid values to variables."
    elif exctype == "KeyError":
        return "Invalid key! Make sure you reference only keys that exist."
    elif exctype == "IndexError":
        return "Invalid index! Make sure you reference only indexes that exist."
    elif exctype == "ImportError":
        return "Invalid import! Make sure you import only valid modules."
    elif exctype == "ModuleNotFoundError":
        return "Invalid module! Make sure you import only valid modules."
    elif exctype == "ZeroDivisionError":
        return "Invalid division! Make sure you do not divide by zero."
    elif exctype == "UnboundLocalError":
        return "Invalid variable! Make sure you assign a value to a variable before using it."
    elif exctype == "Exception":
        return "Generic exception! Please read the error details above!"
    else:
        return "Unknown error type! Please read the error details above!"


def anonymizeFile(file):
    file = file.replace("\\", "/")
    file = file.split("/")
    file = file[-1]
    return file


header = "~~~~~~~~ AN UNEXPECTED ERROR HAS OCCURRED ~~~~~~~~"


def exceptionHook(exctype, value, traceback: types.TracebackType):
    global header
    print(chalk.bold.magenta(header))
    print(chalk.bold.red("Something went wrong!"))
    print(chalk.bold.red("Please report this to the Kurakura developers."))
    exceptionTypeName = exctype.__name__
    print(
        chalk.blackBright("Error type: ")
        + chalk.bold.magenta(exceptionTypeName)
        + ' - "'
        + chalk.redBright(value)
        + '"'
    )
    print(
        chalk.bold.magenta("At: ")
        + traceback.tb_frame.f_code.co_filename
        + ":"
        + str(traceback.tb_lineno)
    )
    print(
        "  - "
        + chalk.blue(
            readSpecifiedLine(
                traceback.tb_frame.f_code.co_filename, traceback.tb_lineno
            ).strip()
        )
    )
    print(
        chalk.bold.blue("Explanation: ")
        + detailExceptionByType(exceptionTypeName or "Exception")
    )
    print("\n")
    print(chalk.bold.green("Reporting the error?"))
    print(chalk.bold.green("Please include the following error ID:"))
    errorID = (
        str(hex(int.from_bytes(exceptionTypeName.encode(), "big")))
        + "-"
        + str(hex(traceback.tb_lineno))
        + "-"
        + str(
            hex(
                int.from_bytes(
                    anonymizeFile(traceback.tb_frame.f_code.co_filename).encode(), "big"
                )
            )
        )
        + "-"
        + str(hex(int.from_bytes(str(value).encode(), "big")))
    )
    print(chalk.bold.blue(errorID))
    print("\n")
    print("Raw error: " + str(exctype) + " - " + str(value))
    print("\n".join(tb.format_tb(traceback)))


sys.excepthook = exceptionHook

if os.path.isfile("beautify.exe"):
    print(chalk.bold.green("Beautifier exists"))
else:
    print(chalk.bold.red("Beautifier does not exist. Downloading..."))
    halo = Halo(
        text="Downloading beautifier...",
        spinner="dots8",
        animation="marquee",
        force=True,
    )
    halo.start()
    s = req.get(
        "https://github.com/uncrustify/uncrustify/releases/download/uncrustify-0.78.1/uncrustify-0.78.1_f-win64.zip",
        allow_redirects=True,
    )
    open("uncrustify-0.78.1_f-win64.zip", "wb").write(s.content)
    halo.succeed(text="Downloaded beautifier.")
    halo = Halo(
        text="Extracting beautifier...",
        spinner="dots8",
        animation="marquee",
        force=True,
    )
    halo.start()
    shutil.unpack_archive("uncrustify-0.78.1_f-win64.zip", "uncrustify")
    halo.succeed(text="Extracted beautifier.")
    os.remove("uncrustify-0.78.1_f-win64.zip")
    path = "uncrustify/bin/uncrustify.exe"
    os.rename(path, "beautify.exe")
    shutil.rmtree("uncrustify")

if os.path.isfile("default.cfg"):
    print(chalk.bold.green("Default config exists"))
else:
    print(chalk.bold.red("Default config does not exist. Downloading..."))
    halo = Halo(
        text="Downloading default config...",
        spinner="dots8",
        animation="marquee",
        force=True,
    )
    halo.start()
    s = req.get(
        "https://raw.githubusercontent.com/uncrustify/uncrustify/master/documentation/htdocs/default.cfg",
        allow_redirects=True,
    )
    open("default.cfg", "wb").write(s.content)
    halo.succeed(text="Downloaded default config.")


def parse(fileName, path):
    oldTime = time.time()
    global code, tree, content, header, defined_external_vars, defined_global_vars, var_types

    code = open(path + ("/" if not len(path) == 0 else "") + fileName).read()
    tree = ast.parse(code)

    fileName = fileName.split("/")[-1]

    content = ""
    header = ""
    defined_external_vars = []
    defined_global_vars = []
    var_types = {}

    for node in tree.body:
        Transform(node)

    if not os.path.exists(("out/src/" + path).replace("//", "/")):
        os.makedirs(("out/src/" + path).replace("//", "/"))
    if not os.path.exists(("out/include/" + path).replace("//", "/")):
        os.makedirs(("out/include/" + path).replace("//", "/"))

    print(" - " + chalk.blue("For " + path + "/" + fileName + ":"))
    print("  - " + chalk.bold.cyan("Writing source file..."))
    open(
        ("out/src/" + path + "/" + ".".join(fileName.split(".")[:-1]) + ".cpp").replace(
            "//", "/"
        ),
        "w",
    ).write(content)
    print("  - " + chalk.bold.yellow("Writing header file..."))
    open(
        (
            "out/include/" + path + "/" + ".".join(fileName.split(".")[:-1]) + ".h"
        ).replace("//", "/"),
        "w",
    ).write(header)

    newTime = time.time()
    print(
        "  - "
        + chalk.bold.green("Done!")
        + " Took "
        + chalk.bold.magenta(str(round(newTime - oldTime, 2)))
        + " seconds."
    )

    hasEnded()


def transformInternalRebuildArgs(args: ast.arguments):
    global content
    args1 = []
    for arg in args:
        if type(arg) == ast.Constant:
            if type(arg.value) == list:
                vals = []
                for x in arg.value:
                    if type(x) == str:
                        vals.append('"' + x + '"')
                    elif type(x) == bool:
                        vals.append("true" if x else "false")
                    else:
                        vals.append(str(x))
                args1.append("{" + ",".join(vals) + "}")
            elif type(arg.value) == str:
                args1.append('"' + arg.value + '"')
            elif type(arg.value) == bool:
                args1.append("true" if arg.value else "false")
            else:
                args1.append(str(arg.value))
        else:
            if type(arg) == ast.Name:
                args1.append(arg.id)
            elif type(arg) == ast.Call:
                if type(arg.func) == ast.Attribute:
                    if arg.func.attr.startswith("this."):
                        arg.func.attr = arg.func.attr.replace("this.", "this->")
                        arg.func.value.id = "this"
                args1.append(
                    arg.func.id + "(" + transformInternalRebuildArgs(arg.args) + ")"
                )
            elif type(arg) == ast.Attribute:
                args1.append(arg.attr)
            elif type(arg) == ast.List:
                arg_t = []
                for x in arg.elts:
                    if type(x) == ast.Constant:
                        if type(x.value) == str:
                            arg_t.append('"' + x.value + '"')
                        elif type(x.value) == bool:
                            arg_t.append("true" if x.value else "false")
                        else:
                            arg_t.append(str(x.value))
                    elif type(x) == ast.Name:
                        arg_t.append(x.id)
                args1.append("{" + ",".join(arg_t) + "}")
            else:
                args1.append("auto " + arg.arg)
    return ",".join(args1)


def transformInternalStringifyConstant(constant):
    if type(constant) == ast.Constant:
        if type(constant.value) == str:
            return '"' + constant.value + '"'
        elif type(constant.value) == bool:
            return "true" if constant.value else "false"
        else:
            return str(constant.value)
    elif type(constant) == ast.Name:
        return constant.id
    else:
        raise Exception("Unknown node type: " + constant.__class__.__name__)


def internalCatchify(lamb, onerr):
    try:
        return lamb()
    except:
        return onerr()


defined_global_vars = []


def TransformFunctionDefinition(node: ast.FunctionDef):
    global content, header, inFunction, defined_variables, inClass, className
    inFunction = True
    defined_variables = []
    if inClass or node.name.startswith("__"):
        if node.name == "__init__":
            for x in node.args.args:
                if x.arg == "self":
                    node.args.args.remove(x)
            a = transformInternalRebuildArgs(node.args.args)
            header += className + "(" + ("" if a == None else a) + ");\n"
            content += className + "(" + ("" if a == None else a) + ") {\n"
            for x in node.body:
                if type(x) == ast.Assign:
                    if type(x.value) == ast.Call:
                        if type(x.value.func) == ast.Attribute:
                            if x.value.func.attr.startswith("this."):
                                x.value.func.attr = x.value.func.attr.replace(
                                    "this.", "this->"
                                )
                                x.value.func.value.id = "this"
                Transform(x)
            content += "}\n"
        else:
            typeReturned = ""
            realTypeReturned = ""
            if type(node.returns) == ast.Constant:
                typeReturned = transformInternalStringifyConstant(node.returns)
            else:
                typeReturned = node.returns.id
            if typeReturned == "Lie":
                typeReturned = "void"
                realTypeReturned = "Lie"
            header += (
                typeReturned
                + " "
                + node.name
                + "("
                + transformInternalRebuildArgs(node.args.args)
                + ");\n"
            )
            content += (
                typeReturned
                + " "
                + node.name
                + "("
                + transformInternalRebuildArgs(node.args.args)
                + ") {\n"
            )
            if realTypeReturned != "Lie":
                for x in node.body:
                    Transform(x)
            else:
                for x in node.body:
                    if type(x) != ast.Return:
                        Transform(x)
            content += "}\n"
        return node
    else:
        if type(node.returns) == ast.Constant:
            print(
                "   - "
                + chalk.bold.blueBright("Function ")
                + node.name
                + chalk.bold.blueBright(" returns ")
                + (
                    "None"
                    if not node.returns
                    else internalCatchify(
                        lambda: str(node.returns.id),
                        lambda: transformInternalStringifyConstant(node.returns),
                    )
                )
                + "..."
            )
            if type(node.returns.value) == str:
                header += (
                    "char *"
                    + node.name
                    + "("
                    + transformInternalRebuildArgs(node.args.args)
                    + ");\n"
                )
                content += (
                    "char *"
                    + node.name
                    + "("
                    + transformInternalRebuildArgs(node.args.args)
                    + ") {\n"
                )
            elif type(node.returns.value) == bool:
                header += (
                    "bool "
                    + node.name
                    + "("
                    + transformInternalRebuildArgs(node.args.args)
                    + ");\n"
                )
                content += (
                    "bool "
                    + node.name
                    + "("
                    + transformInternalRebuildArgs(node.args.args)
                    + ") {\n"
                )
            elif node.returns.value == None:
                header += (
                    "void "
                    + node.name
                    + "("
                    + transformInternalRebuildArgs(node.args.args)
                    + ");\n"
                )
                content += (
                    "void "
                    + node.name
                    + "("
                    + transformInternalRebuildArgs(node.args.args)
                    + ") {\n"
                )
        else:
            if not node.returns:
                print(
                    "   - "
                    + chalk.bold.blueBright("Function ")
                    + node.name
                    + chalk.bold.blueBright(" returns auto...")
                )
                header += (
                    "auto "
                    + node.name
                    + "("
                    + transformInternalRebuildArgs(node.args.args)
                    + ");\n"
                )
                content += (
                    "auto "
                    + node.name
                    + "("
                    + transformInternalRebuildArgs(node.args.args)
                    + ") {\n"
                )
            else:
                if node.returns.id == "Lie":
                    print(
                        "   - "
                        + chalk.bold.blueBright("Function ")
                        + node.name
                        + chalk.bold.blueBright(" returns auto...")
                    )
                    header += (
                        "void "
                        + node.name
                        + "("
                        + transformInternalRebuildArgs(node.args.args)
                        + ");\n"
                    )
                    content += (
                        "void "
                        + node.name
                        + "("
                        + transformInternalRebuildArgs(node.args.args)
                        + ") {\n"
                    )
                else:
                    print(
                        "   - "
                        + chalk.bold.blueBright("Function ")
                        + node.name
                        + chalk.bold.blueBright(" returns ")
                        + node.returns.id
                        + "..."
                    )
                    header += (
                        node.returns.id
                        + " "
                        + node.name
                        + "("
                        + transformInternalRebuildArgs(node.args.args)
                        + ");\n"
                    )
                    content += (
                        node.returns.id
                        + " "
                        + node.name
                        + "("
                        + transformInternalRebuildArgs(node.args.args)
                        + ") {\n"
                    )
        for node2 in node.body:
            if type(node2) == ast.Return:
                if type(node.returns) == ast.Constant:
                    pass
                elif node.returns.id == "Lie":
                    content += "}\n"
                    return node
            Transform(node2)
        return node


def TransformFunctionEnd(node: ast.FunctionDef):
    global content, inFunction
    inFunction = False
    content += "}\n"
    return node


def TransformFunctionCall(node: ast.Call):
    global content
    if node.func.id == "print":
        content += (
            "std::cout << "
            + transformInternalRebuildArgs(node.args)
            + " << std::endl;\n"
        )
    elif node.func.id.startswith("namespaces"):
        content += (
            node.func.id.replace("namespaces.", "").replace(".", "::")
            + "("
            + transformInternalRebuildArgs(node.args)
            + ");\n"
        )
    else:
        content += node.func.id + "(" + transformInternalRebuildArgs(node.args) + ");\n"
    return node


def TransformReturn(node: ast.Return):
    global content, inFunction
    if type(node.value) == ast.Constant:
        if type(node.value.value) == str:
            content += 'return "' + node.value.value + '";}\n'
        elif type(node.value.value) == bool:
            content += "return true;}\n" if node.value.value else "return false;}\n"
        else:
            content += "return " + str(node.value.value) + ";}\n"
    else:
        if not node.value:
            content += "return;}\n"
        else:
            content += "return " + node.value.id + ";}\n"
    inFunction = False
    return node


def transformInternalGetTypeName(constant):
    if type(constant) == ast.Constant:
        if type(constant.value) == str:
            return "char *"
        else:
            return type(constant.value).__name__
    elif type(constant) == ast.Call:
        if constant.func.id.startswith("new."):
            return constant.func.id.replace("new.", "")
    elif type(constant) == ast.BinOp:
        return transformInternalGetTypeName(constant.left)
    elif type(constant) == ast.UnaryOp:
        return transformInternalGetTypeName(constant.operand)
    else:
        return "auto"


var_types = {}
defined_variables = []
defined_external_vars = []


def TransformAssign(node: ast.Assign):
    global content, header, inFunction, var_types, defined_global_vars, defined_external_vars
    isDefined = False
    valu = ""
    if type(node.targets[0]) == ast.Attribute:
        if node.targets[0].attr in defined_global_vars:
            isDefined = True
        valu = node.targets[0].attr
    elif node.targets[0].id in defined_global_vars:
        isDefined = True
        valu = node.targets[0].id
    else:
        valu = node.targets[0].id
    if type(node.value) == ast.Call:
        _prior_func_path = []

        def parse_func_path(node):
            if type(node) == ast.Attribute:
                _prior_func_path.append(node.attr)
                parse_func_path(node.value)
            elif type(node) == ast.Name:
                _prior_func_path.append(node.id)
            else:
                raise Exception("Unknown node type: " + node.__class__.__name__)

        parse_func_path(node.value.func)
        _prior_func_path.reverse()
        _prior_chain = _prior_func_path
        if type(node.value.func) == ast.Name:
            if not isDefined:
                var_types[node.targets[0].id] = node.value.func.id
                defined_variables.append(node.targets[0].id)
                defined_global_vars.append(node.targets[0].id)
            if _prior_chain[0] == "new":
                chained = ".".join(_prior_chain[1:])
                content += (
                    chained
                    + " "
                    + node.targets[0].id
                    + "("
                    + transformInternalRebuildArgs(node.value.args)
                    + ");\n"
                )
                if (
                    not inFunction
                    and not isDefined
                    and not valu in defined_external_vars
                ):
                    header += "extern " + chained + " " + node.targets[0].id + ";\n"
                    defined_external_vars.append(node.targets[0].id)
            elif node.value.func.id == "Enum":
                return TransformEnum(node)
            else:
                chained = ".".join(_prior_chain)
                content += (
                    "auto "
                    + node.targets[0].id
                    + " = "
                    + chained
                    + "("
                    + transformInternalRebuildArgs(node.value.args)
                    + ");\n"
                )
                if (
                    not inFunction
                    and not isDefined
                    and not valu in defined_external_vars
                ):
                    header += "extern auto " + node.targets[0].id + ";\n"
                    defined_external_vars.append(node.targets[0].id)
        else:
            if not isDefined:
                var_types[node.targets[0].id] = ".".join(_prior_chain)
                defined_variables.append(node.targets[0].id)
                defined_global_vars.append(node.targets[0].id)
            chained = ".".join(_prior_chain)
            if _prior_chain[0] == "new":
                chained = ".".join(_prior_chain[1:])
                content += (
                    chained
                    + " "
                    + node.targets[0].id
                    + "("
                    + transformInternalRebuildArgs(node.value.args)
                    + ");\n"
                )
                if (
                    not inFunction
                    and not isDefined
                    and not valu in defined_external_vars
                ):
                    header += "extern " + chained + " " + node.targets[0].id + ";\n"
                    defined_external_vars.append(node.targets[0].id)
            else:
                content += (
                    ("auto " if not isDefined else "")
                    + node.targets[0].id
                    + " = "
                    + chained
                    + "("
                    + transformInternalRebuildArgs(node.value.args)
                    + ");\n"
                )
                if (
                    not inFunction
                    and not isDefined
                    and not valu in defined_external_vars
                ):
                    header += "extern " + chained + " " + node.targets[0].id + ";\n"
                    defined_external_vars.append(node.targets[0].id)
    else:
        if type(node.targets[0]) == ast.Attribute:
            if not isDefined:
                var_types[node.targets[0].attr] = transformInternalGetTypeName(
                    node.value
                )
                defined_variables.append(node.targets[0].attr)
                defined_global_vars.append(node.targets[0].attr)
            if type(node.value.value) == str:
                content += (
                    ("char *" if not isDefined else "")
                    + node.targets[0].attr
                    + ' = "'
                    + node.value.value
                    + '";\n'
                )
            elif type(node.value.value) == bool:
                content += (
                    ("bool " if not isDefined else "")
                    + node.targets[0].attr
                    + " = "
                    + ("true" if node.value.value else "false")
                    + ";\n"
                )
            else:
                content += (
                    (
                        transformInternalGetTypeName(node.value) + " "
                        if not isDefined
                        else ""
                    )
                    + node.targets[0].attr
                    + " = "
                    + str(node.value.value)
                    + ";\n"
                )
            if not inFunction and not isDefined and not valu in defined_external_vars:
                header += (
                    "extern "
                    + var_types[node.targets[0].attr]
                    + " "
                    + node.targets[0].attr
                    + ";\n"
                )
                defined_external_vars.append(node.targets[0].attr)
        elif node.targets[0].id in defined_variables:
            if not isDefined:
                var_types[node.targets[0].id] = transformInternalGetTypeName(node.value)
                defined_variables.append(node.targets[0].id)
                defined_global_vars.append(node.targets[0].id)
            if type(node.value) == ast.UnaryOp:
                node.value.operand.id = node.targets[0].id
                content += (
                    transformInternalGetTypeName(node.value)
                    + " "
                    + node.targets[0].id
                    + " = "
                    + transformInternalGetOpName(node.value.op)
                    + ";\n"
                )
            elif type(node.value) == ast.Constant:
                if type(node.value.value) == str:
                    node.value.value = (
                        node.value.value.replace("\\", "\\\\")
                        .replace('"', '\\"')
                        .replace("\n", "\\n")
                        .replace("\t", "\\t")
                        .replace("\r", "\\r")
                        .replace("'", "\\'")
                    )
                    content += (
                        ("char *" if not isDefined else "")
                        + node.targets[0].id.strip()
                        + ' = "'
                        + node.value.value
                        + '";\n'
                    )
                    if (
                        not inFunction
                        and not isDefined
                        and not valu in defined_external_vars
                    ):
                        header += "extern char *" + node.targets[0].id + ";\n"
                        defined_external_vars.append(node.targets[0].id)
                elif type(node.value.value) == bool:
                    content += (
                        ("bool " if not isDefined else "")
                        + node.targets[0].id
                        + " = "
                        + ("true" if node.value.value else "false")
                        + ";\n"
                    )
                    if (
                        not inFunction
                        and not isDefined
                        and not valu in defined_external_vars
                    ):
                        header += "extern bool " + node.targets[0].id + ";\n"
                        defined_external_vars.append(node.targets[0].id)
                else:
                    content += (
                        (
                            transformInternalGetTypeName(node.value) + " "
                            if not isDefined
                            else ""
                        )
                        + node.targets[0].id
                        + " = "
                        + str(node.value.value)
                        + ";\n"
                    )
                    if (
                        not inFunction
                        and not isDefined
                        and not valu in defined_external_vars
                    ):
                        header += (
                            "extern "
                            + transformInternalGetTypeName(node.value)
                            + " "
                            + node.targets[0].id
                            + ";\n"
                        )
                        defined_external_vars.append(node.targets[0].id)
        else:
            if type(node.value) == ast.Name:
                if not isDefined:
                    var_types[node.targets[0].id] = var_types[node.value.id]
                    defined_variables.append(node.targets[0].id)
                    defined_global_vars.append(node.targets[0].id)
                content += (
                    (var_types[node.value.id] + " " if not isDefined else "")
                    + node.targets[0].id
                    + " = "
                    + node.value.id
                    + ";"
                    + ("\n" if inFunction else "")
                )
                if (
                    not inFunction
                    and not isDefined
                    and not valu in defined_external_vars
                ):
                    header += (
                        "extern "
                        + var_types[node.value.id]
                        + " "
                        + node.targets[0].id
                        + ";\n"
                    )
                    defined_external_vars.append(node.targets[0].id)
            elif type(node.value) == ast.Call:
                chain = []

                def parse_chain(node):
                    if type(node) == ast.Attribute:
                        chain.append(node.attr)
                        parse_chain(node.value)
                    elif type(node) == ast.Name:
                        chain.append(node.id)
                    else:
                        raise Exception("Unknown node type: " + node.__class__.__name__)

                parse_chain(node.value.func)
                chain.reverse()
                if chain[0] == "namespaces":
                    if not isDefined:
                        var_types[node.targets[0].id] = ".".join(chain[1:]).replace(
                            ".", "::"
                        )
                        defined_variables.append(node.targets[0].id)
                        defined_global_vars.append(node.targets[0].id)
                    inferredType = ".".join(chain[1:]).replace(".", "::")
                    content += (
                        (
                            ("auto " if not inferredType else inferredType + " ")
                            if not isDefined
                            else ""
                        )
                        + node.targets[0].id
                        + " = "
                        + ".".join(chain[1:]).replace(".", "::")
                        + "("
                        + transformInternalRebuildArgs(node.value.args)
                        + ");\n"
                    )
                    if (
                        not inFunction
                        and not isDefined
                        and not valu in defined_external_vars
                    ):
                        header += (
                            "extern "
                            + (
                                ("auto " if not inferredType else inferredType + " ")
                                if not isDefined
                                else ""
                            )
                            + node.targets[0].id
                            + ";\n"
                        )
                        defined_external_vars.append(node.targets[0].id)
                else:
                    if type(node.value.func) == ast.Attribute:
                        if not isDefined:
                            var_types[node.targets[0].id] = node.value.func.attr
                            defined_variables.append(node.targets[0].id)
                            defined_global_vars.append(node.targets[0].id)
                        content += (
                            (node.value.func.attr + " " if not isDefined else "")
                            + node.targets[0].id
                            + " = "
                            + ".".join(chain)
                            + "("
                            + transformInternalRebuildArgs(node.value.args)
                            + ");\n"
                        )
                        if (
                            not inFunction
                            and not isDefined
                            and not valu in defined_external_vars
                        ):
                            header += (
                                "extern "
                                + node.value.func.attr
                                + " "
                                + node.targets[0].id
                                + ";\n"
                            )
                    else:
                        if not isDefined:
                            var_types[node.targets[0].id] = node.value.func.id
                            defined_variables.append(node.targets[0].id)
                            defined_global_vars.append(node.targets[0].id)
                        content += (
                            (node.value.func.id + " " if not isDefined else "")
                            + node.targets[0].id
                            + " = "
                            + ".".join(chain)
                            + "("
                            + transformInternalRebuildArgs(node.value.args)
                            + ");\n"
                        )
                        if (
                            not inFunction
                            and not isDefined
                            and not valu in defined_external_vars
                        ):
                            header += (
                                "extern "
                                + node.value.func.id
                                + " "
                                + node.targets[0].id
                                + ";\n"
                            )
                            defined_external_vars.append(node.targets[0].id)
            elif type(node.value) == ast.BinOp:
                if type(node.value.left) == ast.Name:
                    if not isDefined:
                        var_types[node.targets[0].id] = transformInternalGetTypeName(
                            node.value.left
                        )
                        defined_variables.append(node.targets[0].id)
                        defined_global_vars.append(node.targets[0].id)
                    if not hasattr(var_types, node.value.left.id):
                        var_types[node.value.left.id] = transformInternalGetTypeName(
                            node.value.left
                        )
                        defined_variables.append(node.value.left.id)
                        defined_global_vars.append(node.value.left.id)
                    if type(node.value.right) == ast.Constant:
                        content += (
                            (
                                var_types[node.value.left.id] + " "
                                if not isDefined
                                else ""
                            )
                            + node.targets[0].id
                            + " = "
                            + node.value.left.id
                            + " "
                            + transformInternalGetOpName(node.value.op)
                            + " "
                            + str(node.value.right.value)
                            + ";\n"
                        )
                        if (
                            not inFunction
                            and not isDefined
                            and not valu in defined_external_vars
                        ):
                            header += (
                                "extern "
                                + var_types[node.value.left.id]
                                + " "
                                + node.value.left.id
                                + ";\n"
                            )
                            defined_external_vars.append(node.value.left.id)
                    elif type(node.value.right) == ast.UnaryOp:
                        if type(node.value.right.operand) == ast.Constant:
                            content += (
                                (
                                    var_types[node.value.left.id] + " "
                                    if not isDefined
                                    else ""
                                )
                                + node.targets[0].id
                                + " = "
                                + node.value.left.id
                                + " "
                                + transformInternalGetOpName(node.value.op)
                                + " "
                                + transformInternalGetOpName(node.value.right.op)
                                + " "
                                + str(node.value.right.operand.value)
                                + ";\n"
                            )
                            if (
                                not inFunction
                                and not isDefined
                                and not valu in defined_external_vars
                            ):
                                header += (
                                    "extern "
                                    + var_types[node.value.left.id]
                                    + " "
                                    + node.value.left.id
                                    + ";\n"
                                )
                                defined_external_vars.append(node.value.left.id)
                        elif type(node.value.right.operand) == ast.Name:
                            content += (
                                (
                                    var_types[node.value.left.id] + " "
                                    if not isDefined
                                    else ""
                                )
                                + node.targets[0].id
                                + " = "
                                + node.value.left.id
                                + " "
                                + transformInternalGetOpName(node.value.op)
                                + " "
                                + transformInternalGetOpName(node.value.right.op)
                                + " "
                                + node.value.right.operand.id
                                + ";\n"
                            )
                            if (
                                not inFunction
                                and not isDefined
                                and not valu in defined_external_vars
                            ):
                                header += (
                                    "extern "
                                    + var_types[node.value.left.id]
                                    + " "
                                    + node.value.left.id
                                    + ";\n"
                                )
                                defined_external_vars.append(node.value.left.id)
                        else:
                            content += (
                                (
                                    var_types[node.value.left.id] + " "
                                    if not isDefined
                                    else ""
                                )
                                + node.targets[0].id
                                + " = "
                                + node.value.left.id
                                + " "
                                + transformInternalGetOpName(node.value.op)
                                + " "
                                + transformInternalGetOpName(node.value.right.op)
                                + ";\n"
                            )
                            if (
                                not inFunction
                                and not isDefined
                                and not valu in defined_external_vars
                            ):
                                header += (
                                    "extern "
                                    + var_types[node.value.left.id]
                                    + " "
                                    + node.value.left.id
                                    + ";\n"
                                )
                                defined_external_vars.append(node.value.left.id)
                    else:
                        content += (
                            (
                                var_types[node.value.left.id] + " "
                                if not isDefined
                                else ""
                            )
                            + node.targets[0].id
                            + " = "
                            + node.value.left.id
                            + " "
                            + transformInternalGetOpName(node.value.op)
                            + " "
                            + node.value.right.id
                            + ";\n"
                        )
                        if (
                            not inFunction
                            and not isDefined
                            and not valu in defined_external_vars
                        ):
                            header += (
                                "extern "
                                + var_types[node.value.left.id]
                                + " "
                                + node.value.left.id
                                + ";\n"
                            )
                            defined_external_vars.append(node.value.left.id)
                elif type(node.value.left) == ast.Constant:
                    if not isDefined:
                        var_types[node.targets[0].id] = transformInternalGetTypeName(
                            node.value.left
                        )
                        defined_variables.append(node.targets[0].id)
                        defined_global_vars.append(node.targets[0].id)
                    if type(node.value.right) == ast.Constant:
                        content += (
                            (
                                transformInternalGetTypeName(node.value.left) + " "
                                if not isDefined
                                else ""
                            )
                            + node.targets[0].id
                            + " = "
                            + str(node.value.left.value)
                            + " "
                            + transformInternalGetOpName(node.value.op)
                            + " "
                            + str(node.value.right.value)
                            + ";\n"
                        )
                        if (
                            not inFunction
                            and not isDefined
                            and not valu in defined_external_vars
                        ):
                            header += (
                                "extern "
                                + transformInternalGetTypeName(node.value.left)
                                + " "
                                + node.value.left.id
                                + ";\n"
                            )
                            defined_external_vars.append(node.value.left.id)
                    else:
                        content += (
                            (
                                transformInternalGetTypeName(node.value.left) + " "
                                if not isDefined
                                else ""
                            )
                            + node.targets[0].id
                            + " = "
                            + str(node.value.left.value)
                            + " "
                            + transformInternalGetOpName(node.value.op)
                            + " "
                            + node.value.right.id
                            + ";\n"
                        )
                        if (
                            not inFunction
                            and not isDefined
                            and not valu in defined_external_vars
                        ):
                            header += (
                                "extern "
                                + transformInternalGetTypeName(node.value.left)
                                + " "
                                + node.value.left.id
                                + ";\n"
                            )
                            defined_external_vars.append(node.value.left.id)
                else:
                    if not isDefined:
                        var_types[node.targets[0].id] = transformInternalGetTypeName(
                            node.value
                        )
                        defined_variables.append(node.targets[0].id)
                        defined_global_vars.append(node.targets[0].id)
                    content += (
                        (
                            transformInternalGetTypeName(node.value) + " "
                            if not isDefined
                            else ""
                        )
                        + node.targets[0].id
                        + " = "
                        + node.value.left.id
                        + " "
                        + transformInternalGetOpName(node.value.op)
                        + " "
                        + node.value.right.id
                        + ";\n"
                    )
            else:
                if not isDefined:
                    var_types[node.targets[0].id] = transformInternalGetTypeName(
                        node.value
                    )
                    defined_variables.append(node.targets[0].id)
                    defined_global_vars.append(node.targets[0].id)
                if type(node.value) == ast.UnaryOp:
                    content += (
                        (
                            transformInternalGetTypeName(node.value) + " "
                            if not isDefined
                            else ""
                        )
                        + node.targets[0].id
                        + " = "
                        + transformInternalGetOpName(node.value.op)
                        + node.value.operand.id
                        + ";\n"
                    )
                    if (
                        not inFunction
                        and not isDefined
                        and not valu in defined_external_vars
                    ):
                        header += (
                            "extern "
                            + transformInternalGetTypeName(node.value)
                            + " "
                            + node.value.operand.id
                            + ";\n"
                        )
                        defined_external_vars.append(node.value.operand.id)
                elif type(node.value) == ast.Constant:
                    if type(node.value.value) == str:
                        content += (
                            ("char *" if not isDefined else "")
                            + node.targets[0].id
                            + ' = "'
                            + node.value.value
                            + '";\n'
                        )
                    elif type(node.value.value) == bool:
                        content += (
                            ("bool " if not isDefined else "")
                            + node.targets[0].id
                            + " = "
                            + ("true" if node.value.value else "false")
                            + ";\n"
                        )
                    else:
                        content += (
                            (
                                transformInternalGetTypeName(node.value) + " "
                                if not isDefined
                                else ""
                            )
                            + node.targets[0].id
                            + " = "
                            + str(node.value.value)
                            + ";\n"
                        )
                    if (
                        not inFunction
                        and not isDefined
                        and not valu in defined_external_vars
                    ):
                        header += (
                            "extern "
                            + transformInternalGetTypeName(node.value)
                            + " "
                            + node.targets[0].id
                            + ";\n"
                        )
                        defined_external_vars.append(node.targets[0].id)
                else:
                    if type(node.value) == ast.Constant:
                        if type(node.value.value) == str:
                            content += (
                                ("char *" if not isDefined else "")
                                + node.targets[0].id
                                + ' = "'
                                + node.value.value
                                + '";\n'
                            )
                            if (
                                not inFunction
                                and not isDefined
                                and not valu in defined_external_vars
                            ):
                                header += "extern char *" + node.value.value + ";\n"
                                defined_external_vars.append(node.value.value)
                        elif type(node.value.value) == bool:
                            content += (
                                ("bool " if not isDefined else "")
                                + node.targets[0].id
                                + " = "
                                + ("true" if node.value.value else "false")
                                + ";\n"
                            )
                            if (
                                not inFunction
                                and not isDefined
                                and not valu in defined_external_vars
                            ):
                                header += "extern bool " + node.value.value + ";\n"
                                defined_external_vars.append(node.value.value)
                        else:
                            content += (
                                (
                                    transformInternalGetTypeName(node.value) + " "
                                    if not isDefined
                                    else ""
                                )
                                + node.targets[0].id
                                + " = "
                                + node.value.id
                                + ";\n"
                            )
                            if (
                                not inFunction
                                and not isDefined
                                and not valu in defined_external_vars
                            ):
                                header += (
                                    "extern "
                                    + transformInternalGetTypeName(node.value)
                                    + " "
                                    + node.value.value
                                    + ";\n"
                                )
                    else:
                        if type(node.value) == ast.Name:
                            content += (
                                (
                                    var_types[node.value.id] + " "
                                    if not isDefined
                                    else ""
                                )
                                + node.targets[0].id
                                + " = "
                                + node.value.id
                                + ";\n"
                            )
                            if (
                                not inFunction
                                and not isDefined
                                and not valu in defined_external_vars
                            ):
                                header += (
                                    "extern "
                                    + var_types[node.value.id]
                                    + " "
                                    + node.value.id
                                    + ";\n"
                                )
                                defined_external_vars.append(node.value.id)
                        else:
                            content += (
                                (
                                    transformInternalGetTypeName(node.value) + " "
                                    if not isDefined
                                    else ""
                                )
                                + node.targets[0].id
                                + " = "
                                + node.value.id
                                + ";\n"
                            )
                            if (
                                not inFunction
                                and not isDefined
                                and not valu in defined_external_vars
                            ):
                                header += (
                                    "extern "
                                    + transformInternalGetTypeName(node.value)
                                    + " "
                                    + node.value.id
                                    + ";\n"
                                )
                                defined_external_vars.append(node.value.id)
        if not inFunction and not isDefined and not valu in defined_external_vars:
            if var_types[node.targets[0].id] == "char *":
                header += "extern char *" + node.targets[0].id + ";\n"
            elif var_types[node.targets[0].id] == "bool":
                header += "extern bool " + node.targets[0].id + ";\n"
            else:
                header += (
                    "extern "
                    + var_types[node.targets[0].id]
                    + " "
                    + node.targets[0].id
                    + ";\n"
                )
            defined_external_vars.append(node.targets[0].id)
        return node


def transformInternalGetOpName(op):
    if type(op) == ast.Add:
        return "+"
    elif type(op) == ast.Sub:
        return "-"
    elif type(op) == ast.Mult:
        return "*"
    elif type(op) == ast.Div:
        return "/"
    elif type(op) == ast.Mod:
        return "%"
    elif type(op) == ast.Pow:
        return "**"
    elif type(op) == ast.LShift:
        return "<<"
    elif type(op) == ast.RShift:
        return ">>"
    elif type(op) == ast.BitOr:
        return "|"
    elif type(op) == ast.BitXor:
        return "^"
    elif type(op) == ast.BitAnd:
        return "&"
    elif type(op) == ast.FloorDiv:
        return "//"
    elif type(op) == ast.Eq:
        return "=="
    elif type(op) == ast.NotEq:
        return "!="
    elif type(op) == ast.Not:
        return "!"
    elif type(op) == ast.Lt:
        return "<"
    elif type(op) == ast.LtE:
        return "<="
    elif type(op) == ast.Gt:
        return ">"
    elif type(op) == ast.GtE:
        return ">="
    elif type(op) == ast.USub:
        return "-"
    elif type(op) == ast.UAdd:
        return "+"
    elif type(op) == ast.Is:
        return "=="
    else:
        raise Exception("Unknown node type: " + op.__class__.__name__)


def transformInternalRebuildConstantOrDynamic(constant):
    if type(constant) == ast.Constant:
        if type(constant.value) == str:
            return '"' + constant.value + '"'
        elif type(constant.value) == bool:
            return "true" if constant.value else "false"
        else:
            return str(constant.value)
    elif type(constant) == ast.Name:
        return constant.id
    else:
        raise Exception("Unknown node type: " + constant.__class__.__name__)


def TransformIf(node: ast.If):
    global content
    if isinstance(node, ast.If):
        if type(node.test) == ast.Compare:
            content += (
                "if ("
                + transformInternalRebuildConstantOrDynamic(node.test.left)
                + " "
                + transformInternalGetOpName(node.test.ops[0])
                + " "
                + transformInternalRebuildConstantOrDynamic(node.test.comparators[0])
                + ") {\n"
            )
        elif type(node.test) == ast.Call:
            chain = []

            def parse_chain(node):
                if type(node) == ast.Attribute:
                    chain.append(node.attr)
                    parse_chain(node.value)
                elif type(node) == ast.Name:
                    chain.append(node.id)
                    parse_chain(node.id)
                elif type(node) == str:
                    chain.append(node)
                else:
                    raise Exception("Unknown node type: " + node.__class__.__name__)

            parse_chain(node.test.func)
            chain.reverse()
            if type(node.test.func) == ast.Attribute:
                node.test.func.id = node.test.func.attr
            content += (
                "if ("
                + ".".join(chain[1:])
                + "("
                + transformInternalRebuildArgs(node.test.args)
                + ")) {\n"
            )
        else:
            content += "if (" + node.test.id + ") {\n"
        for node1 in node.body:
            Transform(node1)
        content += "}\n"
        hasCapturedElse = False
        if node.orelse:
            for node2 in node.orelse:
                if isinstance(node2, ast.If):
                    if type(node2.test) == ast.Compare:
                        content += (
                            "else if ("
                            + transformInternalRebuildConstantOrDynamic(node2.test.left)
                            + " "
                            + transformInternalGetOpName(node.test.ops[0])
                            + " "
                            + transformInternalRebuildConstantOrDynamic(
                                node.test.comparators[0]
                            )
                            + ") {\n"
                        )
                    else:
                        content += "else if (" + node2.test.id + ") {\n"
                    for node3 in node2.body:
                        Transform(node3)
                    content += "}\n"
                else:
                    if not hasCapturedElse:
                        hasCapturedElse = True
                        content += "else {\n"
                        for node2 in node.orelse:
                            Transform(node2)
                        content += "}\n"

    return node


def TransformIfEnd(node: ast.If):
    global content
    content += "}"
    return node


def transformInternalCompileCondition(node: ast.AST):
    if type(node) == ast.Constant:
        if type(node.value) == str:
            return '"' + node.value + '"'
        elif type(node.value) == bool:
            return "true" if node.value else "false"
        else:
            return str(node.value)
    elif type(node) == ast.Name:
        return node.id
    else:
        raise Exception("Unknown node type: " + node.__class__.__name__)


inWhile = False


def TransformWhile(node: ast.While):
    global content, inWhile
    content += "\nwhile (" + transformInternalCompileCondition(node.test) + ") {\n"
    inWhile = True
    for node in node.body:
        Transform(node)
    inWhile = False
    content += "}\n"
    return node


def TransformWhileEnd(node: ast.While):
    global content
    content += "}"
    return node


def TransformFor(node: ast.For):
    global content
    content += "for (" + node.target.id + " in " + node.iter.id + ") {\n"
    for node in node.body:
        Transform(node)
    content += "}\n"
    return node


def TransformForEnd(node: ast.For):
    global content
    content += "}\n"
    return node


def TransformBinOp(node: ast.BinOp):
    global content
    content += node.left.id + " " + node.op + " " + node.right.id + ";\n"
    return node


def TransformCompare(node: ast.Compare):
    global content
    content += node.left.id + " " + node.ops[0] + " " + node.comparators[0].id + ";\n"
    return node


def TransformUnaryOp(node: ast.UnaryOp):
    global content
    content += node.op + node.operand.id + ";\n"
    return node


def transformInternalStringifyAugAssign(node: ast.AugAssign):
    if type(node.op) == ast.Add:
        return "+="
    elif type(node.op) == ast.Sub:
        return "-="
    elif type(node.op) == ast.Mult:
        return "*="
    elif type(node.op) == ast.Div:
        return "/="
    elif type(node.op) == ast.Mod:
        return "%="
    elif type(node.op) == ast.Pow:
        return "**="
    elif type(node.op) == ast.LShift:
        return "<<="
    elif type(node.op) == ast.RShift:
        return ">>="
    elif type(node.op) == ast.BitOr:
        return "|="
    elif type(node.op) == ast.BitXor:
        return "^="
    elif type(node.op) == ast.BitAnd:
        return "&="
    elif type(node.op) == ast.FloorDiv:
        return "//="
    else:
        raise Exception("Unknown node type: " + node.__class__.__name__)


def transformInternalStringifyAugSide(node: ast.AugAssign):
    if type(node.value) == ast.Constant:
        if type(node.value.value) == str:
            return '"' + node.value.value + '"'
        elif type(node.value.value) == bool:
            return "true" if node.value.value else "false"
        else:
            return str(node.value.value)
    elif type(node.value) == ast.Name:
        return node.value.id
    else:
        raise Exception("Unknown node type: " + node.__class__.__name__)


def TransformAugAssign(node: ast.AugAssign):
    global content, defined_global_vars
    isDefined = False
    if type(node.target) == ast.Attribute:
        if node.target.attr in defined_global_vars:
            isDefined = True
    elif node.target.id in defined_global_vars:
        isDefined = True
    content += (
        (node.target.id + " " if not isDefined else "")
        + transformInternalStringifyAugAssign(node)
        + " "
        + transformInternalStringifyAugSide(node)
        + ";\n"
    )
    return node


def TransformBreak(node: ast.Break):
    global content
    content += "break;\n"
    return node


def TransformContinue(node: ast.Continue):
    global content
    content += "continue;\n"
    return node


def TransformPass(node: ast.Pass):
    global content
    if inWhile:
        content += "continue;\n"
    else:
        content += "return;\n"
    return node


def transformInternalRebuildCallArgs(args: ast.arguments):
    args1 = []
    for arg in args:
        if type(arg) == ast.Constant:
            if type(arg.value) == str:
                args1.append('"' + arg.value + '"')
            elif type(arg.value) == bool:
                args1.append("true" if arg.value else "false")
            else:
                args1.append(str(arg.value))
        elif type(arg) == ast.Name:
            args1.append(arg.id)
        elif type(arg) == ast.BinOp:
            args1.append(transformInternalInferType(arg))
        elif type(arg) == ast.UnaryOp:
            args1.append(transformInternalInferType(arg))
        elif type(arg) == ast.Call:
            args1.append(transformInternalInferType(arg))
        else:
            raise Exception("Unknown node type: " + arg.__class__.__name__)
    return ", ".join(args1)


def transformInternalInferType(node: ast.AST):
    if type(node) == ast.Constant:
        if type(node.value) == str:
            return "char *"
        elif type(node.value) == bool:
            return "bool"
        elif type(node.value) == int:
            return "int"
        else:
            return type(node.value).__name__
    elif type(node) == ast.Name:
        return node.id
    elif type(node) == ast.BinOp:
        val_r = None
        if type(node.right) == ast.Constant:
            if type(node.right.value) == str:
                val_r = '"' + node.right.value + '"'
            elif type(node.right.value) == bool:
                val_r = "true" if node.right.value else "false"
            else:
                val_r = str(node.right.value)
        elif type(node.right) == ast.Name:
            val_r = node.right.id
        elif type(node.right) == ast.BinOp:
            val_l_1 = None
            if type(node.right.left) == ast.Constant:
                if type(node.right.left.value) == str:
                    val_l_1 = '"' + node.right.left.value + '"'
                elif type(node.right.left.value) == bool:
                    val_l_1 = "true" if node.right.left.value else "false"
                else:
                    val_l_1 = str(node.right.left.value)
            val_r_1 = None
            if type(node.right.right) == ast.Constant:
                if type(node.right.right.value) == str:
                    val_r_1 = '"' + node.right.right.value + '"'
                elif type(node.right.right.value) == bool:
                    val_r_1 = "true" if node.right.right.value else "false"
                else:
                    val_r_1 = str(node.right.right.value)
            val_r = (
                val_l_1
                + " "
                + transformInternalGetOpName(node.right.op)
                + " "
                + val_r_1
            )
        elif type(node.right) == ast.UnaryOp:
            val_l_1 = None
            if type(node.right.operand) == ast.Constant:
                if type(node.right.operand.value) == str:
                    val_l_1 = '"' + node.right.operand.value + '"'
                elif type(node.right.operand.value) == bool:
                    val_l_1 = "true" if node.right.operand.value else "false"
                else:
                    val_l_1 = str(node.right.operand.value)
            val_r = transformInternalGetOpName(node.right.op) + " " + val_l_1
        else:
            raise Exception("Unknown node type: " + node.right.__class__.__name__)
        return (
            transformInternalInferType(node.left)
            + " "
            + transformInternalGetOpName(node.op)
            + " "
            + val_r
        )
    elif type(node) == ast.UnaryOp:
        return (
            transformInternalGetOpName(node.op)
            + " "
            + transformInternalInferType(node.operand)
        )
    else:
        raise Exception("Unknown node type: " + node.__class__.__name__)


def TransformExpr(node: ast.Expr):
    print(
        "   - "
        + chalk.bold.blueBright("Expression ")
        + (
            (
                node.value.func.id
                if hasattr(node.value.func, "id")
                else node.value.func.attr
            )
            if hasattr(node.value, "func")
            else ""
        )
        + "..."
    )
    global content, header
    built_path = []

    def parse_chain(node):
        if type(node) == ast.Attribute:
            built_path.append(node.attr)
            parse_chain(node.value)
        elif type(node) == ast.Name:
            built_path.append(node.id)
        else:
            raise Exception("Unknown node type: " + node.__class__.__name__)

    if isinstance(node.value, ast.Call):
        if type(node.value.func) == ast.Attribute:
            parse_chain(node.value.func)
            built_path.reverse()
            if built_path[0] == "namespaces":
                content += (
                    ".".join(built_path[1:]).replace(".", "::")
                    + "("
                    + transformInternalRebuildCallArgs(node.value.args)
                    + ");\n"
                )
            else:
                content += (
                    ".".join(built_path)
                    + "("
                    + (transformInternalRebuildCallArgs(node.value.args) or "")
                    + ");\n"
                )
            return node
        elif type(node.value.func) == ast.Name:
            parse_chain(node.value.func)
            built_path.reverse()
            s = ".".join(built_path)
            if s.startswith("header_flag"):
                header += "#define " + node.value.args[0].value + "\n"
            elif s.startswith("header_define"):
                header += (
                    "#define "
                    + node.value.args[0].value
                    + " "
                    + node.value.args[1].value
                    + "\n"
                )
            elif s.startswith("header_ifndef"):
                header += "#ifndef " + node.value.args[0].value + "\n"
            elif s.startswith("header_include"):
                header += '#include "' + node.value.args[0].value + '"\n'
            elif s.startswith("namespaces"):
                content += (
                    node.value.func.id.replace("namespaces.", "").replace(".", "::")
                    + "("
                    + transformInternalRebuildCallArgs(node.value.args)
                    + ");\n"
                )
            elif node.value.func.id == "print":
                content += (
                    "std::cout << "
                    + transformInternalRebuildCallArgs(node.value.args)
                    + " << std::endl;\n"
                )
            else:
                content += (
                    node.value.func.id
                    + "("
                    + (transformInternalRebuildCallArgs(node.value.args) or "")
                    + ");\n"
                )
            return node
    elif isinstance(node.value, ast.BinOp):
        content += (
            transformInternalInferType(node.value)
            + " "
            + node.value.left.id
            + " "
            + transformInternalGetOpName(node.value.op)
            + " "
            + node.value.right.id
            + ";\n"
        )
    elif isinstance(node.value, ast.UnaryOp):
        content += (
            transformInternalInferType(node.value)
            + " "
            + node.value.op
            + " "
            + node.value.operand.id
            + ";\n"
        )
    if type(node.value) == ast.Call:
        if type(node.value.func) == ast.Attribute:
            name = node.value.func.attr
            if name.startswith("header_flag"):
                header += "#define " + node.value.args[0].value + "\n"
            elif name.startswith("header_define"):
                header += (
                    "#define "
                    + node.value.args[0].value
                    + " "
                    + node.value.args[1].value
                    + "\n"
                )
            elif name.startswith("header_ifndef"):
                header += "#ifndef " + node.value.args[0].value + "\n"
            elif name.startswith("header_include"):
                header += '#include "' + node.value.args[0].value + '"\n'
            elif name.startswith("namespaces"):
                content += (
                    node.value.func.attr.replace("namespaces.", "").replace(".", "::")
                    + "("
                    + transformInternalRebuildCallArgs(node.value.args)
                    + ");\n"
                )
            elif name.startswith("print"):
                content += (
                    "std::cout << "
                    + transformInternalRebuildCallArgs(node.value.args)
                    + " << std::endl;\n"
                )
            else:
                content += (
                    node.value.func.attr
                    + "("
                    + (transformInternalRebuildCallArgs(node.value.args) or "")
                    + ");\n"
                )
        else:
            name = node.value.func.id
            if name == "print":
                content += (
                    "std::cout << "
                    + transformInternalRebuildCallArgs(node.value.args)
                    + " << std::endl;\n"
                )
            else:
                content += (
                    name
                    + "("
                    + (transformInternalRebuildCallArgs(node.value.args) or "")
                    + ");\n"
                )
    else:
        content += node.value.id + ";"
    return node


def hasEnded():
    global toParse

    for i in toParse:
        print("- " + chalk.bold.green("Running recursive compiler for " + i[0] + "..."))
        toParse.remove(i)
        parse(i[0] + ".py", "/".join(i[1]))


def TransformImport(node: ast.Import):
    global content, header
    content += '#include "' + node.names[0].name + '.h"\n'


def TransformEnum(node: ast.Assign):
    global content, header
    args = []
    name = ""
    enum = node.value.args[0].value
    values = node.value.args[1].elts
    name = enum
    for value in values:
        args.append(value.value)
    header += "enum " + name + " {\n"
    for arg in args:
        header += arg + ",\n"
    header += "};\n"
    return node


toParse = []


def TransformFromImport(node: ast.ImportFrom):
    global content, toParse, header
    module = node.module
    name = node.names[0].name
    if module == None:
        content += '#include "' + name + '.h"\n'
        if not name in toParse:
            toParse.append([name, []])
    elif module.startswith("."):
        path = module.replace(".", "/")
        content += '#include "' + path + "/" + name + '.h"\n'
    elif module == "builtins":
        content += "#include <" + name + ">\n"
        header += "#include <" + name + ">\n"
    elif module.startswith("namespaces"):
        isNamespaceMulti = len(module.split(".")) > 1
        if isNamespaceMulti:
            name = ".".join(module.split(".")[1:]) + "." + name
        content += "using namespace " + name.replace(".", "::") + ";\n"
        header += "using namespace " + name.replace(".", "::") + ";\n"
    elif module.startswith("headers"):
        module = module.replace("headers.", "")
        path = "/".join(module.replace(".", "/").split("/")[1:])
        if len(path) > 0:
            path = path + "/"
        content += '#include "' + path + name + '.h"\n'
        header += '#include "' + path + name + '.h"\n'
    elif module.startswith("this"):
        module = module.replace("this.", "")
        path = module.replace(".", "/")
        content += '#include "' + path + "/" + name + '.h"\n'
        header += '#include "' + path + "/" + name + '.h"\n'
        if not name in toParse:
            toParse.append([name, path.split("/")])
    elif module.startswith("hpp"):
        module = module.replace("hpp.", "")
        path = module.replace(".", "/")
        content += '#include "' + path + "/" + name + '.hpp"\n'
        header += '#include "' + path + "/" + name + '.hpp"\n'
    elif module.startswith("external"):
        module = module.replace("external.", "")
        path = module.replace(".", "/")
        content += '#include "' + path + "/" + name + '.h"\n'
        header += '#include "' + path + "/" + name + '.h"\n'
    else:
        path = module.replace(".", "/")
        content += '#include "' + path + "/" + name + '.h"\n'
        toParse.append([name, path.split("/")])
    return node


inClass = False
className = ""


def TransformClassDefinition(node: ast.ClassDef):
    global content, header, inClass, className
    inClass = True
    className = node.name
    header += "class " + node.name + " {\npublic:\n"
    content += "class " + node.name + " {\npublic:\n"
    for node in node.body:
        Transform(node)
    header += "};\n"
    content += "};\n"
    inClass = False
    className = ""
    return node


def TransformClassEnd(node: ast.ClassDef):
    global content
    content += "};\n"
    return node


def TransformClassProperty(node: ast.Assign):
    global content
    content += node.targets[0].id + " = " + node.value.id + ";\n"
    return node


def TransformClassMethod(node: ast.FunctionDef):
    global content, header, inClass, className
    if node.name == "__init__":
        header += className + "();\n"
        content += className + "() {\n"
        for node in node.body:
            Transform(node)
        content += "};\n"
        return node
    header += (
        "auto "
        + node.name
        + "("
        + transformInternalRebuildArgs(node.args.args)
        + ");\n"
    )
    content += (
        "auto "
        + node.name
        + "("
        + transformInternalRebuildArgs(node.args.args)
        + ") {\n"
    )
    for node in node.body:
        Transform(node)
    content += "};\n"
    return node


def Transform(node: ast.AST):
    global content
    cancelled = False
    for x in plugins:
        p = importlib.import_module("plugins." + x)
        for x1 in p.Transformers:
            if not x1(node, {"content": content, "header": header}):
                cancelled = True
    if cancelled:
        return node
    if isinstance(node, ast.FunctionDef):
        TransformFunctionDefinition(node)
    elif isinstance(node, ast.Call):
        TransformFunctionCall(node)
    elif isinstance(node, ast.Return):
        TransformReturn(node)
    elif isinstance(node, ast.Assign):
        TransformAssign(node)
    elif isinstance(node, ast.If):
        TransformIf(node)
    elif isinstance(node, ast.While):
        TransformWhile(node)
    elif isinstance(node, ast.For):
        TransformFor(node)
    elif isinstance(node, ast.BinOp):
        TransformBinOp(node)
    elif isinstance(node, ast.Compare):
        TransformCompare(node)
    elif isinstance(node, ast.UnaryOp):
        TransformUnaryOp(node)
    elif isinstance(node, ast.AugAssign):
        TransformAugAssign(node)
    elif isinstance(node, ast.Break):
        TransformBreak(node)
    elif isinstance(node, ast.Continue):
        TransformContinue(node)
    elif isinstance(node, ast.Pass):
        TransformPass(node)
    elif isinstance(node, ast.Expr):
        TransformExpr(node)
    elif isinstance(node, ast.Module):
        pass
    elif isinstance(node, ast.Import):
        TransformImport(node)
    elif isinstance(node, ast.ImportFrom):
        TransformFromImport(node)
    elif isinstance(node, ast.ClassDef):
        TransformClassDefinition(node)
    else:
        raise Exception("Unknown node type: " + node.__class__.__name__)


def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split(".")[0]
    format = base.split(".")[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move("%s.%s" % (name, format), destination)


def detect_project(path):
    if (
        os.path.exists(path + "/kurakura.py")
        and os.path.exists(path + "/default.cfg")
        and os.path.exists(path + "/beautify.exe")
    ):
        return True
    else:
        return False


if __name__ == "__main__":
    oldTotalTime = time.time()
    success = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "remake":
            path = sys.argv[2] if len(sys.argv) > 2 else input("Enter project name: ")
            if os.path.exists(path):
                print(chalk.green.bold("Folder exists!"))
            else:
                print(chalk.red.bold("Folder does not exist. Exiting!"))
                sys.exit(1)
            halo = Halo(text="Remaking project...", spinner="dots")
            halo._text = "Copying myself..."
            shutil.copyfile("kurakura.py", path + "/kurakura.py")
            halo._text = "Copying default.cfg..."
            shutil.copyfile("default.cfg", path + "/default.cfg")
            halo._text = "Copying uncrustify..."
            shutil.copyfile("beautify.exe", path + "/beautify.exe")
            halo.succeed("Done!")
        elif sys.argv[1] == "script":
            print(chalk.bold.green("KuraScript v1.0.0"))
            inferredScriptPath = sys.argv[2] if len(sys.argv) > 2 else None
            if not inferredScriptPath or not os.path.exists(inferredScriptPath):
                print(chalk.bold.yellow("Script doesn't exist. Inferring..."))
                inferredScriptPath = "compile.kura"
                if not os.path.exists(inferredScriptPath):
                    print(chalk.bold.red("Script doesn't exist. Exiting!"))
                    sys.exit(1)
                iLine = 0
                compiled = False
                endedCompilation = False
                for x in open(inferredScriptPath, "r").read().split("\n"):
                    iLine += 1
                    if x.startswith("Compile-Kura"):
                        path = x.split(" ")[1]
                        if os.path.isfile(path):
                            print(
                                chalk.green.bold("Line " + str(iLine) + ": ")
                                + "Detected compile source: "
                                + path
                            )
                            pr = subprocess.Popen(
                                "py kurakura.py " + path,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                            )
                            out, err = pr.communicate()
                            pr.wait()
                            print(
                                chalk.green.bold("Line " + str(iLine) + ": ")
                                + "Compiled "
                                + path
                                + " + included (recursive)!"
                            )
                        endedCompilation = True
                if not endedCompilation:
                    print(
                        chalk.bold.red(
                            "Script doesn't contain any compilation commands. Exiting!"
                        )
                    )
                    sys.exit(1)
        elif sys.argv[1] == "new":
            path = sys.argv[2] if len(sys.argv) > 2 else input("Enter project name: ")
            if os.path.exists(path):
                print(chalk.bold.red("Project already exists. Exiting!"))
                sys.exit(1)
            os.makedirs(path)
            os.makedirs(path + "/out")
            os.makedirs(path + "/out/src")
            os.makedirs(path + "/out/include")
            open(path + "/main.py", "w").write("def main() -> int:\n\treturn 0\n")
            open(path + "/default.cfg", "w").write(
                io.open("default.cfg", mode="r", encoding="utf-8").read()
            )
            open(path + "/beautify.exe", "wb").write(
                io.open("beautify.exe", mode="rb").read()
            )
            io.open(path + "/kurakura.py", mode="w", encoding="utf-8").write(
                io.open("kurakura.py", mode="r", encoding="utf-8").read()
            )
        elif sys.argv[1] == "deinit":
            if detect_project("."):
                print(chalk.bold.green("Detected project!"))
            else:
                print(chalk.bold.red("Could not detect project. Exiting!"))
                sys.exit(1)
            print(chalk.bold.red("Are you sure you want to deinitialize this project?"))
            print(chalk.bold.red("This action cannot be undone!"))
            print(chalk.bold.red("Type 'yes' to confirm."))
            if input("> ") == "yes":
                if os.path.isfile("plugins.json"):
                    os.remove("plugins.json")
                if os.path.exists("plugins"):
                    shutil.rmtree("plugins")
                if os.path.exists("out"):
                    shutil.rmtree("out")
                if os.path.exists("pkg.zip"):
                    os.remove("pkg.zip")
                if os.path.exists("kurakura.compiled.py"):
                    os.remove("kurakura.compiled.py")
                os.remove("default.cfg")
                os.remove("beautify.exe")
                for root, dirs, files in os.walk("."):
                    for file in files:
                        if file.endswith(".py") and file != "kurakura.py":
                            os.remove(os.path.join(root, file))
                print(chalk.bold.green("Deinitialized project!"))
            else:
                print(chalk.bold.green("Cancelled!"))
        elif sys.argv[1] == "clean":
            path = sys.argv[2] if len(sys.argv) > 2 else input("Enter project name: ")
            if os.path.exists(path) and detect_project(path):
                print(chalk.green.bold("Folder exists!"))
            else:
                print(chalk.red.bold("Folder does not exist. Exiting!"))
                sys.exit(1)
            if os.path.exists(path + "/out"):
                shutil.rmtree(path + "/out")
                print(chalk.bold.green("Cleaned output folder!"))
            if os.path.exists(path + "/pkg.zip"):
                os.remove(path + "/pkg.zip")
                print(chalk.bold.green("Cleaned package!"))
            print(chalk.bold.green("All done!"))
        # elif sys.argv[1] == "toolchain":
        #    print(chalk.bold.green("Minifying toolchain..."))
        #    text = io.open("kurakura.py", mode="r", encoding="utf-8").read()
        #    min = python_minifier.minify(text)
        #    io.open("dist/kurakura.py", mode="w", encoding="utf-8").write(min)
        #    print(chalk.bold.green("Minified toolchain!"))
        #    print(chalk.bold.green("Copying to main directory..."))
        #    shutil.copyfile('dist/kurakura.py', 'kurakura.compiled.py')
        #    print(chalk.bold.green("Copied to main directory!"))
        #    print(chalk.bold.green("Cleaning up..."))
        #    shutil.rmtree('dist')
        #    print(chalk.bold.blue("You may now distribute the optimized toolchain."))
        #    print(chalk.bold.green("All done!"))
        elif sys.argv[1] == "del":
            if sys.argv[2] == ".":
                print(chalk.red.bold("Cannot delete current directory. Exiting!"))
                sys.exit(1)
            path = sys.argv[2] if len(sys.argv) > 2 else input("Enter project name: ")
            if os.path.exists(path) and detect_project(path):
                print(chalk.green.bold("Folder exists!"))
            else:
                print(chalk.red.bold("Folder does not exist. Exiting!"))
                sys.exit(1)
            print(chalk.bold.red("Are you sure you want to delete " + path + "?"))
            print(chalk.bold.red("This action cannot be undone!"))
            print(chalk.bold.red("Type 'yes' to confirm."))
            if input("> ") == "yes":
                shutil.rmtree(path)
                print(chalk.bold.green("Deleted " + path + "!"))
            else:
                print(chalk.bold.green("Cancelled!"))
        elif sys.argv[1] == "plugin_add":
            plugin = sys.argv[2] if len(sys.argv) > 2 else input("Enter plugin name: ")
            if os.path.exists("plugins/" + plugin):
                print(chalk.green.bold("Plugin exists!"))
            else:
                print(chalk.red.bold("Plugin does not exist. Exiting!"))
                sys.exit(1)
            print(chalk.bold.green("Installing plugin..."))
            if not os.path.isfile("plugins.json"):
                open("plugins.json", "w").write("{}")
            plugins = json.loads(open("plugins.json", "r").read())
            plugins[plugin] = "1.0.0"
            open("plugins.json", "w").write(json.dumps(plugins))
            print(chalk.bold.green("Installed plugin!"))
        elif sys.argv[1] == "plugin_remove":
            plugin = sys.argv[2] if len(sys.argv) > 2 else input("Enter plugin name: ")
            if os.path.exists("plugins/" + plugin):
                print(chalk.green.bold("Plugin exists!"))
            else:
                print(chalk.red.bold("Plugin does not exist. Exiting!"))
                sys.exit(1)
            print(chalk.bold.green("Uninstalling plugin..."))
            if not os.path.isfile("plugins.json"):
                open("plugins.json", "w").write("{}")
            plugins = json.loads(open("plugins.json", "r").read())
            del plugins[plugin]
            open("plugins.json", "w").write(json.dumps(plugins))
            print(chalk.bold.green("Uninstalled plugin!"))
        elif sys.argv[1] == "pkg":
            path = sys.argv[2] if len(sys.argv) > 2 else input("Enter project name: ")
            if os.path.exists(path) and detect_project(path):
                print(chalk.green.bold("Folder exists!"))
            else:
                print(chalk.red.bold("Folder does not exist. Exiting!"))
                sys.exit(1)
            if os.path.exists(path + "/out"):
                shutil.rmtree(path + "/out")
            if not os.path.isfile(path + "/main.py"):
                print(chalk.red.bold("main.py does not exist. Exiting!"))
                sys.exit(1)
            os.chdir(path)
            print(chalk.bold.green("Starting compiler on " + path + "..."))
            p = subprocess.Popen(
                "py kurakura.py main.py",
                shell=True,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            (output, err) = p.communicate()
            p_status = p.wait()
            print(chalk.bold.green("Compiling complete!"))
            halo = Halo(
                text="Compressing...", spinner="dots8", animation="marquee", force=True
            )
            halo.start()
            zipf = zipfile.ZipFile(path + "/pkg" + ".zip", "w", zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk(path + "/out"):
                for file in files:
                    if not file.endswith(".zip"):
                        zipf.write(os.path.join(root, file))
            zipf.close()
            halo.succeed(text="Compressed!")
            print(chalk.bold.green("All done!"))
        elif sys.argv[1].endswith(".py"):
            if detect_project("."):
                print(chalk.bold.green("Detected project!"))
            else:
                print(chalk.bold.red("Could not detect project. Exiting!"))
                sys.exit(1)
            if not sys.argv[1].endswith(".py"):
                print(chalk.bold.red("Input file is not a .py file. Exiting!"))
                sys.exit(1)
            if os.path.exists("out"):
                shutil.rmtree("out")
            if not os.path.isfile(sys.argv[1]):
                print(chalk.bold.red("Input file does not exist. Exiting!"))
                sys.exit(1)
            if not os.path.basename(sys.argv[1]) == "main.py":
                print(
                    chalk.bold.yellow(
                        "Why is the input file not named main.py? We'll just build it anyway."
                    )
                )
            print(chalk.bold.green("Starting operations on " + sys.argv[1] + "..."))
            print(chalk.bold.green("- Compiling " + sys.argv[1] + "..."))
            parse(sys.argv[1], "")
            print(
                chalk.bold.magentaBright("Done!")
                + " Output is in "
                + chalk.bold.blue("out/")
            )
            success = True
        else:
            print(chalk.bold.red("Unknown command. Exiting!"))
            sys.exit(1)
    else:
        print(
            chalk.bold.red(
                "No input files. Will attempt to infer from current directory."
            )
        )
        if os.path.isfile("main.py"):
            print(chalk.bold.green("Detected main.py!"))
            if os.path.exists("out"):
                shutil.rmtree("out")
            print(chalk.bold.green("- Compiling main.py..."))
            parse("main.py", "")
            print(
                chalk.bold.magentaBright("Done!")
                + " Output is in "
                + chalk.bold.blue("out/")
            )
            success = True
        else:
            print(chalk.bold.red("Could not find main.py! Exiting!"))
            sys.exit(1)
    if success == True:
        print(chalk.bold.green("Beautifying..."))
        for root, dirs, files in os.walk("out/src"):
            for file in files:
                if file.endswith(".cpp"):
                    print(
                        " - "
                        + chalk.blue.bold("Beautifying ")
                        + os.path.join(root, file)
                        + "..."
                    )
                    p = subprocess.Popen(
                        "beautify.exe -c default.cfg -f "
                        + os.path.join(root, file)
                        + " -o "
                        + os.path.join(root, file),
                        shell=True,
                        stdout=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    (output, err) = p.communicate()
                    p_status = p.wait()
                    print(
                        " - "
                        + chalk.green.bold("Beautified ")
                        + os.path.join(root, file)
                        + "..."
                    )
                    if len(output.strip()) > 0:
                        print(
                            " - "
                            + chalk.blue.magenta("Output")
                            + ": "
                            + output.decode("utf-8")
                        )
                    elif len(err.strip()) > 0:
                        print(
                            " - " + chalk.red.bold("Error") + ": " + err.decode("utf-8")
                        )
        for root, dirs, files in os.walk("out/include"):
            for file in files:
                if file.endswith(".h"):
                    print(
                        " - "
                        + chalk.blue.bold("Beautifying ")
                        + os.path.join(root, file)
                        + "..."
                    )
                    p = subprocess.Popen(
                        "beautify.exe -c default.cfg -f "
                        + os.path.join(root, file)
                        + " -o "
                        + os.path.join(root, file),
                        shell=True,
                        stdout=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    (output, err) = p.communicate()
                    p_status = p.wait()
                    print(
                        " - "
                        + chalk.green.bold("Beautified ")
                        + os.path.join(root, file)
                        + "..."
                    )
                    if len(output.strip()) > 0:
                        print(
                            " - "
                            + chalk.blue.magenta("Output")
                            + ": "
                            + output.decode("utf-8")
                        )
                    elif len(err.strip()) > 0:
                        print(
                            " - " + chalk.red.bold("Error") + ": " + err.decode("utf-8")
                        )
        for root, dirs, files in os.walk("out/src"):
            for file in files:
                if file.endswith("~"):
                    os.remove(os.path.join(root, file))
        for root, dirs, files in os.walk("out/include"):
            for file in files:
                if file.endswith("~"):
                    os.remove(os.path.join(root, file))
        print(chalk.bold.magentaBright("Done!"))
        print(chalk.bold.green("All done!"))
        newTotalTime = time.time()
        print(
            chalk.bold.green("Total time taken: ")
            + chalk.bold.magenta(str(round(newTotalTime - oldTotalTime, 2)))
            + " seconds."
        )
