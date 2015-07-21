PageMapping = {
    'properties': {
        'id': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'uuid': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'primary_category': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'source': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'language': {
            'index': 'not_analyzed',
            'type': 'string'
        },
        'slug': {
            'type': 'string',
            'index': 'not_analyzed',
        }
    }
}

CategoryMapping = {
    'properties': {
        'id': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'uuid': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'source': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'language': {
            'index': 'not_analyzed',
            'type': 'string'
        },
        'slug': {
            'type': 'string',
            'index': 'not_analyzed',
        }
    }
}

LocalisationMapping = {
    'properties': {
        'locale': {
            'type': 'string',
            'index': 'not_analyzed',
        }
    }
}
