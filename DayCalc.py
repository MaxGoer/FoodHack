NON_ACTIVE, ACTIVE, VERY_ACTIVE = 0, 1, 2
MALE, FEMALE = 0, 1
DELTA_CAL = 500

##
# Table of constants
const = {
    MALE: [
        [
            [72, 81, 358, 2450],
            [80, 93, 411, 2800],
            [94, 110, 484, 3300]
        ],
        [
            [68, 77, 335, 2300],
            [77, 88, 387, 2650],
            [89, 105, 462, 3150]
        ],
        [
            [65, 70, 303, 2100],
            [72, 83, 366, 2500],
            [84, 98, 432, 2950]
        ]
    ],
    FEMALE: [
        [
            [61, 67, 269, 2000],
            [66, 73, 318, 2200],
            [76, 87, 378, 2600]
        ],
        [
            [59, 63, 274, 1900],
            [65, 72, 311, 2150],
            [74, 85, 372, 2550]
        ],
        [
            [58, 60, 257, 1800],
            [63, 70, 305, 2100],
            [72, 83, 366, 2500]
        ]
    ]
}


PROT, FAT, HYD, CAL = 0, 1, 2, 3


def get_nutrition(data: dict):
    nut = const[data['gender']][data['age']][data['activity']].copy()
    nut[CAL] += data['delta']
    return nut
