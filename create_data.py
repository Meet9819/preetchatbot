import pandas as pd

# Define the full dataset with the new 'branch' column
data = {
    "name": ["Paracetamol", "Ibuprofen", "Loratadine", "Amoxicillin"],
    "usage": ["fever, headache", "fever, pain, inflammation", "allergies, cold", "infections"],
    "price": ["$5.00", "$6.00", "$8.50", "$15.00"],
    "stock": [10, 3, 15, 0],
    "branch": ["Downtown", "Eastside", "Downtown", "Westside"], # ADDED THIS
    "image_url": [
        "https://onlinefamilypharmacy.com/wp-content/uploads/2022/03/Panadol-Advance-500mg-Tablet.jpg",
        "https://onlinefamilypharmacy.com/wp-content/uploads/2022/01/advil.jpg",
        "https://onlinefamilypharmacy.com/wp-content/uploads/2021/11/claritine.jpg",
        "https://onlinefamilypharmacy.com/wp-content/uploads/2022/03/Amoxicillin.jpg"
    ],
    "buy_link": ["#", "#", "#", "#"]
}

# Overwrite the old products.csv
df = pd.DataFrame(data)
df.to_csv("products.csv", index=False)
print("✅ SUCCESS: 'products.csv' now contains the 'branch' column!")