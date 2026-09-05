import matplotlib.pyplot as plt
import numpy as np

labels = [
    "Зарплата",
    "Интересные задачи",
    "Разнообразие",
    "Объем работы",
    "Коллектив"
]

values = [8, 6, 8, 8, 2]
values += values[:1]

angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

ax.plot(angles, values, color="red")
ax.fill(angles, values, color="red", alpha=0.1)

ax.set_thetagrids(np.degrees(angles[:-1]), labels)
ax.set_ylim(0, 8)

plt.show()
