__all__ = ["QueryParamsDependency", "QueryParams"]

from dataclasses import dataclass
from typing import Annotated, Literal
from bson import ObjectId
from fastapi import Depends
from pymongo.collection import Collection

op_map = {
    # Primero los que tienen mas catacteres
    ">=": "$gte",
    "<=": "$lte",
    "!=": "$ne",
    # luego los demás
    ">": "$gt",
    "<": "$lt",
    "=": "$eq",
    "~": "$regex",
}


def format_value(v):
    return (
        int(v)
        if v.strip().isdigit()
        else (
            float(v)
            if v.strip().isdecimal()
            else ObjectId(v.strip()) if len(v.strip()) == 24 else v.strip()
        )
    )


def get_filter_query(f):
    op = ""
    for o in op_map:
        if o in f:
            op = o
            break
    if not op:
        return {}

    k, v = f.split(op)
    return {k.strip(): {op_map[op]: format_value(v)}}


@dataclass
class QueryParams:
    filter: str = ""
    limit: int = 0
    offset: int = 0
    sort_by: str = "_id"
    sort_dir: Literal["asc", "desc"] = "asc"

    @property
    def filter_dict(self):
        filter_dict = {}
        filter_item_list = self.filter.split(",")

        for filter_item in filter_item_list:
            filter_dict.update(get_filter_query(filter_item))

        return filter_dict

    def query_collection(
        self,
        collection: Collection,
        *,
        get_deleted: bool | None = False,
        extra_filter: dict | None = None,
    ):
        """Este método consulta los datos de una colección aplicando los filtros

        Args:
            collection (Collection): es la colección de pymongo
            get_deleted (bool | None, optional): es para obtener los datos eliminados.
            Defaults to False.
                True: Obtiene los datos eliminados
                False: Obtiene los datos no eliminados
                None: Obtiene todos los datos
        """
        filter_dict = self.filter_dict

        if get_deleted is not None:
            filter_dict.update(
                deactivated_at={"$ne": None} if get_deleted else {"$eq": None}
            )

        if extra_filter:
            filter_dict.update(extra_filter)

        # WARNING: Note this return statement with parenthesis
        #          This is only to split the expression into more lines
        #          BUT BE CAUTIOUS, if you add a comma before de closing parenthesis
        #          it will become into a tuple and we don't want that.
        return (
            collection.find(filter_dict)
            .limit(self.limit)
            .skip(self.offset)
            .sort(self.sort_by, 1 if self.sort_dir == "asc" else -1)
        )


QueryParamsDependency = Annotated[QueryParams, Depends()]
