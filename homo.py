from typing import Iterator, Iterable
from argparse import ArgumentParser
from operator import add, sub, mul
from fractions import Fraction
from time import perf_counter
from itertools import count
from enum import IntEnum


def div(a: Fraction, b: Fraction) -> Fraction:
    if b == 0:
        return float('nan')
    return a / b


def cons(a: Fraction, b: Fraction) -> Fraction:
    return a * 10 + b


class Op(IntEnum):
    ADD = 0
    SUB = 1
    MUL = 2
    DIV = 3
    CONS = 4
    PUSH = 5

    def __str__(self) -> str:
        return ['+', '-', '*', '/', '', ''][self]

    def __call__(self, a: Fraction, b: Fraction) -> Fraction | float:
        return [add, sub, mul, div, cons][self](a, b)

    def precedence(self) -> int:
        return [1, 1, 2, 2, 3, 4][self]


def compute(source: list[int], op_stack: Iterable[Op]) -> Fraction:
    source = source.copy()
    compute_stack = []
    for op in op_stack:
        if op == Op.PUSH:
            compute_stack.append(source.pop())
        else:
            x = compute_stack.pop()
            y = compute_stack.pop()
            compute_stack.append(op(x, y))
    return compute_stack[0]


def to_infix(source: list[int], op_stack: list[Op]) -> str:
    source = source.copy()
    compute_stack = []
    for op in op_stack:
        if op == Op.PUSH:
            compute_stack.append((str(source.pop()), 4))
        else:
            content1, pr1 = compute_stack.pop()
            content2, pr2 = compute_stack.pop()
            current_precedence = op.precedence()
            symbol = str(op)
            match pr1 < current_precedence, (pr2 < current_precedence or 
                                             op in (Op.SUB, Op.DIV) and
                                             pr2 == current_precedence):
                case False, False:
                    formatter = '{}{}{}'
                case True, False:
                    formatter = '({}){}{}'
                case False, True:
                    formatter = '{}{}({})'
                case True, True:
                    formatter = '({}){}({})'
            compute_stack.append(
                (formatter.format(content1, symbol, content2), current_precedence))
    return compute_stack.pop()[0]


def prove_all(source: list[int], target: int) -> Iterator[list[Op]]:
    length = len(source) * 2 - 1
    op_stack = []
    def loop(a: int, b: int):
        if a + b == length:
            result = compute(source, (op_stack))
            if result == target:
                yield op_stack
        else:
            if a <= length // 2:
                op_stack.append(Op.PUSH)
                yield from loop(a + 1, b)
                op_stack.pop()
            if a > b + 1:
                for op in [Op.ADD, Op.SUB, Op.MUL, Op.DIV]:
                    op_stack.append(op)
                    yield from loop(a, b + 1)
                    op_stack.pop()
            for i in count():
                if a + 1 + i > length // 2 or a < b - 2:
                    break
                op_stack.extend([Op.PUSH] * (i + 2))
                op_stack.extend([Op.CONS] * (i + 1))
                yield from loop(a + 2 + i, b + 1 + i)
                op_stack[:] = op_stack[:-2 * i - 3]

    return loop(0, 0)


def prove(source: list[int], target: int) -> list[Op]:
    return next(prove_all(source, target), None)


def get_ints(n: int) -> list[int]:
    ret = []
    while n:
        ret.append(n % 10)
        n //= 10
    ret.reverse()
    return ret


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('target', type=int)
    parser.add_argument('source', type=int, default=114514, nargs='?')
    parser.add_argument('-d', '--digest', action='store_true')
    args = parser.parse_args()

    source = get_ints(args.source)
    past = perf_counter()
    if args.digest:
        match prove(source, args.target):
            case None:
                print('No result found')
            case data:
                now = perf_counter()
                print(args.target, '=', to_infix(source, data))
    else:
        count = 0
        exprs = set(to_infix(source, data) for data in prove_all(source, args.target))
        now = perf_counter()
        for expr in exprs:
            print(args.target, '=', expr)
            count += 1
        print(count, 'results found')
    print('Fixed within', now - past, 'seconds')


if __name__ == '__main__':
    main()
