import os
import json
from aws import upload_optimized_files

optimized_files_dir = 'C:\\Users\\ninja\\git\\viewer\\Aligneur_server_V2\\files\patient1\\Setup_1\\'
strDataJson = """
{
    "upper": [
        "Tooth17.obj",
        "Tooth16.obj",
        "Tooth15.obj",
        "Tooth14.obj",
        "Tooth13.obj",
        "Tooth12.obj",
        "Tooth11.obj",
        "Tooth21.obj",
        "Tooth22.obj",
        "Tooth23.obj",
        "Tooth24.obj",
        "Tooth25.obj",
        "Tooth26.obj",
        "Tooth27.obj"
    ],
    "lower": [
        "Tooth37.obj",
        "Tooth36.obj",
        "Tooth35.obj",
        "Tooth34.obj",
        "Tooth33.obj",
        "Tooth32.obj",
        "Tooth31.obj",
        "Tooth41.obj",
        "Tooth42.obj",
        "Tooth43.obj",
        "Tooth44.obj",
        "Tooth45.obj",
        "Tooth46.obj",
        "Tooth47.obj"
    ],
    "attach": [
        "16.obj",
        "14.obj",
        "13.obj",
        "12.obj",
        "22.obj",
        "23.obj",
        "24.obj",
        "26.obj",
        "36.obj",
        "34.obj",
        "33.obj",
        "43.obj",
        "44.obj",
        "46.obj"
    ],
    "quadrant": [
        7,
        7,
        7,
        7
    ],
    "stages": [
        {
            "step": 1,
            "path": "/0/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        },
        {
            "step": 2,
            "path": "/1/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        },
        {
            "step": 3,
            "path": "/2/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        },
        {
            "step": 4,
            "path": "/3/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        },
        {
            "step": 5,
            "path": "/4/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        },
        {
            "step": 6,
            "path": "/5/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        },
        {
            "step": 7,
            "path": "/6/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        },
        {
            "step": 8,
            "path": "/7/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        },
        {
            "step": 9,
            "path": "/8/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        },
        {
            "step": 10,
            "path": "/9/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        },
        {
            "step": 11,
            "path": "/10/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        },
        {
            "step": 12,
            "path": "/11/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        },
        {
            "step": 13,
            "path": "/12/",
            "maxilla": "Maxilla.obj",
            "mandible": "Mandible.obj",
            "maxillaMatrix": {},
            "mandibleMatrix": {},
            "upperMatrices": [],
            "lowerMatrices": [],
            "upperIPR": [],
            "lowerIPR": []
        }
    ],
    "fake": [],
    "steps": 13,
    "movData": {
        "17": [
            {
                "active": false,
                "percent": 100.0
            }
        ],
        "16": [
            {
                "active": false,
                "percent": 100.0
            }
        ],
        "15": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "14": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "13": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "12": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "11": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "21": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "22": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "23": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "24": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "25": [
            {
                "active": false,
                "percent": 100.0
            }
        ],
        "26": [
            {
                "active": false,
                "percent": 100.0
            }
        ],
        "27": [
            {
                "active": false,
                "percent": 100.0
            }
        ],
        "37": [
            {
                "active": false,
                "percent": 100.0
            }
        ],
        "36": [
            {
                "active": false,
                "percent": 100.0
            }
        ],
        "35": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "34": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "33": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "32": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "31": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "41": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "42": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "43": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "44": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "45": [
            {
                "active": true,
                "percent": 100.0
            }
        ],
        "46": [
            {
                "active": false,
                "percent": 100.0
            }
        ],
        "47": [
            {
                "active": false,
                "percent": 100.0
            }
        ]
    },
    "attachmentData": {
        "16": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 4 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "14": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 3 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "13": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 4 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "12": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 3 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "22": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 3 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "23": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 4 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "24": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 3 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "26": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 4 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "36": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 4 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "34": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 3 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "33": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 4 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "43": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 4 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "44": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 3 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        },
        "46": {
            "0": {
                "new": [
                    {
                        "type": "Box 2 x 4 mm"
                    }
                ],
                "lost": []
            },
            "1": {
                "new": [],
                "lost": []
            },
            "2": {
                "new": [],
                "lost": []
            },
            "3": {
                "new": [],
                "lost": []
            },
            "4": {
                "new": [],
                "lost": []
            },
            "5": {
                "new": [],
                "lost": []
            },
            "6": {
                "new": [],
                "lost": []
            },
            "7": {
                "new": [],
                "lost": []
            },
            "8": {
                "new": [],
                "lost": []
            },
            "9": {
                "new": [],
                "lost": []
            },
            "10": {
                "new": [],
                "lost": []
            },
            "11": {
                "new": [],
                "lost": []
            },
            "12": {
                "new": [],
                "lost": []
            }
        }
    },
    "landmarks": {
        "17": {
            "Distal point": [
                -28.39702,
                2.40807,
                -21.36313
            ],
            "Distal Buccal": [
                -30.48865,
                1.2623,
                -18.76044
            ],
            "Vestibular Gingival": [
                -27.95608,
                6.80182,
                -17.3871
            ],
            "Apical Rotation": [
                -23.58179,
                16.11165,
                -19.51709
            ],
            "Mesial Buccal": [
                -30.42516,
                0.13447,
                -14.68146
            ],
            "Mesial Point": [
                -26.11029,
                2.64138,
                -13.11229
            ],
            "mdAxis": [
                0.26698412582696385,
                0.02723979936270957,
                0.9633158723321708
            ],
            "mdCenter": [
                -27.253655000000002,
                2.524725,
                -17.23771
            ],
            "toothAxis": [
                0.2575351418207586,
                0.9529518805247497,
                -0.15986983496490217
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                0.9636734647474147,
                0.0,
                -0.2670832329849879
            ],
            "attachPoint": [
                -27.95608,
                2.524725,
                -17.3871
            ],
            "mdToothPerpendicular": [
                -0.9239739013062704,
                0.29128280755187874,
                0.24784381317589005
            ]
        },
        "16": {
            "Distal point": [
                -26.28018,
                1.55463,
                -12.56871
            ],
            "Distal Buccal": [
                -28.26527,
                -1.04897,
                -8.9199
            ],
            "Vestibular Gingival": [
                -29.57482,
                5.39432,
                -6.48705
            ],
            "Apical Rotation": [
                -23.06646,
                20.1218,
                -10.55532
            ],
            "Mesial Buccal": [
                -27.52212,
                -0.3016,
                -3.40739
            ],
            "Mesial Point": [
                -25.48337,
                2.32573,
                -1.86996
            ],
            "mdAxis": [
                0.07408012358196372,
                0.07168984236399165,
                0.9946721579454746
            ],
            "mdCenter": [
                -25.881775,
                1.94018,
                -7.219335
            ],
            "toothAxis": [
                0.1505653614943479,
                0.9723679900305522,
                -0.178411221289526
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                0.997238078429764,
                0.0,
                -0.07427122544910583
            ],
            "attachPoint": [
                -29.57482,
                1.94018,
                -6.48705
            ],
            "mdToothPerpendicular": [
                -0.9845820458156812,
                0.16374565634101124,
                0.061526864757269754
            ]
        },
        "15": {
            "Distal point": [
                -25.01687,
                2.32748,
                -1.60404
            ],
            "Vestibular Gingival": [
                -25.04439,
                6.10343,
                1.96041
            ],
            "Buccal Cusp": [
                -24.62837,
                -0.79804,
                2.3886
            ],
            "Apical Rotation": [
                -22.22724,
                16.35231,
                -0.76064
            ],
            "Mesial Point": [
                -22.02687,
                2.73032,
                4.16474
            ],
            "mdAxis": [
                0.4592874193578574,
                0.06187937926893614,
                0.8861297923221466
            ],
            "mdCenter": [
                -23.52187,
                2.5289,
                1.28035
            ],
            "toothAxis": [
                0.09225534181444263,
                0.9850562821741987,
                -0.14544096003480458
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                0.8878312009765156,
                0.0,
                -0.46016927165185423
            ],
            "attachPoint": [
                -25.04439,
                2.5289,
                1.96041
            ],
            "mdToothPerpendicular": [
                -0.8821755769660828,
                0.14859793262780596,
                0.4468611706372585
            ]
        },
        "14": {
            "Distal point": [
                -23.38231,
                2.839,
                4.94896
            ],
            "Vestibular Gingival": [
                -23.07516,
                6.38886,
                9.16691
            ],
            "Buccal Cusp": [
                -22.84986,
                -0.77581,
                8.8146
            ],
            "Apical Rotation": [
                -18.79752,
                20.32871,
                5.33778
            ],
            "Mesial Point": [
                -19.93225,
                2.32915,
                10.87456
            ],
            "mdAxis": [
                0.5017739835422866,
                -0.07415217866038123,
                0.8618145530449249
            ],
            "mdCenter": [
                -21.65728,
                2.584075,
                7.91176
            ],
            "toothAxis": [
                0.15750202342287964,
                0.9772903731083897,
                -0.14176261583140665
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                0.8641937323820074,
                0.0,
                -0.5031592122893662
            ],
            "attachPoint": [
                -23.07516,
                2.584075,
                9.16691
            ],
            "mdToothPerpendicular": [
                -0.8373458137090559,
                0.208266844816695,
                0.5054472372206793
            ]
        },
        "13": {
            "Distal point": [
                -20.54898,
                2.5097,
                11.83997
            ],
            "Vestibular Gingival": [
                -18.68206,
                8.84599,
                15.09867
            ],
            "Cusp of": [
                -18.8871,
                -0.78477,
                16.74223
            ],
            "Apical Rotation": [
                -11.86164,
                24.12855,
                5.51623
            ],
            "Mesial Point": [
                -15.32514,
                2.83105,
                17.52558
            ],
            "mdAxis": [
                0.675985669649108,
                0.04158396791282671,
                0.7357405439702721
            ],
            "mdCenter": [
                -17.93706,
                2.670375,
                14.682775
            ],
            "toothAxis": [
                0.2519664376688888,
                0.8899368131957313,
                -0.38016494158125114
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                0.7363775011532393,
                0.0,
                -0.6765708948774778
            ],
            "attachPoint": [
                -18.68206,
                2.670375,
                15.09867
            ],
            "mdToothPerpendicular": [
                -0.6723343185517715,
                0.4435309782091879,
                0.592660809794545
            ]
        },
        "12": {
            "Distal point": [
                -14.26057,
                1.47242,
                19.15838
            ],
            "Vestibular Gingival": [
                -12.36233,
                7.5254,
                20.4215
            ],
            "Incisal Edge": [
                -12.16051,
                -0.7731,
                22.66964
            ],
            "Apical Rotation": [
                -9.9137,
                20.08643,
                11.80331
            ],
            "Mesial Point": [
                -9.05688,
                2.3146,
                22.3678
            ],
            "mdAxis": [
                0.8431738736232405,
                0.13646165949317132,
                0.5200346472376138
            ],
            "mdCenter": [
                -11.658725,
                1.89351,
                20.76309
            ],
            "toothAxis": [
                0.08573171456068569,
                0.8938039423305626,
                -0.4401869895769633
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                0.5249453254333595,
                0.0,
                -0.8511359499549201
            ],
            "attachPoint": [
                -12.36233,
                1.89351,
                20.4215
            ],
            "mdToothPerpendicular": [
                -0.5251931441375443,
                0.41598751133626544,
                0.7423789812239979
            ]
        },
        "11": {
            "Distal point": [
                -9.00403,
                1.56739,
                22.45895
            ],
            "Vestibular Gingival": [
                -4.90003,
                7.47772,
                23.96065
            ],
            "Incisal Edge": [
                -4.47739,
                -1.64594,
                25.06529
            ],
            "Apical Rotation": [
                -4.29786,
                20.95277,
                14.23972
            ],
            "Mesial Point": [
                -0.15893,
                2.00454,
                23.94752
            ],
            "mdAxis": [
                0.9849634695896641,
                0.04867969618558542,
                0.16576263376638878
            ],
            "mdCenter": [
                -4.58148,
                1.785965,
                23.203235
            ],
            "toothAxis": [
                0.013402905378167053,
                0.9057572590676933,
                -0.42358487906628955
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                0.16595938844380348,
                0.0,
                -0.9861325881378014
            ],
            "attachPoint": [
                -4.90003,
                1.785965,
                23.96065
            ],
            "mdToothPerpendicular": [
                -0.17077494867091017,
                0.41947235143436257,
                0.8915597923238656
            ]
        },
        "21": {
            "Mesial Point": [
                -0.17185,
                2.33437,
                24.3392
            ],
            "Incisal Edge": [
                4.23818,
                -1.15645,
                25.45779
            ],
            "Vestibular Gingival": [
                4.53031,
                7.87493,
                23.72896
            ],
            "Apical Rotation": [
                3.26627,
                20.99088,
                12.87692
            ],
            "Distal point": [
                8.31117,
                1.86973,
                22.48898
            ],
            "mdAxis": [
                -0.9756346171389173,
                0.053438382616972084,
                0.21279434462287816
            ],
            "mdCenter": [
                4.069660000000001,
                2.1020499999999998,
                23.41409
            ],
            "toothAxis": [
                -0.037118268968753185,
                0.8727027625998005,
                -0.486838907914558
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                -0.21309883113839728,
                -0.0,
                -0.977030648530254
            ],
            "attachPoint": [
                4.53031,
                2.1020499999999998,
                23.72896
            ],
            "mdToothPerpendicular": [
                0.21176767703273555,
                0.48297940552306695,
                0.8496383611894792
            ]
        },
        "22": {
            "Mesial Point": [
                8.6217,
                2.83895,
                22.65706
            ],
            "Incisal Edge": [
                11.58161,
                -0.61397,
                22.05556
            ],
            "Vestibular Gingival": [
                11.57336,
                7.76452,
                20.11627
            ],
            "Apical Rotation": [
                8.3474,
                20.65447,
                12.72997
            ],
            "Distal point": [
                13.35989,
                1.93481,
                18.41916
            ],
            "mdAxis": [
                -0.7379345856666852,
                0.140812457137573,
                0.6600184839773934
            ],
            "mdCenter": [
                10.990795,
                2.38688,
                20.538110000000003
            ],
            "toothAxis": [
                -0.13189644173077947,
                0.9114907609331067,
                -0.389599693778557
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                -0.66666090107683,
                -0.0,
                -0.7453611493601134
            ],
            "attachPoint": [
                11.57336,
                2.38688,
                20.11627
            ],
            "mdToothPerpendicular": [
                0.6567863998344885,
                0.37473870241472074,
                0.6543718590411592
            ]
        },
        "23": {
            "Mesial Point": [
                14.03426,
                3.13943,
                17.71305
            ],
            "Cusp of": [
                16.77865,
                -0.48974,
                17.00745
            ],
            "Vestibular Gingival": [
                16.9345,
                9.04402,
                14.4836
            ],
            "Apical Rotation": [
                10.76001,
                24.25781,
                5.98543
            ],
            "Distal point": [
                18.32294,
                2.38005,
                11.6947
            ],
            "mdAxis": [
                -0.5772893694468014,
                0.10221839852134268,
                0.8101162774117345
            ],
            "mdCenter": [
                16.1786,
                2.75974,
                14.703875
            ],
            "toothAxis": [
                -0.22745122346616262,
                0.9024049288950089,
                -0.3659662351225038
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                -0.8143820258707288,
                -0.0,
                -0.5803291444849962
            ],
            "attachPoint": [
                16.9345,
                2.75974,
                14.4836
            ],
            "mdToothPerpendicular": [
                0.7705131001074367,
                0.3965863721856059,
                0.4990278669167556
            ]
        },
        "24": {
            "Mesial Point": [
                18.21522,
                2.78403,
                10.89326
            ],
            "Apical Rotation": [
                17.59248,
                20.04786,
                2.35951
            ],
            "Buccal Cusp": [
                20.65145,
                -0.76614,
                8.60602
            ],
            "Vestibular Gingival": [
                21.363,
                6.40562,
                8.46111
            ],
            "Distal point": [
                20.96654,
                2.27407,
                4.60937
            ],
            "mdAxis": [
                -0.39997428505819105,
                0.07413564631096169,
                0.913523112591162
            ],
            "mdCenter": [
                19.59088,
                2.52905,
                7.751315
            ],
            "toothAxis": [
                -0.10838262196089886,
                0.9501273826235062,
                -0.29242291983681157
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                -0.9160439127531187,
                -0.0,
                -0.40107798482085316
            ],
            "attachPoint": [
                21.363,
                2.52905,
                8.46111
            ],
            "mdToothPerpendicular": [
                0.9002904932997408,
                0.21855666258260148,
                0.37644390407451744
            ]
        },
        "25": {
            "Mesial Point": [
                20.63294,
                3.29227,
                4.01711
            ],
            "Apical Rotation": [
                20.37159,
                16.68085,
                -2.07532
            ],
            "Buccal Cusp": [
                22.95859,
                -0.51074,
                2.08612
            ],
            "Vestibular Gingival": [
                23.21454,
                6.3292,
                1.142
            ],
            "Distal point": [
                22.65705,
                2.27446,
                -2.03584
            ],
            "mdAxis": [
                -0.3131813062111062,
                0.15748109800096136,
                0.9365453396458269
            ],
            "mdCenter": [
                21.644995,
                2.783365,
                0.9906349999999999
            ],
            "toothAxis": [
                -0.0891208628408016,
                0.9726331014226404,
                -0.21457474647191568
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                -0.9483792138978098,
                -0.0,
                -0.3171385606427769
            ],
            "attachPoint": [
                23.21454,
                2.783365,
                1.142
            ],
            "mdToothPerpendicular": [
                0.9448931384265381,
                0.1506962997536117,
                0.29063307140622624
            ]
        },
        "26": {
            "Mesial Point": [
                22.94763,
                2.40844,
                -2.12691
            ],
            "Mesial Buccal": [
                25.12958,
                -0.2026,
                -3.77851
            ],
            "Vestibular Gingival": [
                26.84605,
                5.62261,
                -6.943
            ],
            "Apical Rotation": [
                20.16368,
                20.4106,
                -10.62784
            ],
            "Distal Buccal": [
                25.71669,
                -0.86892,
                -9.591
            ],
            "Distal point": [
                23.63299,
                1.85266,
                -13.18443
            ],
            "mdAxis": [
                -0.06178493680002185,
                0.050103350319125994,
                0.9968311170260569
            ],
            "mdCenter": [
                23.290309999999998,
                2.13055,
                -7.655670000000001
            ],
            "toothAxis": [
                -0.16646800237338755,
                0.9732662345034891,
                -0.15824424463851222
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                -0.9980846730253117,
                -0.0,
                -0.06186263389120046
            ],
            "attachPoint": [
                26.84605,
                2.13055,
                -6.943
            ],
            "mdToothPerpendicular": [
                0.982909333720098,
                0.1765796818163134,
                0.052046687267898684
            ]
        },
        "27": {
            "Mesial Point": [
                24.71548,
                3.07755,
                -12.74823
            ],
            "Mesial Buccal": [
                28.53782,
                0.47408,
                -15.05641
            ],
            "Vestibular Gingival": [
                26.11405,
                6.85948,
                -17.9521
            ],
            "Apical Rotation": [
                20.9465,
                16.65168,
                -19.21867
            ],
            "Distal Buccal": [
                28.19871,
                0.20082,
                -19.97089
            ],
            "Distal point": [
                25.0451,
                2.66963,
                -22.4861
            ],
            "mdAxis": [
                -0.033800307197538605,
                0.04182944394156864,
                0.9985528713357601
            ],
            "mdCenter": [
                24.880290000000002,
                2.87359,
                -17.617165
            ],
            "toothAxis": [
                -0.27284106874352976,
                0.955625186104123,
                -0.11107769753802473
            ],
            "verticalToothAxis": [
                0,
                -1,
                0
            ],
            "vestibularAxis": [
                -0.9994276045633833,
                -0.0,
                -0.03382991629752548
            ],
            "attachPoint": [
                26.11405,
                2.87359,
                -17.9521
            ],
            "mdToothPerpendicular": [
                0.960720295145378,
                0.27672830136382137,
                0.020927534973612452
            ]
        },
        "37": {
            "Distal point": [
                22.61621,
                -1.54655,
                -23.15195
            ],
            "Distal Buccal": [
                25.03688,
                1.91639,
                -18.86177
            ],
            "Vestibular Gingival": [
                27.79712,
                -3.80055,
                -16.4147
            ],
            "Apical Rotation": [
                25.80792,
                -17.25091,
                -20.23364
            ],
            "Mesial Buccal": [
                23.77114,
                1.19812,
                -13.88595
            ],
            "Mesial Point": [
                21.82015,
                -2.6052,
                -11.93093
            ],
            "mdAxis": [
                -0.07045448047335848,
                -0.09369474129226593,
                0.9931049600296056
            ],
            "mdCenter": [
                22.21818,
                -2.075875,
                -17.54144
            ],
            "toothAxis": [
                0.22684649716792224,
                -0.9589562291839026,
                -0.1701282376092643
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                -0.9974929594847601,
                0.0,
                -0.07076578112572968
            ],
            "attachPoint": [
                27.79712,
                -2.075875,
                -16.4147
            ],
            "mdToothPerpendicular": [
                0.972691737536591,
                0.21426696429966907,
                0.0892213636852283
            ]
        },
        "36": {
            "Distal point": [
                21.86855,
                -2.29533,
                -11.98262
            ],
            "Distal Buccal": [
                22.77623,
                0.25443,
                -11.22667
            ],
            "Vestibular Gingival": [
                25.60933,
                -4.26985,
                -5.07495
            ],
            "Apical Rotation": [
                22.9232,
                -20.1059,
                -7.31068
            ],
            "Mesial Buccal": [
                22.24933,
                0.86024,
                -4.01233
            ],
            "Mesial Point": [
                18.97345,
                -1.57168,
                -1.92466
            ],
            "mdAxis": [
                -0.2759518829633912,
                0.06897605613155264,
                0.9586933096509519
            ],
            "mdCenter": [
                20.421,
                -1.9335049999999998,
                -6.95364
            ],
            "toothAxis": [
                0.13637953618573628,
                -0.9904655109439656,
                -0.019460054991509546
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                -0.9609820656164334,
                0.0,
                -0.2766106823019912
            ],
            "attachPoint": [
                25.60933,
                -1.9335049999999998,
                -5.07495
            ],
            "mdToothPerpendicular": [
                0.9556588360917193,
                0.12636097416560985,
                0.26598701699093974
            ]
        },
        "35": {
            "Distal point": [
                18.53682,
                -1.75525,
                -1.55824
            ],
            "Apical Rotation": [
                18.06222,
                -19.85943,
                2.04608
            ],
            "Vestibular Gingival": [
                21.19268,
                -5.15736,
                3.11582
            ],
            "Buccal Cusp": [
                19.79904,
                1.37445,
                2.62948
            ],
            "Mesial Point": [
                17.50436,
                -1.12566,
                5.31799
            ],
            "mdAxis": [
                -0.14787973373445035,
                0.09017647324048636,
                0.9848856725653673
            ],
            "mdCenter": [
                18.02059,
                -1.440455,
                1.879875
            ],
            "toothAxis": [
                0.0022600714169442268,
                -0.9999567361736464,
                0.009023184478818221
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                -0.9889147065949222,
                0.0,
                -0.14848468971674794
            ],
            "attachPoint": [
                21.19268,
                -1.440455,
                3.11582
            ],
            "mdToothPerpendicular": [
                0.9889563718409874,
                0.003572176560824701,
                0.14816387599455175
            ]
        },
        "34": {
            "Distal point": [
                17.76363,
                -1.59004,
                5.75573
            ],
            "Apical Rotation": [
                13.6463,
                -20.4627,
                9.16156
            ],
            "Vestibular Gingival": [
                17.56179,
                -6.17483,
                10.51728
            ],
            "Buccal Cusp": [
                16.68027,
                1.79715,
                10.31177
            ],
            "Mesial Point": [
                14.34567,
                -0.52966,
                12.07949
            ],
            "mdAxis": [
                -0.47039553251809063,
                0.14593442134241857,
                0.8703052267190375
            ],
            "mdCenter": [
                16.05465,
                -1.05985,
                8.91761
            ],
            "toothAxis": [
                -0.12316867574691401,
                -0.992307322530368,
                0.01247617599122207
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                -0.8797233105073978,
                0.0,
                -0.47548595873054395
            ],
            "attachPoint": [
                17.56179,
                -1.05985,
                10.51728
            ],
            "mdToothPerpendicular": [
                0.8679422400613728,
                -0.10161962908343947,
                0.48615812129613817
            ]
        },
        "33": {
            "Distal point": [
                14.41027,
                -0.386,
                13.28918
            ],
            "Apical Rotation": [
                10.75592,
                -20.27824,
                8.97067
            ],
            "Vestibular Gingival": [
                13.0605,
                -7.7017,
                15.73367
            ],
            "Cusp of": [
                12.30724,
                1.99015,
                17.51137
            ],
            "Mesial Point": [
                10.28295,
                -1.17542,
                17.95662
            ],
            "mdAxis": [
                -0.6571786483852693,
                -0.12569657031882653,
                0.743180056457784
            ],
            "mdCenter": [
                12.34661,
                -0.78071,
                15.622900000000001
            ],
            "toothAxis": [
                -0.07698464189018728,
                -0.9436221795530134,
                -0.32194805041910146
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                -0.7491215389402713,
                0.0,
                -0.6624325776226284
            ],
            "attachPoint": [
                13.0605,
                -0.78071,
                15.73367
            ],
            "mdToothPerpendicular": [
                0.7435762190100934,
                -0.2694529904956086,
                0.6119554660558455
            ]
        },
        "32": {
            "Distal point": [
                10.04229,
                -0.11639,
                18.65953
            ],
            "Apical Rotation": [
                5.71124,
                -17.10497,
                11.36346
            ],
            "Vestibular Gingival": [
                7.78181,
                -6.40045,
                19.27325
            ],
            "Incisal Edge": [
                7.61048,
                1.66348,
                20.75095
            ],
            "Mesial Point": [
                4.51532,
                -0.52571,
                20.68579
            ],
            "mdAxis": [
                -0.9366310409489733,
                -0.06936564115260872,
                0.34338127636539867
            ],
            "mdCenter": [
                7.278805,
                -0.32105,
                19.67266
            ],
            "toothAxis": [
                -0.08340943685536406,
                -0.8930649226191463,
                -0.44212883849702633
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                -0.3442103748616185,
                0.0,
                -0.9388925486111944
            ],
            "attachPoint": [
                7.78181,
                -0.32105,
                19.27325
            ],
            "mdToothPerpendicular": [
                0.33735359972367374,
                -0.4427833838180544,
                0.8307438978217733
            ]
        },
        "31": {
            "Distal point": [
                4.4002,
                -1.07596,
                20.8415
            ],
            "Apical Rotation": [
                -0.08848,
                -17.03074,
                10.64425
            ],
            "Vestibular Gingival": [
                1.43081,
                -6.17694,
                21.08368
            ],
            "Incisal Edge": [
                2.16274,
                1.12744,
                22.61999
            ],
            "Mesial Point": [
                -0.74846,
                -0.4088,
                21.19624
            ],
            "mdAxis": [
                -0.9894019188861763,
                0.12820605443049288,
                0.0681692783570253
            ],
            "mdCenter": [
                1.8258699999999999,
                -0.74238,
                21.01887
            ],
            "toothAxis": [
                -0.0986453202231896,
                -0.8393295312302311,
                -0.5345980160858294
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                -0.06873652291348688,
                0.0,
                -0.9976348482374519
            ],
            "attachPoint": [
                1.43081,
                -0.74238,
                21.08368
            ],
            "mdToothPerpendicular": [
                -0.011334448341832342,
                -0.5362356978161678,
                0.8439921840090665
            ]
        },
        "41": {
            "Mesial Point": [
                -0.91813,
                -1.08461,
                21.28598
            ],
            "Apical Rotation": [
                -4.60771,
                -17.34044,
                10.47948
            ],
            "Vestibular Gingival": [
                -4.20509,
                -6.36,
                20.66248
            ],
            "Incisal Edge": [
                -3.52078,
                0.85932,
                22.57644
            ],
            "Distal point": [
                -6.30295,
                -0.64858,
                20.71286
            ],
            "mdAxis": [
                0.991175858225592,
                -0.08025939761442441,
                0.10549335128495486
            ],
            "mdCenter": [
                -3.61054,
                -0.866595,
                20.99942
            ],
            "toothAxis": [
                -0.05094961105448657,
                -0.8417180574244093,
                -0.5375079989535739
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                0.10583477309402002,
                0.0,
                -0.9943837291529549
            ],
            "attachPoint": [
                -4.20509,
                -0.866595,
                20.66248
            ],
            "mdToothPerpendicular": [
                -0.1320395471862204,
                -0.527805110380151,
                0.8390395243583312
            ]
        },
        "42": {
            "Mesial Point": [
                -6.19454,
                -0.68654,
                20.18167
            ],
            "Apical Rotation": [
                -6.86093,
                -18.19909,
                9.89613
            ],
            "Vestibular Gingival": [
                -8.95522,
                -6.5171,
                18.68928
            ],
            "Incisal Edge": [
                -9.3238,
                1.41841,
                20.72199
            ],
            "Distal point": [
                -11.88843,
                -0.65807,
                18.73379
            ],
            "mdAxis": [
                0.9691457356547358,
                -0.00484582229268397,
                0.24644078613035736
            ],
            "mdCenter": [
                -9.041485,
                -0.672305,
                19.457729999999998
            ],
            "toothAxis": [
                0.10857172831976636,
                -0.8726738556647075,
                -0.47608037288776384
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                0.24644367964180924,
                0.0,
                -0.9691571145921621
            ],
            "attachPoint": [
                -8.95522,
                -0.672305,
                18.68928
            ],
            "mdToothPerpendicular": [
                -0.21737617232463857,
                -0.48816290228029796,
                0.8452482360483016
            ]
        },
        "43": {
            "Mesial Point": [
                -11.83762,
                -1.79991,
                18.2778
            ],
            "Apical Rotation": [
                -12.15425,
                -22.14264,
                9.28156
            ],
            "Vestibular Gingival": [
                -15.12839,
                -8.03696,
                16.06414
            ],
            "Cusp of": [
                -13.20294,
                1.74764,
                18.01451
            ],
            "Distal point": [
                -15.9756,
                -0.9127,
                13.32306
            ],
            "mdAxis": [
                0.6350400421423522,
                -0.13615674212758788,
                0.7603850908908204
            ],
            "mdCenter": [
                -13.90661,
                -1.3563049999999999,
                15.800429999999999
            ],
            "toothAxis": [
                0.08018143518019581,
                -0.9511048942205564,
                -0.2982790935384981
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                0.7675328885369478,
                0.0,
                -0.64100956702231
            ],
            "attachPoint": [
                -15.12839,
                -1.3563049999999999,
                16.06414
            ],
            "mdToothPerpendicular": [
                -0.7646418730619188,
                -0.250657783872461,
                0.5937116146282698
            ]
        },
        "44": {
            "Mesial Point": [
                -16.27179,
                -0.9985,
                12.03323
            ],
            "Apical Rotation": [
                -16.14689,
                -21.16293,
                9.66946
            ],
            "Vestibular Gingival": [
                -19.57502,
                -6.70803,
                10.88324
            ],
            "Buccal Cusp": [
                -19.72734,
                1.0243,
                8.54094
            ],
            "Distal point": [
                -20.15187,
                -2.15433,
                6.28831
            ],
            "mdAxis": [
                0.5520760144712625,
                0.16445692351866956,
                0.8174142123503241
            ],
            "mdCenter": [
                -18.21183,
                -1.576415,
                9.16077
            ],
            "toothAxis": [
                0.10481060532398978,
                -0.994156969857432,
                0.025819688137311742
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                0.8286975375483768,
                0.0,
                -0.5596966957748247
            ],
            "attachPoint": [
                -19.57502,
                -1.576415,
                10.88324
            ],
            "mdToothPerpendicular": [
                -0.8198182509558944,
                -0.07167576305905128,
                0.5681202516981073
            ]
        },
        "45": {
            "Mesial Point": [
                -18.75136,
                -1.78428,
                5.59894
            ],
            "Apical Rotation": [
                -22.33225,
                -19.87422,
                1.01701
            ],
            "Vestibular Gingival": [
                -23.72173,
                -5.07181,
                3.74707
            ],
            "Buccal Cusp": [
                -20.51032,
                1.15318,
                3.91756
            ],
            "Distal point": [
                -21.12123,
                -1.68026,
                -1.22014
            ],
            "mdAxis": [
                0.3282413883417468,
                -0.0144074017626741,
                0.9444839954990933
            ],
            "mdCenter": [
                -19.936295,
                -1.7322700000000002,
                2.1894
            ],
            "toothAxis": [
                -0.13066234549825126,
                -0.9893632137965873,
                -0.06393576976140829
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                0.9445820355569392,
                0.0,
                -0.32827546070809055
            ],
            "attachPoint": [
                -23.72173,
                -1.7322700000000002,
                3.74707
            ],
            "mdToothPerpendicular": [
                -0.9390872769819216,
                0.10283039025059455,
                0.3279344401730169
            ]
        },
        "46": {
            "Mesial Point": [
                -21.15347,
                -1.52287,
                -1.26459
            ],
            "Mesial Buccal": [
                -24.59276,
                0.79694,
                -3.7848
            ],
            "Vestibular Gingival": [
                -28.17247,
                -3.88641,
                -4.17547
            ],
            "Apical Rotation": [
                -25.50948,
                -19.20639,
                -6.68134
            ],
            "Distal Buccal": [
                -25.22972,
                0.45267,
                -10.42576
            ],
            "Distal point": [
                -24.67319,
                -2.16583,
                -11.57838
            ],
            "mdAxis": [
                0.3224137452287564,
                0.05889648654787344,
                0.9447648282826169
            ],
            "mdCenter": [
                -22.913330000000002,
                -1.84435,
                -6.421485
            ],
            "toothAxis": [
                -0.1478698666629816,
                -0.9888960729531633,
                -0.01480065643422341
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                0.9464077019044641,
                0.0,
                -0.32297439801927164
            ],
            "attachPoint": [
                -28.17247,
                -1.84435,
                -4.17547
            ],
            "mdToothPerpendicular": [
                -0.9401851466884561,
                0.13591079324527466,
                0.312378210228957
            ]
        },
        "47": {
            "Mesial Point": [
                -24.61224,
                -2.70778,
                -11.20099
            ],
            "Mesial Buccal": [
                -26.75097,
                1.17398,
                -14.14174
            ],
            "Vestibular Gingival": [
                -31.27282,
                -3.26543,
                -15.10406
            ],
            "Apical Rotation": [
                -30.92335,
                -17.70679,
                -18.44093
            ],
            "Distal Buccal": [
                -28.16714,
                1.83973,
                -17.7959
            ],
            "Distal point": [
                -26.14026,
                -2.13003,
                -21.76994
            ],
            "mdAxis": [
                0.14287966583856596,
                -0.05402332884270585,
                0.9882645804796469
            ],
            "mdCenter": [
                -25.37625,
                -2.418905,
                -16.485464999999998
            ],
            "toothAxis": [
                -0.3386449943268262,
                -0.9333103295585389,
                -0.11937921325220537
            ],
            "verticalToothAxis": [
                0,
                1,
                0
            ],
            "vestibularAxis": [
                0.9897098798525865,
                0.0,
                -0.14308862191725297
            ],
            "attachPoint": [
                -31.27282,
                -2.418905,
                -15.10406
            ],
            "mdToothPerpendicular": [
                -0.9351133529325535,
                0.31977057337641174,
                0.15267546485849812
            ]
        }
    },
    "movementTable": {
        "18": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "17": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 23.0
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": -0.1
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "16": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -15.2
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 4.2
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "15": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -1.6
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": -0.2
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 5.0
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0.3
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 2.0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "14": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -1.2
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 1.8
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": -0.6
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0.8
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 3.9
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.02
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -0.61
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -0.18
            }
        ],
        "13": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 5.2
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": -2.3
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 9.2
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 2.7
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 1.0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.08
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -1.19
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -0.65
            }
        ],
        "12": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 10.6
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": -1.3
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 3.9
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": -5.3
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": -1.9
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -1.45
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -1.48
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -1.23
            }
        ],
        "11": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 5.3
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": -1.0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 4.7
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0.9
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": -0.5
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.82
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -1.58
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -1.27
            }
        ],
        "21": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 7.3
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": -2.8
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 4.9
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0.7
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": -2.8
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.15
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -1.93
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -1.5
            }
        ],
        "22": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 6.7
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": -2.7
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 5.6
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": -3.1
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": -7.4
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -1.13
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -1.43
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -0.9
            }
        ],
        "23": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 8.7
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 1.0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 12.3
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": -0.6
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": -6.3
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.42
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -0.89
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -0.29
            }
        ],
        "24": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -4.8
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 3.3
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.1
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -0.02
            }
        ],
        "25": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 0.4
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 8.1
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "26": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -12.8
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 3.2
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "27": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 19.1
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 3.1
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "28": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "48": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "47": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -39.4
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": -2.5
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "46": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -41.2
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": -19.2
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "45": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -25.5
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 10.6
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.09
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0.1
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -0.01
            }
        ],
        "44": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -4.3
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 4.3
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": -10.5
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 4.3
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 3.4
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0.06
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -0.71
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -0.15
            }
        ],
        "43": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -0.1
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 1.3
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 13.8
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": -2.1
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": -7.8
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.89
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -0.93
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -0.94
            }
        ],
        "42": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 16.4
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 1.9
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 1.3
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0.2
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 4.5
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.06
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -1.18
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -1.2
            }
        ],
        "41": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 10.3
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": -3.7
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 4.2
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": -2.8
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": -0.8
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0.08
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -1.56
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -0.89
            }
        ],
        "31": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 6.4
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": -5.5
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": -1.1
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 3.6
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 9.3
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.31
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -1.67
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -0.96
            }
        ],
        "32": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 8.7
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": -0.6
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 3.4
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": -1.4
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 6.3
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.69
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -1.44
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -0.94
            }
        ],
        "33": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 4.7
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 1.3
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 6.9
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": -3.9
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": -6.2
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.99
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -0.9
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": -0.89
            }
        ],
        "34": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -6.4
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 1.9
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.19
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": -0.01
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0.02
            }
        ],
        "35": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -12.5
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": -2.4
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": -0.09
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0.01
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "36": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -36.7
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": -17.1
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "37": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": -32.2
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 3.2
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ],
        "38": [
            {
                "type": "Strip Mesial",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Strip Distal",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Inclination",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Inclination +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Angulation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Rotation +/-",
                "unity": "\u00b0",
                "value": 0
            },
            {
                "type": "Mesial +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Vestibular +/-",
                "unity": "mm",
                "value": 0
            },
            {
                "type": "Occlusal +/-",
                "unity": "mm",
                "value": 0
            }
        ]
    },
    "movDataByArcanum": {
        "0": {
            "Lower": true,
            "Upper": true
        },
        "1": {
            "Lower": true,
            "Upper": true
        },
        "2": {
            "Lower": true,
            "Upper": true
        },
        "3": {
            "Lower": true,
            "Upper": true
        },
        "4": {
            "Lower": true,
            "Upper": true
        },
        "5": {
            "Lower": true,
            "Upper": true
        },
        "6": {
            "Lower": true,
            "Upper": true
        },
        "7": {
            "Lower": true,
            "Upper": true
        },
        "8": {
            "Lower": true,
            "Upper": true
        },
        "9": {
            "Lower": true,
            "Upper": true
        },
        "10": {
            "Lower": true,
            "Upper": true
        },
        "11": {
            "Lower": true,
            "Upper": true
        },
        "12": {
            "Lower": true,
            "Upper": true
        }
    },
    "transformationAttachment": {
        "0": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.24,
                    0.551,
                    -0.799,
                    -23.35
                ],
                [
                    -0.966,
                    -0.05,
                    0.255,
                    2.148
                ],
                [
                    0.101,
                    0.833,
                    0.544,
                    9.177
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.591,
                    0.388,
                    -0.708,
                    -19.69
                ],
                [
                    -0.734,
                    -0.622,
                    0.273,
                    1.794
                ],
                [
                    -0.334,
                    0.681,
                    0.652,
                    16.283
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.69,
                    0.628,
                    -0.36,
                    -12.797
                ],
                [
                    -0.722,
                    -0.557,
                    0.41,
                    1.577
                ],
                [
                    0.057,
                    0.543,
                    0.838,
                    22.396
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.311,
                    0.734,
                    0.604,
                    12.222
                ],
                [
                    -0.882,
                    -0.014,
                    0.472,
                    1.97
                ],
                [
                    0.355,
                    -0.679,
                    0.643,
                    21.842
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.589,
                    -0.326,
                    0.739,
                    17.851
                ],
                [
                    0.699,
                    -0.666,
                    0.263,
                    2.594
                ],
                [
                    0.406,
                    0.671,
                    0.62,
                    16.348
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.307
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.083
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.686
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.073
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.02
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.835
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.72,
                    0.282,
                    0.634,
                    13.818
                ],
                [
                    -0.571,
                    0.76,
                    0.311,
                    -2.271
                ],
                [
                    -0.394,
                    -0.586,
                    0.708,
                    16.786
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.834,
                    -0.111,
                    -0.54,
                    -14.98
                ],
                [
                    0.295,
                    0.918,
                    0.266,
                    -1.521
                ],
                [
                    0.467,
                    -0.381,
                    0.798,
                    17.466
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.239,
                    -0.56,
                    -0.793,
                    -20.426
                ],
                [
                    0.971,
                    -0.134,
                    -0.198,
                    -2.062
                ],
                [
                    0.004,
                    -0.818,
                    0.576,
                    10.556
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        },
        "10": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.262,
                    0.503,
                    -0.824,
                    -22.971
                ],
                [
                    -0.959,
                    -0.039,
                    0.281,
                    2.247
                ],
                [
                    0.109,
                    0.863,
                    0.493,
                    8.808
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.549,
                    0.41,
                    -0.729,
                    -18.863
                ],
                [
                    -0.766,
                    -0.596,
                    0.241,
                    1.753
                ],
                [
                    -0.335,
                    0.691,
                    0.641,
                    15.442
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.728,
                    0.611,
                    -0.312,
                    -13.025
                ],
                [
                    -0.685,
                    -0.623,
                    0.378,
                    1.748
                ],
                [
                    0.037,
                    0.489,
                    0.872,
                    20.414
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.281,
                    0.807,
                    0.52,
                    11.861
                ],
                [
                    -0.9,
                    0.033,
                    0.435,
                    1.978
                ],
                [
                    0.334,
                    -0.59,
                    0.735,
                    20.255
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.635,
                    -0.376,
                    0.675,
                    17.261
                ],
                [
                    0.689,
                    -0.67,
                    0.276,
                    2.493
                ],
                [
                    0.349,
                    0.64,
                    0.685,
                    15.761
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.341
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.077
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.609
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.146
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.011
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.685
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.721,
                    0.374,
                    0.584,
                    13.524
                ],
                [
                    -0.619,
                    0.726,
                    0.3,
                    -2.66
                ],
                [
                    -0.312,
                    -0.578,
                    0.754,
                    15.667
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.87,
                    -0.186,
                    -0.457,
                    -14.575
                ],
                [
                    0.329,
                    0.909,
                    0.256,
                    -1.973
                ],
                [
                    0.367,
                    -0.373,
                    0.852,
                    16.335
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.259,
                    -0.522,
                    -0.812,
                    -19.923
                ],
                [
                    0.963,
                    -0.072,
                    -0.261,
                    -2.29
                ],
                [
                    0.078,
                    -0.85,
                    0.522,
                    10.123
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        },
        "11": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.265,
                    0.498,
                    -0.826,
                    -22.932
                ],
                [
                    -0.958,
                    -0.038,
                    0.284,
                    2.258
                ],
                [
                    0.11,
                    0.866,
                    0.487,
                    8.769
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.544,
                    0.412,
                    -0.731,
                    -18.779
                ],
                [
                    -0.769,
                    -0.593,
                    0.238,
                    1.75
                ],
                [
                    -0.335,
                    0.692,
                    0.64,
                    15.357
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.731,
                    0.609,
                    -0.307,
                    -13.049
                ],
                [
                    -0.681,
                    -0.629,
                    0.375,
                    1.769
                ],
                [
                    0.035,
                    0.483,
                    0.875,
                    20.213
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.278,
                    0.814,
                    0.511,
                    11.827
                ],
                [
                    -0.902,
                    0.037,
                    0.43,
                    1.979
                ],
                [
                    0.331,
                    -0.58,
                    0.744,
                    20.09
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.64,
                    -0.381,
                    0.668,
                    17.199
                ],
                [
                    0.688,
                    -0.671,
                    0.277,
                    2.482
                ],
                [
                    0.343,
                    0.637,
                    0.691,
                    15.7
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.345
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.076
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.601
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.154
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.01
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.67
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.72,
                    0.383,
                    0.579,
                    13.494
                ],
                [
                    -0.624,
                    0.722,
                    0.299,
                    -2.7
                ],
                [
                    -0.304,
                    -0.576,
                    0.759,
                    15.554
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.873,
                    -0.193,
                    -0.448,
                    -14.533
                ],
                [
                    0.332,
                    0.908,
                    0.256,
                    -2.018
                ],
                [
                    0.357,
                    -0.372,
                    0.857,
                    16.219
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.261,
                    -0.519,
                    -0.814,
                    -19.873
                ],
                [
                    0.962,
                    -0.066,
                    -0.267,
                    -2.317
                ],
                [
                    0.085,
                    -0.853,
                    0.516,
                    10.078
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        },
        "12": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.266,
                    0.494,
                    -0.828,
                    -22.903
                ],
                [
                    -0.957,
                    -0.037,
                    0.286,
                    2.266
                ],
                [
                    0.11,
                    0.869,
                    0.483,
                    8.74
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.541,
                    0.414,
                    -0.732,
                    -18.715
                ],
                [
                    -0.771,
                    -0.591,
                    0.236,
                    1.748
                ],
                [
                    -0.335,
                    0.692,
                    0.639,
                    15.293
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.734,
                    0.607,
                    -0.303,
                    -13.068
                ],
                [
                    -0.678,
                    -0.634,
                    0.372,
                    1.784
                ],
                [
                    0.034,
                    0.479,
                    0.877,
                    20.061
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.275,
                    0.819,
                    0.504,
                    11.801
                ],
                [
                    -0.903,
                    0.041,
                    0.427,
                    1.981
                ],
                [
                    0.329,
                    -0.573,
                    0.751,
                    19.964
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.643,
                    -0.384,
                    0.663,
                    17.152
                ],
                [
                    0.687,
                    -0.671,
                    0.278,
                    2.474
                ],
                [
                    0.338,
                    0.634,
                    0.696,
                    15.653
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.347
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.075
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.595
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.16
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.01
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.658
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.72,
                    0.39,
                    0.575,
                    13.472
                ],
                [
                    -0.628,
                    0.719,
                    0.298,
                    -2.73
                ],
                [
                    -0.297,
                    -0.575,
                    0.762,
                    15.468
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.875,
                    -0.199,
                    -0.441,
                    -14.501
                ],
                [
                    0.335,
                    0.907,
                    0.255,
                    -2.053
                ],
                [
                    0.349,
                    -0.371,
                    0.861,
                    16.131
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.263,
                    -0.516,
                    -0.815,
                    -19.836
                ],
                [
                    0.961,
                    -0.061,
                    -0.271,
                    -2.337
                ],
                [
                    0.09,
                    -0.855,
                    0.511,
                    10.043
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        },
        "1": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.242,
                    0.546,
                    -0.802,
                    -23.313
                ],
                [
                    -0.965,
                    -0.049,
                    0.258,
                    2.157
                ],
                [
                    0.102,
                    0.836,
                    0.539,
                    9.141
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.587,
                    0.39,
                    -0.71,
                    -19.609
                ],
                [
                    -0.738,
                    -0.619,
                    0.27,
                    1.789
                ],
                [
                    -0.334,
                    0.682,
                    0.651,
                    16.2
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.693,
                    0.627,
                    -0.355,
                    -12.818
                ],
                [
                    -0.718,
                    -0.564,
                    0.407,
                    1.592
                ],
                [
                    0.055,
                    0.538,
                    0.841,
                    22.2
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.308,
                    0.742,
                    0.596,
                    12.185
                ],
                [
                    -0.883,
                    -0.009,
                    0.468,
                    1.97
                ],
                [
                    0.353,
                    -0.671,
                    0.652,
                    21.689
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.594,
                    -0.331,
                    0.733,
                    17.795
                ],
                [
                    0.698,
                    -0.666,
                    0.264,
                    2.585
                ],
                [
                    0.401,
                    0.668,
                    0.627,
                    16.291
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.311
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.082
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.678
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.08
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.019
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.82
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.721,
                    0.291,
                    0.629,
                    13.788
                ],
                [
                    -0.576,
                    0.757,
                    0.309,
                    -2.31
                ],
                [
                    -0.386,
                    -0.585,
                    0.713,
                    16.675
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.838,
                    -0.118,
                    -0.532,
                    -14.94
                ],
                [
                    0.298,
                    0.917,
                    0.265,
                    -1.566
                ],
                [
                    0.457,
                    -0.381,
                    0.804,
                    17.355
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.241,
                    -0.556,
                    -0.795,
                    -20.375
                ],
                [
                    0.971,
                    -0.128,
                    -0.204,
                    -2.082
                ],
                [
                    0.012,
                    -0.821,
                    0.571,
                    10.515
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        },
        "2": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.244,
                    0.542,
                    -0.804,
                    -23.275
                ],
                [
                    -0.964,
                    -0.048,
                    0.26,
                    2.167
                ],
                [
                    0.102,
                    0.839,
                    0.534,
                    9.105
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.583,
                    0.392,
                    -0.712,
                    -19.527
                ],
                [
                    -0.741,
                    -0.617,
                    0.267,
                    1.784
                ],
                [
                    -0.334,
                    0.683,
                    0.65,
                    16.116
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.697,
                    0.625,
                    -0.35,
                    -12.84
                ],
                [
                    -0.715,
                    -0.57,
                    0.404,
                    1.607
                ],
                [
                    0.053,
                    0.532,
                    0.845,
                    22.003
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.305,
                    0.749,
                    0.588,
                    12.148
                ],
                [
                    -0.885,
                    -0.004,
                    0.465,
                    1.97
                ],
                [
                    0.351,
                    -0.662,
                    0.662,
                    21.534
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.599,
                    -0.336,
                    0.727,
                    17.738
                ],
                [
                    0.697,
                    -0.666,
                    0.265,
                    2.575
                ],
                [
                    0.395,
                    0.665,
                    0.633,
                    16.234
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.314
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.082
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.671
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.087
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.018
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.805
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.721,
                    0.3,
                    0.624,
                    13.759
                ],
                [
                    -0.581,
                    0.754,
                    0.308,
                    -2.348
                ],
                [
                    -0.378,
                    -0.585,
                    0.718,
                    16.564
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.842,
                    -0.126,
                    -0.524,
                    -14.901
                ],
                [
                    0.301,
                    0.916,
                    0.264,
                    -1.611
                ],
                [
                    0.447,
                    -0.38,
                    0.81,
                    17.244
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.243,
                    -0.553,
                    -0.797,
                    -20.325
                ],
                [
                    0.97,
                    -0.122,
                    -0.211,
                    -2.102
                ],
                [
                    0.019,
                    -0.824,
                    0.566,
                    10.473
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        },
        "3": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.246,
                    0.537,
                    -0.807,
                    -23.237
                ],
                [
                    -0.964,
                    -0.047,
                    0.263,
                    2.176
                ],
                [
                    0.103,
                    0.842,
                    0.529,
                    9.069
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.578,
                    0.394,
                    -0.714,
                    -19.445
                ],
                [
                    -0.744,
                    -0.614,
                    0.263,
                    1.779
                ],
                [
                    -0.335,
                    0.684,
                    0.649,
                    16.033
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.701,
                    0.624,
                    -0.346,
                    -12.862
                ],
                [
                    -0.711,
                    -0.577,
                    0.401,
                    1.623
                ],
                [
                    0.051,
                    0.527,
                    0.848,
                    21.807
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.302,
                    0.757,
                    0.58,
                    12.111
                ],
                [
                    -0.887,
                    0.0,
                    0.461,
                    1.97
                ],
                [
                    0.349,
                    -0.654,
                    0.671,
                    21.378
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.603,
                    -0.341,
                    0.721,
                    17.68
                ],
                [
                    0.696,
                    -0.667,
                    0.267,
                    2.565
                ],
                [
                    0.39,
                    0.662,
                    0.64,
                    16.177
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.317
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.081
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.663
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.095
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.017
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.791
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.721,
                    0.31,
                    0.619,
                    13.73
                ],
                [
                    -0.586,
                    0.75,
                    0.307,
                    -2.387
                ],
                [
                    -0.37,
                    -0.584,
                    0.723,
                    16.453
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.846,
                    -0.133,
                    -0.516,
                    -14.861
                ],
                [
                    0.305,
                    0.915,
                    0.263,
                    -1.656
                ],
                [
                    0.438,
                    -0.38,
                    0.815,
                    17.132
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.245,
                    -0.549,
                    -0.799,
                    -20.274
                ],
                [
                    0.969,
                    -0.116,
                    -0.217,
                    -2.123
                ],
                [
                    0.026,
                    -0.828,
                    0.56,
                    10.43
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        },
        "4": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.249,
                    0.532,
                    -0.809,
                    -23.2
                ],
                [
                    -0.963,
                    -0.046,
                    0.266,
                    2.186
                ],
                [
                    0.104,
                    0.845,
                    0.524,
                    9.033
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.574,
                    0.397,
                    -0.716,
                    -19.364
                ],
                [
                    -0.747,
                    -0.612,
                    0.26,
                    1.774
                ],
                [
                    -0.335,
                    0.685,
                    0.648,
                    15.949
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.705,
                    0.622,
                    -0.341,
                    -12.884
                ],
                [
                    -0.708,
                    -0.584,
                    0.398,
                    1.639
                ],
                [
                    0.049,
                    0.522,
                    0.852,
                    21.611
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.299,
                    0.764,
                    0.572,
                    12.074
                ],
                [
                    -0.889,
                    0.005,
                    0.458,
                    1.971
                ],
                [
                    0.347,
                    -0.645,
                    0.681,
                    21.222
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.608,
                    -0.346,
                    0.715,
                    17.622
                ],
                [
                    0.695,
                    -0.667,
                    0.268,
                    2.555
                ],
                [
                    0.384,
                    0.659,
                    0.646,
                    16.12
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.321
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.08
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.655
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.102
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.016
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.776
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.722,
                    0.319,
                    0.615,
                    13.701
                ],
                [
                    -0.59,
                    0.747,
                    0.306,
                    -2.425
                ],
                [
                    -0.362,
                    -0.584,
                    0.727,
                    16.343
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.85,
                    -0.141,
                    -0.508,
                    -14.821
                ],
                [
                    0.308,
                    0.915,
                    0.262,
                    -1.701
                ],
                [
                    0.428,
                    -0.379,
                    0.821,
                    17.02
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.246,
                    -0.545,
                    -0.801,
                    -20.224
                ],
                [
                    0.969,
                    -0.11,
                    -0.223,
                    -2.145
                ],
                [
                    0.034,
                    -0.831,
                    0.555,
                    10.388
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        },
        "5": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.251,
                    0.527,
                    -0.812,
                    -23.162
                ],
                [
                    -0.962,
                    -0.045,
                    0.268,
                    2.196
                ],
                [
                    0.105,
                    0.848,
                    0.519,
                    8.997
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.57,
                    0.399,
                    -0.718,
                    -19.282
                ],
                [
                    -0.75,
                    -0.609,
                    0.257,
                    1.77
                ],
                [
                    -0.335,
                    0.686,
                    0.647,
                    15.866
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.709,
                    0.62,
                    -0.336,
                    -12.906
                ],
                [
                    -0.704,
                    -0.59,
                    0.395,
                    1.656
                ],
                [
                    0.047,
                    0.517,
                    0.855,
                    21.414
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.296,
                    0.771,
                    0.564,
                    12.038
                ],
                [
                    -0.891,
                    0.01,
                    0.454,
                    1.972
                ],
                [
                    0.345,
                    -0.636,
                    0.69,
                    21.065
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.613,
                    -0.351,
                    0.708,
                    17.564
                ],
                [
                    0.694,
                    -0.668,
                    0.269,
                    2.545
                ],
                [
                    0.378,
                    0.656,
                    0.653,
                    16.062
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.324
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.08
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.648
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.109
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.015
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.761
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.722,
                    0.328,
                    0.61,
                    13.672
                ],
                [
                    -0.595,
                    0.744,
                    0.305,
                    -2.464
                ],
                [
                    -0.354,
                    -0.583,
                    0.732,
                    16.232
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.853,
                    -0.148,
                    -0.5,
                    -14.781
                ],
                [
                    0.311,
                    0.914,
                    0.261,
                    -1.746
                ],
                [
                    0.418,
                    -0.378,
                    0.826,
                    16.908
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.248,
                    -0.541,
                    -0.803,
                    -20.174
                ],
                [
                    0.968,
                    -0.104,
                    -0.229,
                    -2.167
                ],
                [
                    0.041,
                    -0.834,
                    0.55,
                    10.345
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        },
        "6": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.253,
                    0.523,
                    -0.814,
                    -23.124
                ],
                [
                    -0.962,
                    -0.044,
                    0.271,
                    2.206
                ],
                [
                    0.106,
                    0.851,
                    0.514,
                    8.96
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.566,
                    0.401,
                    -0.72,
                    -19.199
                ],
                [
                    -0.753,
                    -0.606,
                    0.254,
                    1.766
                ],
                [
                    -0.335,
                    0.687,
                    0.645,
                    15.781
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.712,
                    0.619,
                    -0.331,
                    -12.929
                ],
                [
                    -0.7,
                    -0.597,
                    0.392,
                    1.673
                ],
                [
                    0.045,
                    0.511,
                    0.858,
                    21.216
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.293,
                    0.779,
                    0.555,
                    12.002
                ],
                [
                    -0.893,
                    0.014,
                    0.45,
                    1.973
                ],
                [
                    0.343,
                    -0.627,
                    0.699,
                    20.906
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.617,
                    -0.356,
                    0.702,
                    17.504
                ],
                [
                    0.693,
                    -0.668,
                    0.27,
                    2.534
                ],
                [
                    0.373,
                    0.653,
                    0.659,
                    16.003
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.327
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.079
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.64
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.117
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.014
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.746
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.722,
                    0.337,
                    0.605,
                    13.642
                ],
                [
                    -0.6,
                    0.74,
                    0.304,
                    -2.503
                ],
                [
                    -0.345,
                    -0.582,
                    0.736,
                    16.119
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.857,
                    -0.156,
                    -0.491,
                    -14.74
                ],
                [
                    0.315,
                    0.913,
                    0.26,
                    -1.791
                ],
                [
                    0.408,
                    -0.377,
                    0.831,
                    16.795
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.25,
                    -0.538,
                    -0.805,
                    -20.124
                ],
                [
                    0.967,
                    -0.098,
                    -0.236,
                    -2.19
                ],
                [
                    0.048,
                    -0.837,
                    0.544,
                    10.302
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        },
        "7": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.255,
                    0.518,
                    -0.817,
                    -23.086
                ],
                [
                    -0.961,
                    -0.043,
                    0.273,
                    2.216
                ],
                [
                    0.107,
                    0.854,
                    0.508,
                    8.922
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.562,
                    0.403,
                    -0.722,
                    -19.116
                ],
                [
                    -0.757,
                    -0.604,
                    0.251,
                    1.763
                ],
                [
                    -0.335,
                    0.688,
                    0.644,
                    15.697
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.716,
                    0.617,
                    -0.326,
                    -12.952
                ],
                [
                    -0.697,
                    -0.603,
                    0.388,
                    1.691
                ],
                [
                    0.043,
                    0.506,
                    0.862,
                    21.017
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.29,
                    0.786,
                    0.547,
                    11.967
                ],
                [
                    -0.895,
                    0.019,
                    0.447,
                    1.974
                ],
                [
                    0.34,
                    -0.618,
                    0.708,
                    20.746
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.622,
                    -0.361,
                    0.695,
                    17.445
                ],
                [
                    0.692,
                    -0.669,
                    0.272,
                    2.524
                ],
                [
                    0.367,
                    0.65,
                    0.666,
                    15.944
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.331
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.078
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.632
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.124
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.014
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.731
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.722,
                    0.346,
                    0.6,
                    13.613
                ],
                [
                    -0.605,
                    0.737,
                    0.303,
                    -2.542
                ],
                [
                    -0.337,
                    -0.581,
                    0.741,
                    16.007
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.86,
                    -0.163,
                    -0.483,
                    -14.7
                ],
                [
                    0.318,
                    0.912,
                    0.259,
                    -1.836
                ],
                [
                    0.398,
                    -0.376,
                    0.837,
                    16.681
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.253,
                    -0.534,
                    -0.807,
                    -20.073
                ],
                [
                    0.966,
                    -0.091,
                    -0.242,
                    -2.214
                ],
                [
                    0.055,
                    -0.841,
                    0.539,
                    10.258
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        },
        "8": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.258,
                    0.513,
                    -0.819,
                    -23.048
                ],
                [
                    -0.96,
                    -0.042,
                    0.276,
                    2.226
                ],
                [
                    0.108,
                    0.857,
                    0.503,
                    8.884
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.557,
                    0.406,
                    -0.724,
                    -19.032
                ],
                [
                    -0.76,
                    -0.601,
                    0.248,
                    1.759
                ],
                [
                    -0.335,
                    0.689,
                    0.643,
                    15.612
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.72,
                    0.615,
                    -0.322,
                    -12.976
                ],
                [
                    -0.693,
                    -0.61,
                    0.385,
                    1.71
                ],
                [
                    0.041,
                    0.5,
                    0.865,
                    20.816
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.287,
                    0.793,
                    0.538,
                    11.931
                ],
                [
                    -0.896,
                    0.024,
                    0.443,
                    1.975
                ],
                [
                    0.338,
                    -0.609,
                    0.717,
                    20.583
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.626,
                    -0.366,
                    0.688,
                    17.384
                ],
                [
                    0.691,
                    -0.669,
                    0.273,
                    2.514
                ],
                [
                    0.361,
                    0.647,
                    0.672,
                    15.883
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.334
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.078
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.624
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.131
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.013
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.715
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.721,
                    0.355,
                    0.595,
                    13.583
                ],
                [
                    -0.61,
                    0.733,
                    0.302,
                    -2.581
                ],
                [
                    -0.329,
                    -0.58,
                    0.745,
                    15.894
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.864,
                    -0.171,
                    -0.474,
                    -14.658
                ],
                [
                    0.322,
                    0.911,
                    0.258,
                    -1.882
                ],
                [
                    0.388,
                    -0.375,
                    0.842,
                    16.566
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.255,
                    -0.53,
                    -0.809,
                    -20.023
                ],
                [
                    0.965,
                    -0.085,
                    -0.248,
                    -2.239
                ],
                [
                    0.063,
                    -0.844,
                    0.533,
                    10.213
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        },
        "9": {
            "16": [
                [
                    0.082,
                    -0.218,
                    -0.972,
                    -29.223
                ],
                [
                    0.988,
                    -0.107,
                    0.108,
                    2.012
                ],
                [
                    -0.128,
                    -0.97,
                    0.207,
                    -6.264
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "14": [
                [
                    -0.26,
                    0.508,
                    -0.821,
                    -23.009
                ],
                [
                    -0.96,
                    -0.041,
                    0.279,
                    2.237
                ],
                [
                    0.108,
                    0.86,
                    0.498,
                    8.846
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "13": [
                [
                    -0.553,
                    0.408,
                    -0.726,
                    -18.948
                ],
                [
                    -0.763,
                    -0.598,
                    0.245,
                    1.756
                ],
                [
                    -0.335,
                    0.69,
                    0.642,
                    15.527
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "12": [
                [
                    -0.724,
                    0.613,
                    -0.317,
                    -13.0
                ],
                [
                    -0.689,
                    -0.616,
                    0.382,
                    1.729
                ],
                [
                    0.039,
                    0.494,
                    0.868,
                    20.615
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "22": [
                [
                    0.284,
                    0.8,
                    0.529,
                    11.896
                ],
                [
                    -0.898,
                    0.028,
                    0.439,
                    1.976
                ],
                [
                    0.336,
                    -0.6,
                    0.726,
                    20.419
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "23": [
                [
                    -0.631,
                    -0.371,
                    0.682,
                    17.323
                ],
                [
                    0.69,
                    -0.67,
                    0.274,
                    2.503
                ],
                [
                    0.355,
                    0.643,
                    0.678,
                    15.823
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "24": [
                [
                    0.126,
                    0.426,
                    0.896,
                    21.338
                ],
                [
                    -0.979,
                    -0.096,
                    0.183,
                    2.077
                ],
                [
                    0.163,
                    -0.9,
                    0.405,
                    8.616
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "26": [
                [
                    -0.134,
                    0.035,
                    0.99,
                    26.572
                ],
                [
                    0.991,
                    0.006,
                    0.134,
                    2.278
                ],
                [
                    -0.001,
                    0.999,
                    -0.035,
                    -6.751
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "36": [
                [
                    0.037,
                    0.231,
                    0.972,
                    25.109
                ],
                [
                    -0.992,
                    0.123,
                    0.008,
                    -2.11
                ],
                [
                    -0.118,
                    -0.965,
                    0.234,
                    -5.495
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "34": [
                [
                    0.192,
                    -0.619,
                    0.762,
                    18.139
                ],
                [
                    0.981,
                    0.109,
                    -0.159,
                    -2.012
                ],
                [
                    0.015,
                    0.778,
                    0.628,
                    10.7
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "33": [
                [
                    0.721,
                    0.364,
                    0.589,
                    13.553
                ],
                [
                    -0.614,
                    0.729,
                    0.301,
                    -2.621
                ],
                [
                    -0.32,
                    -0.579,
                    0.75,
                    15.78
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "43": [
                [
                    0.867,
                    -0.178,
                    -0.465,
                    -14.617
                ],
                [
                    0.325,
                    0.91,
                    0.257,
                    -1.928
                ],
                [
                    0.378,
                    -0.374,
                    0.847,
                    16.45
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "44": [
                [
                    -0.257,
                    -0.526,
                    -0.811,
                    -19.973
                ],
                [
                    0.964,
                    -0.079,
                    -0.254,
                    -2.264
                ],
                [
                    0.07,
                    -0.847,
                    0.527,
                    10.168
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "46": [
                [
                    -0.007,
                    -0.23,
                    -0.973,
                    -27.673
                ],
                [
                    0.995,
                    0.09,
                    -0.029,
                    -2.125
                ],
                [
                    0.095,
                    -0.969,
                    0.229,
                    -5.249
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ]
        }
    }
}
"""


def test_aws_upload():
    jsonData = json.loads(strDataJson)
    jsonData = upload_optimized_files(data_json=jsonData, base_file_path=optimized_files_dir, patient_id='patient1', af_setup_name='Setup_1')
    # print('==== jsonData: \n', json.dumps(jsonData))
    with open (os.path.join("up.json"),'w') as f:
        json.dump(jsonData,f)


if __name__ == "__main__": 
    test_aws_upload()