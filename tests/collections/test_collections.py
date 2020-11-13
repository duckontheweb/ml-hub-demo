from satstac.item import Item

from ml_hub_demo.collection import Collection

from tests.helpers import use_cassette


class TestCollections:
    @use_cassette('cassettes/test_list_collections.yml')
    def test_list_collections(self):
        collections = Collection.list()
        assert type(collections[0]) is Collection

    @use_cassette('cassettes/test_from_mlhub.yml')
    def test_from_mlhub(self):
        collection_id = 'ref_african_crops_uganda_01'
        collection = Collection.from_mlhub(collection_id)

        assert type(collection) is Collection
        assert collection.description == 'African Crops Uganda'

    @use_cassette('cassettes/test_items.yml')
    def test_items(self):
        collection = Collection.from_mlhub('ref_african_crops_uganda_01')
        first_item = next(collection.items(limit=1))

        assert type(first_item) is Item
        assert first_item.properties['label:description'] == 'Uganda Tile 016 Labels'
