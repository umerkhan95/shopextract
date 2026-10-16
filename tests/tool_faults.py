"""Surgical test-only source mutations. Never imported by production."""
import ast
import inspect
import textwrap


def without_post_operation_cancel_check(run):
    """Remove exactly one real publication guard; keep scheduler/dispatcher intact."""
    tree=ast.parse(textwrap.dedent(inspect.getsource(run)))
    changed=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.AsyncFunctionDef) and node.name=='work':
            for block in ast.walk(node):
                if isinstance(block,ast.AsyncWith):
                    for index,statement in enumerate(block.body[:-1]):
                        if (isinstance(statement,ast.Assign)
                            and any(isinstance(t,ast.Name) and t.id=='graph' for t in statement.targets)
                            and isinstance(statement.value,ast.Await)):
                            guard=block.body[index+1]
                            assert isinstance(guard,ast.If)
                            assert ast.unparse(guard.test)=='ctx.cancelled.is_set()'
                            del block.body[index+1];changed.append(True)
    assert changed==[True], 'Negative control must alter exactly the reviewed guard'
    namespace={}
    exec(compile(ast.fix_missing_locations(tree),'<test-only-publication-guard-fault>','exec'),run.__globals__,namespace)
    return namespace['run']
