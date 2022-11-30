projects = {
    'green':[{
        'tables':
            ['study_area',
             'grid_visualization',
             'grid_calculation',
            ],
        'raw_db_schema': 'basic'
    },
             {
            'tables':
            ['sub_study_area'
            ],
        'raw_db_schema': 'public'
             }]
}

def get_schema(table_name):
    for key, project in projects.items():
        for part in project:
            for table in part['tables']:
                if table_name == table:
                    return part['raw_db_schema']