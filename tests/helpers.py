from functools import partial

import vcr

use_cassette = partial(vcr.use_cassette, filter_headers=['authorization'])
