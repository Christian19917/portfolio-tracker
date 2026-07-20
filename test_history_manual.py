from datetime import date
import matplotlib.pyplot as plt

from src.providers.yahoo_price_provider import (
    YahooPriceProvider,
)


provider = YahooPriceProvider({
    "MTD": "MTD.PA",
    "ALLW": "ALLW.DE",
})

start_date = date(2026, 7, 8)
end_date = date.today()

mtd_history = provider.get_history(
    "MTD",
    start_date,
    end_date,
)

allw_history = provider.get_history(
    "ALLW",
    start_date,
    end_date,
)

print("\nMTD")
print(mtd_history)

print("\nALLW")
print(allw_history)

plt.figure(figsize=(10, 5))

plt.plot(
    mtd_history.index,
    mtd_history.values,
    marker="o",
    label="MTD",
)

plt.plot(
    allw_history.index,
    allw_history.values,
    marker="o",
    label="ALLW",
)

plt.title("ETF prices since first investment")
plt.xlabel("Date")
plt.ylabel("Price (€)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()