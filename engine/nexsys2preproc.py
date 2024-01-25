"""
Defines built-in preprocessors for adding
syntactic sugar to Nexsys2.
"""
from copy import copy
from engine.nexsys2lib import DeclaredVariable, nexsys_findall

def comments(system: str, ctx_dict: dict, declared_dict: dict):
    """
    Removes comments from code prior to processing anything else.

    ### Example: Will not be present in any later preprocessing stage
    ```C
    // This is a Nexsys2-legal comment, just like in C
    ```
    """
    pattern = r"//[^\n]*"

    for match in nexsys_findall(pattern, system):
        system = system.replace(match, "")

    return system

def conditionals(system: str, ctx_dict: dict, declared_dict: dict):
    """
    Reformats multiline "if statements" to "if" function calls

    ### Example: if(i,4.0,0,-i,i) = 0 
    ```
    if [i < 0]
        -i
    else
        i
    end
    ``` 
    """
    def format_eqn_to_expr(eqn: str):
        lhs, rhs = eqn.split("=")
        return f"{lhs} - ({rhs})"

    def is_eqn_not_if_statement_construct(line: str):
        return "=" in line and not (
                "<" in line or 
                ">" in line or 
                "[" in line or 
                "]" in line)

    # pattern = r"if *\[.*([<>=]{2}).*\].* +else +.* +end"
    pattern = r"if ?\[ ?.* ?([<>=]{1,2}) ?.* ?\] ?.* ?else ?.*"
    for original, operator in nexsys_findall(pattern, system):
        whole = copy(original)

        operator_code = {
            "==": ",1.0,",
            "<=": ",2.0,",
            ">=": ",3.0,",
             "<": ",4.0,",
             ">": ",5.0,",
            "!=": ",6.0,",
        }[operator]
 
        for line in whole.split("\n"):
            if is_eqn_not_if_statement_construct(line):
                whole = whole.replace(line, format_eqn_to_expr(line))

        # Remove whitespace and format args to if function call
        formatted = whole                       \
            .replace(" ",       "")             \
            .replace("\t",      "")             \
            .replace("\n",      "")             \
            .replace("[",       "(")            \
            .replace(operator,  operator_code)  \
            .replace("]",       ",")            \
            .replace("else",    ",")            \
            .replace("end",     ") = 0")

        system = system.replace(original, formatted)

    return system

def const_values(system: str, ctx_dict: dict, declared_dict: dict):
    """
    Adds custom constants to the ctx dict.

    ### Example: specifies a constant 'G' with a value of 87
    ```
    const G = 87
    ```
    """
    pattern = r"const +(@V) *= *(@N)"
    for whole, const, val in nexsys_findall(pattern, system):
        ctx_dict[const] = float(val)
        system = system.replace(whole, "")

    return system

def domains(system: str, ctx_dict: dict, declared_dict: dict):
    """
    Adds domain specifications to the declared dict.

    ### Example: specifies a domain of 0.0 < 'x' < 7.0
    ```
    keep x on [0, 7]
    ```
    """
    pattern = r"keep +(@V) +on +\[ *(@N), *(@N) *\]"
    for whole, var, min_val, max_val in nexsys_findall(pattern, system):
        if var in declared_dict:
            declared_dict[var].min_val = float(min_val)
            declared_dict[var].max_val = float(max_val)
        else:
            declared_dict[var] = DeclaredVariable(min_val = float(min_val), max_val = float(max_val))
        system = system.replace(whole, "")

    return system

def guess_values(system: str, ctx_dict: dict, declared_dict: dict):
    """
    Adds guess values to the declared dict.

    ### Example: specifies a guess value of 3.0 for 'x'
    ```
    guess 3 for x
    ```
    """
    pattern = r"guess +(@N) +for +(@V)"
    for whole, val, var in nexsys_findall(pattern, system):
        if var in declared_dict:
            declared_dict[var].guess = float(val)
        else:
            declared_dict[var] = DeclaredVariable(guess = float(val))
        system = system.replace(whole, "")

    return system
