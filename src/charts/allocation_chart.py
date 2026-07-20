from pathlib import Path

import matplotlib.pyplot as plt


def plot_allocation(
    allocation: dict[str, float],
    title: str,
    output_path: Path | None = None,
) -> None:
    if not allocation:
        raise ValueError(
            "Cannot plot an empty allocation"
        )

    labels = list(allocation.keys())
    percentages = list(allocation.values())

    figure, axis = plt.subplots(
        figsize=(8, 6)
    )

    axis.pie(
        percentages,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
    )

    axis.set_title(title)
    axis.axis("equal")

    figure.tight_layout()

    if output_path is not None:
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        figure.savefig(
            output_path,
            dpi=150,
            bbox_inches="tight",
        )

    plt.show()
    plt.close(figure)