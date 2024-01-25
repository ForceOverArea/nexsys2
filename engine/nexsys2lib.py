"""
Contains code for solving equations with Nexsys2 as well as extending its functionality.
"""
from dataclasses import dataclass
from re import findall, DOTALL, IGNORECASE
from engine.geqslib import create_context_with, solve_equation, SystemBuilder, WILL_CONSTRAIN, WILL_OVERCONSTRAIN

_SUCCESS = True

LEGAL_VAR_PATTERN = r"[a-z][a-z0-9_]*"
"""
Regex pattern for a legal variable in Nexsys
"""

# TODO: make the decimal point and afterwards optional AS A GROUP.
LEGAL_NUM_PATTERN = r"-? ?[0-9]+\.?[0-9]*"
"""
Regex pattern for a legal number literal in Nexsys
"""

@dataclass
class DeclaredVariable:
    guess:   float = 1.0
    min_val: float = float("-inf")
    max_val: float = float("inf")

def nexsys_findall(pattern: str, string: str):
    """
    Same as `re.findall`, but replaces `"@V"` and `"@N"` in the 
    given pattern with Nexsys-legal variable and number patterns, 
    respectively. Also sets only the IGNORECASE flag
    """
    nexsys_pattern = "(" + pattern \
        .replace("@V", LEGAL_VAR_PATTERN) \
        .replace("@N", LEGAL_NUM_PATTERN) + ")"
    
    return findall(nexsys_pattern, string, IGNORECASE | DOTALL)

def _try_solve_single_unknown_equation(eqn_pool: list, ctx_dict: dict, declared_dict: dict):
    """
    Tries to solve ONE single-unknown equation in the given pool. This function will 
    iterate through the given pool until it finds a solvable equation, updating the 
    equation pool and caller context if it can find a solution.
    """
    for i, eqn in enumerate(eqn_pool): 

        unknowns = [var for var in nexsys_findall("@V", eqn) if var not in ctx_dict]
        if len(unknowns) != 1:
            return False
        
        var_info = DeclaredVariable()
        if unknowns[0] in declared_dict:
            var_info = declared_dict[unknowns[0]]

        # Try to solve equation...
        maybe_soln = solve_equation(eqn, 
            create_context_with(ctx_dict),
            guess = var_info.guess,
            soln_min = var_info.min_val,
            soln_max = var_info.max_val)

        # ...if successful
        if maybe_soln != None:
            ctx_dict.update(maybe_soln.soln_dict)   # ...add information to caller's context
            eqn_pool.pop(i)                         # ...remove equation from pool
            return True                             # ...alert caller of success and exit
        
    # If no equations are solvable, indicate failure.
    return False

def _try_solve_subsystem_of_equations(eqn_pool: list, ctx_dict: dict, declared_dict: dict):
    """
    Tries to identify and solve a constrained system of equations within `eqn_pool`. 
    This function will iterate through the given pool until it finds a solvable system, 
    updating the equation pool and caller context if it can find a solution.
    """
    for eqn in eqn_pool:
        builder = SystemBuilder(eqn, create_context_with(ctx_dict))
        sub_pool = [x for x in eqn_pool if x != eqn]
        still_learning = True

        # Identify if a constrained subsystem exists
        while still_learning:
            still_learning = False

            for i in range(len(sub_pool)):
                constraint_status = builder.try_constrain_with(sub_pool[i])

                if WILL_CONSTRAIN == constraint_status:
                    sub_pool.pop(i)
                    still_learning = True
                    break

                elif WILL_OVERCONSTRAIN == constraint_status:
                    break
        
        # Add declared domains and guesses, and solve
        if builder.is_fully_constrained():
            system = builder.build_system()

            for var in declared_dict:
                system.specify_variable(var, 
                    guess = declared_dict[var].guess, 
                    min = declared_dict[var].min_val, 
                    max = declared_dict[var].max_val)

            maybe_soln = system.solve_system()

            if maybe_soln != None:
                ctx_dict.update(maybe_soln.soln_dict)
                eqn_pool.clear()
                eqn_pool.extend(sub_pool)

            return True
        
        # ...or just abort if no constrained system exists 
        else:
            return False

def nexsys2(system: str, preprocessors: list = []):
    """
    The process for solving a system of equations in Nexsys2. This function automatically 
    calls any preprocessors scheduled with the `NexsysPreProcessorScheduler` prior to solving.
    """
    ctx_dict = {}
    declared_dict = {}

    # Run preprocessors in order, mutating system and context along the way
    for pp in preprocessors:
        system = pp(system, ctx_dict, declared_dict)
    
    print(system)

    # Split plain text into lines with 1 equation each
    equations = [line for line in system.split("\n") if "=" in line]

    # NOTE: Using if-else to support pre-3.11 syntax. A match may be better here in the future.
    while True:

        if _SUCCESS == _try_solve_single_unknown_equation(equations, ctx_dict, declared_dict):
            continue

        elif _SUCCESS == _try_solve_subsystem_of_equations(equations, ctx_dict, declared_dict):
            continue

        else:
            break

    if len(equations) != 0:
        raise Exception
    
    return ctx_dict
