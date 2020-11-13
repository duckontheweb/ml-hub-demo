from typing import List, Generator
import itertools as it

import satstac

from .connection import get, paginate


class Collection(satstac.Collection):
    path = 'collections'

    @classmethod
    def from_mlhub(cls, collection_id):
        """Creates a :class:`Collection` instance by fetching collection details from ML Hub using the given ``collection_id``.

        Parameters
        ----------
        collection_id : str
            The ID of the collection to fetch.

        Returns
        -------
        collection : Collection

        Examples
        --------
        >>> from ml_hub_demo.collection import Collection
        >>> collection_id = 'ref_african_crops_uganda_01'
        >>> collection = Collection.from_mlhub(collection_id)
        >>> print(collection.description)
        African Crops Uganda
        """
        return cls(data=get(f'{cls.path}/{collection_id}'))

    @classmethod
    def list(cls) -> List['Collection']:
        """List all collections.

        Returns
        -------
        List[dict]
            List of all collections found as dictionaries

        Examples
        --------
        >>> from ml_hub_demo.collection import Collection
        >>> collections = Collection.list()
        >>> print(collections[0])
        microsoft_chesapeake_nlcd
        >>> print(type(collections[0]))
        <class 'ml_hub_demo.collection.Collection'>
        """
        return [cls(data=c) for c in get(cls.path)['collections']]

    def items(self, limit: int = None) -> Generator[satstac.Item, None, str]:
        """Yields items associated with this collection up to the given limit (if provided).

        Parameters
        ----------
        limit : int, optional
            The maximum number of items to return.

        Yields
        -------
        item : satstac.Item

        Examples
        --------
        >>> from pprint import pprint
        >>> from ml_hub_demo.collection import Collection
        >>> collection = Collection.from_mlhub()
        >>> first_item = next(collection.items())
        >>> pprint(first_item.properties)
        {'datetime': '2018-12-31T00:00:00Z',
         'label:description': 'Uganda Tile 016 Labels',
         'label:methods': ['manual'],
         'label:properties': None,
         'label:tasks': ['classification'],
         'label:type': 'vector'}
        """
        items_link = next((link for link in self.links(rel='items')), None)
        if not items_link:
            return 'No link found with "rel" type "items"'

        for item in it.islice(paginate(items_link), None, limit):
            yield satstac.Item(data=item)
