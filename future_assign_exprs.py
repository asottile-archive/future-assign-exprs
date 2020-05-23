import dis
import re
import struct
import types


def op(name):
    return struct.pack('<B', dis.opmap[name])


def arg_i(n):
    return struct.pack('<B', n)


def un_arg_i(bts):
    return struct.unpack('<B', bts)[0]


def ASSIGN(name, expr):
    raise AssertionError('Unreachable {} = ...'.format(name))


def future_assign_exprs(fn):
    code = fn.__code__

    try:
        assign_index = code.co_names.index(ASSIGN.__name__)
    except ValueError:  # no ASSIGN, return original
        return fn

    varnames = list(code.co_varnames)

    def replace_assign_callback(match):
        varname = code.co_consts[un_arg_i(match.group(1))]
        try:
            var_index = code.co_varnames.index(varname)
        except ValueError:
            var_index = len(varnames)
            varnames.append(varname)

        return (
            # pad with nop as we lost 3 instructions and added 2
            op('NOP') + arg_i(0) +
            match.group(2) +
            op('DUP_TOP') + arg_i(0) +
            op('STORE_FAST') + arg_i(var_index)
        )

    assign_reg = re.compile(
        op('LOAD_GLOBAL') + arg_i(assign_index) +
        op('LOAD_CONST') + b'(.)' +
        b'(.*?)' +
        op('CALL_FUNCTION') + arg_i(2)
    )
    new_co_code = assign_reg.sub(replace_assign_callback, code.co_code)

    def replace_load_callback(match):
        name = code.co_names[un_arg_i(match.group(1))]
        try:
            name_index = varnames.index(name)
        except ValueError:
            return match.group()
        else:
            return op('LOAD_FAST') + arg_i(name_index)

    load_reg = re.compile(op('LOAD_GLOBAL') + b'(.)')
    new_co_code = load_reg.sub(replace_load_callback, new_co_code)

    new_code = types.CodeType(
        code.co_argcount,
        code.co_kwonlyargcount,
        len(varnames),
        code.co_stacksize,
        code.co_flags,
        new_co_code,
        code.co_consts,
        code.co_names,
        tuple(varnames),
        code.co_filename,
        code.co_name,
        code.co_firstlineno,
        code.co_lnotab,
        code.co_freevars,
        code.co_cellvars,
    )

    return types.FunctionType(
        new_code,
        fn.__globals__,
        fn.__name__,
        fn.__defaults__,
        fn.__closure__,
    )
