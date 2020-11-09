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
        """
        return cls(data=get(f'{cls.path}/{collection_id}'))

    @classmethod
    def list(cls) -> List[dict]:
        """List all collections.

        Returns
        -------
        List[dict]
            List of all collections found as dictionaries
        """
        return get(cls.path)['collections']

    def items(self, limit: int = None) -> Generator[satstac.Item, None, str]:
        """Yields items associated with this collection up to the given limit (if provided).

        Parameters
        ----------
        limit : int, optional
            The maximum number of items to return.

        Yields
        -------
        item : satstac.Item
        """
        items_link = next((link for link in self.links(rel='items')), None)
        if not items_link:
            return 'No link found with "rel" type "items"'

        for item in it.islice(paginate(items_link), None, limit):
            yield satstac.Item(data=item)
