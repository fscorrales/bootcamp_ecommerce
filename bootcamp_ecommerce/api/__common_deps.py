__all__ = ["QueryParamsDependency", "QueryParams"]

from dataclasses import dataclass
from typing import Annotated, Literal

from fastapi import Depends
from pymongo.collection import Collection
from .config.__base_config import logger


@dataclass
class QueryParams:
    filter: str = ""
    limit: int = 0
    offset: int = 0
    sort_by: str = "_id"
    sort_dir: Literal["asc", "desc"] = "asc"

    def format_value(self, v):
        return (int(v)
        if v.strip().isdigit()
        else float(v) if v.strip().isdecimal() else v.strip())

    def query_collection(self, collection: Collection):
        # filter_dict = (
        #     {
        #         k.strip(): (
        #             int(v)
        #             if v.strip().isdigit()
        #             else float(v) if v.strip().isdecimal() else v.strip()
        #         )
        #         for k, v in map(lambda x: x.split("="), self.filter.split(","))
        #     }
        #     if self.filter
        #     else {}
        # )

        filter_dict = {}
        filter_list = self.filter.split(",")

        for f in filter_list:
            if ">=" in f: #No funciona
                k, v = f.split(">=")
                filter_dict.update({k.strip(): {"$gte":self.format_value(v)}})
            elif ">" in f:
                k, v = f.split(">")
                filter_dict.update({k.strip(): {"$gt":self.format_value(v)}})
            elif "<=" in f: #No funciona
                k, v = f.split("<=")
                filter_dict.update({k.strip(): {"$lte":self.format_value(v)}})
            elif "<" in f:
                k, v = f.split("<")
                filter_dict.update({k.strip(): {"$lt":self.format_value(v)}})
            if "=" in f:
                k, v = f.split("=")
                filter_dict.update({k.strip(): self.format_value(v)})
            else:
                pass

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
