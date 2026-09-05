schedule = [
    ('6:20', 'B', 'O', '7:00'),
    ('7:30', 'A', 'U', '11:10'),
    ('8:10', 'O', 'V', '9:20'),
    ('8:50', 'A', 'B', '9:20'),
    ('10:00', 'U', 'V', '12:10'),
    ('10:00', 'V', 'O', '10:50'),
    ('10:10', 'A', 'O', '11:20'),
    ('11:15', 'B', 'U', '14:30'),
    ('11:25', 'O', 'Y', '11:50'),
    ('11:30', 'A', 'V', '13:10'),
    ('12:00', 'Y', 'U', '14:10'),
    ('12:30', 'V', 'U', '14:40'),

    ('13:15', 'A', 'B', '13:45'),
    ('14:40', 'U', 'B', '16:55'),
    ('14:50', 'Y', 'O', '15:15'),
    ('15:20', 'U', 'A', '18:50'),
    ('16:00', 'B', 'Y', '17:00'),
    ('16:00', 'O', 'A', '17:50'),
    ('18:00', 'A', 'O', '19:10'),
    ('18:10', 'V', 'A', '19:30'),
    ('19:15', 'O', 'Y', '19:40'),
    ('20:30', 'A', 'V', '21:50'),
    ('21:40', 'Y', 'U', '23:50'),
    ('22:00', 'V', 'A', '23:40'),
]


def to_minutes(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m


def find_all_routes(schedule, start='A', end='U'):
    routes = []

    def dfs(current_station, current_time, path):
        if current_station == end:
            routes.append(path.copy())
            return

        for dep, src, dst, arr in schedule:
            dep_min = to_minutes(dep)
            arr_min = to_minutes(arr)

            if src == current_station and dep_min >= current_time:
                if dst not in [step[2] for step in path]:
                    path.append((dep, src, dst, arr))
                    dfs(dst, arr_min, path)
                    path.pop()

    dfs(start, 0, [])
    return routes


routes = find_all_routes(schedule)

for i, route in enumerate(routes, 1):
    print(f"\nМаршрут {i}:")
    for dep, src, dst, arr in route:
        print(f"{src} ({dep}) -> {dst} ({arr})")