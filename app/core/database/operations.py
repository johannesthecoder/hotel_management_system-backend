from bson.objectid import ObjectId

from .check import exist
from .connection import db


def create_one(collection_name: str, new_document: dict) -> str:
    """create/insert a single document
    >>> # request
    >>> create_one(
            collection_name="programming_languages",
            new_document={
                "language": "python",
                "framework": ["flask", "django", "fastapi"],
                "rank": 2,
                "is_dying": False,
            },
        )
    >>> # response
    >>> "54f112defba522406c9cc208"

    Args:
        `collection_name` (str): collection name
        `new_document` (dict): document you want to insert

    Returns:
        str: inserted id
    """
    result = db[collection_name].insert_one(new_document)

    if result.inserted_id:
        return str(result.inserted_id)


def create_many(collection_name: str, new_documents: dict) -> list[str]:
    """ it is yet to be implemented """
    pass


def get_one(collection_name: str, id: str, projection: dict = {}) -> dict:
    """get a single document
    >>> # request
    >>> get_one(
            collection_name="programming_languages",
            id="54f112defba522406c9cc208",
            projection={
                "framework": 0,
                "rank": 0,
            },
        )
    >>> # response
    >>> {
            "language": "python",
            "is_dying": False,
            # document fields according to the {projection}
            # example in this case, all filed except ["framework", "rank"]
        }

    Args:
        `collection_name` (str): collection name
        `id` (str): id of the document
        `projection` (dict, optional): fields of the document with values of 0[unwanted] & 1[wanted]. By default every field is wanted. Defaults to {}.

    Returns:
        dict: the document with the specified patter/shape {projection}
    """
    ObjectId.is_valid(id)

    result = db[collection_name].find_one(
        filter={"_id": ObjectId(id)},
        projection=projection,
    )

    return dict(result) if result else None


def get_many(collection_name: str, filter: dict = {}, projection: dict = {}, limit: int = 101, skip: int = 0) -> list[dict]:
    """get a list of documents
    >>> # request
    >>> get_many(
            collection_name="programming_languages",
            filter={"is_dying": False} 
            projection={
                "framework": 0,
                "rank": 0,
            },
        )
    >>> # response
    >>> [
            {
                "language": "python",
                "is_dying": False,
                # document fields according to the {projection}
                # example in this case, all filed except ["framework", "rank"]
            },
        ]

    Args:
        `collection_name` (str): collection name
        `filter` (dict, optional): Defaults to {}.
        `projection` (dict, optional): fields of the document with values of 0[unwanted] & 1[wanted]. By default every field is wanted. Defaults to {}.
        `limit` (int, optional): how many do you want to get. Defaults to 101.
        `skip` (int, optional): how many documents to skip. Defaults to 0.

    Returns:
        list[dict]: list of documents according to the projection structure
    """
    result = db[collection_name].find(
        filter=filter, projection=projection, limit=limit, skip=skip,
    )

    return list(result)


def update_one(collection_name: str, id: str, updated_document: dict, operation: str = "set") -> bool:
    """update one document where _id={id}
    >>> # request
    >>> update_one(
            collection_name="programming_languages",
            id="54f112defba522406c9cc208",
            updated_document={
                "rank": 1,
            }
        )

    >>> # response
    >>> True

    Args:
        `collection_name` (str): collection name
        `id` (str): id of the targeted document
        `updated_document` (dict): a document containing only the updated fields

    Returns:
        bool: True if successful else False
    """
    ObjectId.is_valid(id)
    exist(collection_name=collection_name, filter={"_id": ObjectId(id)})

    update = {}

    match operation:
        case "push":
            update["$push"] = {}
            for k, v in updated_document.items():
                if type(v) == list:
                    update["$push"][k] = {"$each": v}
                else:
                    update["$push"][k] = v
        case "pull":
            update["$pull"] = {}
            for k, v in updated_document.items():
                if type(v) == list:
                    update["$pull"][k] = {"$in": v}
                else:
                    update["$pull"][k] = v
        case _:
            update["$set"] = updated_document

    result = db[collection_name].update_one(
        filter={"_id": ObjectId(id)},
        update=update,
    )
    print()
    print("###################")
    print(result.modified_count)
    print(result.matched_count)
    if result.modified_count:
        return True

    return False


def update_many(collection_name: str, ids: list[str], updated_document: dict) -> list[bool]:
    """ it is yet to be implemented """
    pass


def delete_one(collection_name: str, id: str) -> bool:
    """delete one document where _id={id}
    >>> # request
    >>> delete_one(
            collection_name="programming_languages",
            id="54f112defba522406c9cc208",
        )

    >>> # response
    >>> True

    Args:
        `collection_name` (str): collection name
        `id` (str): id of the targeted document

    Returns:
        bool: True if successful else False
    """
    ObjectId.is_valid(id)
    exist(collection_name=collection_name, filter={"_id": ObjectId(id)})

    result = db[collection_name].delete_one(filter={"_id": ObjectId(id)})

    if result.deleted_count:
        return True


def delete_many(collection_name: str, ids: list[str], updated_document: dict) -> list[bool]:
    """ it is yet to be implemented """
    pass
