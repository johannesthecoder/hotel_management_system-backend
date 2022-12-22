from types import NoneType
from typing import Type, TypeVar

from pydantic import BaseModel


Model = TypeVar("Model", bound=BaseModel)


def dict_to_model(model: Type[Model], dict_model: dict) -> Model:
    populated_keys = dict_model.keys()
    required_keys = set(model.schema()['required'])
    missing_keys = required_keys.difference(populated_keys)

    if missing_keys:
        raise ValueError(f'required keys missing: {missing_keys}')

    all_definition_keys = model.schema()['properties'].keys()

    return model(**{k: v if not k == "_id" else str(v) for k, v in dict_model.items() if k in all_definition_keys})


def model_to_dict_without_None(model) -> dict:
    return {k: v for k, v in model.dict().items() if type(v) != NoneType}


def str_to_match_all_regex(s: str):
    return f'.*{"".join([f"{v}.*" for v in s])}'
