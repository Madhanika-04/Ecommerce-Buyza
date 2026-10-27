# Dataset Documentation: 100k Amazon Products

## 1. Source & Overview
- **Dataset Title**: A Comprehensive Dataset of 100k Amazon Products
- **Kaggle Source**: [https://www.kaggle.com/datasets/joyshil0599/a-comprehensive-dataset-of-100k-amazon-products](https://www.kaggle.com/datasets/joyshil0599/a-comprehensive-dataset-of-100k-amazon-products)
- **Total Files**: 9 category-specific CSV files
- **Total Physical Records**: 100,707 lines (100,678 successfully parsed product records)
- **Total Size on Disk**: ~14.93 MB

---

## 2. File-by-File Breakdown & Schema Inspection

| File Name | Category | Size (MB) | Physical Lines | Parsed Rows | Key Columns / Column Count |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `amazon_audio_video.csv` | Audio & Video | 0.47 MB | 2,773 | 2,760 | 7 columns: `Product Description`, `Price(Dollar)`, `Number of  reviews`, `Real price(Dollar)`, `Free days`, `Shipment`, `Delivery Date` |
| `amazon_camra.csv` | Cameras & Photography | 2.10 MB | 11,966 | 11,965 | 16 columns: `Product Description `, `Price(Dollar)`, `Number of reviews`, `Real price(Dollar)`, `Free days`, `Shipment`, `Delivery Date`, plus 9 trailing `Unnamed` artifact columns |
| `amazon_car_accessories.csv` | Car Accessories | 2.04 MB | 9,574 | 9,571 | 9 columns: `Production Description`, `Price(Dollar)`, `Number of  reviews`, `Real price(Dollar)`, `Free days`, `Shipment`, `Delivery Date`, `How many sell  in past month`, `Stock update` |
| `amazon_laptop.csv` | Laptops & Computers | 0.46 MB | 2,307 | 2,306 | 5 columns: `Product Description`, `Price(Dollar)`, `Number of  reviews`, `Free days`, `Shipment` |
| `amazon_men.csv` | Men's Clothing | 3.09 MB | 23,954 | 23,953 | 7 columns: `Product Description `, `Price(Dollar)`, `Number of reviews`, `Real price(Dollar)`, `Shipment`, `Delivery Date`, `How many sell  in past month` |
| `amazon_men_shoe.csv` | Men's Footwear | 2.76 MB | 23,745 | 23,744 | 7 columns: `Product Description `, `Price(Dollar)`, `Number of reviews`, `Real price(Dollar)`, `Shipment`, `Delivery Date`, `How many sell in past month` |
| `amazon_mobile.csv` | Mobiles & Accessories | 1.26 MB | 6,975 | 6,974 | 14 columns: `Product Description `, `Price(Dollar)`, `Number of reviews`, `Real price(Dollar)`, `Free days`, `Shipment`, `Delivery Date`, plus 7 trailing `Unnamed` artifact columns |
| `amazon_movies.csv` | Movies & Entertainment | 1.44 MB | 8,003 | 8,002 | 12 columns: `Product Description `, `Price(Dollar)`, `Quality`, `Release Year`, `Movie type`, `Actor`, `Director`, `Number of reviews`, `Real price(Dollar)`, `Free days`, `Shipment`, `Stock update` |
| `amazon_toys_1.csv` | Toys & Games | 2.51 MB | 11,404 | 11,403 | 10 columns: `Product Description `, `PriceDollar)`, `Number of reviews`, `Real priceDollar)`, `Free days`, `Shipment`, `Delivery Date`, `How many sell  in past month`, `Stock update`, `Age` |

---

## 3. Critical Data Engineering Insights (Identified in Phase 1)

1. **Character Encoding**:
   - Files are encoded in `latin1` (or Windows `cp1252`), NOT standard UTF-8. Attempting to parse with UTF-8 fails with byte decoding errors (`0x96`, `0xae`, `0x92`).
   
2. **Column Name Inconsistencies**:
   - **Text Description**: Found as `Product Description ` (trailing space in 6 files), `Product Description` (no trailing space in laptops/audio), and `Production Description` (typo in car accessories).
   - **Price**: Found as `Price(Dollar)` in most files, but `PriceDollar)` (missing opening parenthesis) in `amazon_toys_1.csv`.
   - **Reviews**: Found with single or double spaces (`Number of reviews` vs `Number of  reviews`).

3. **CSV Formatting & Stray Commas**:
   - Camera and mobile files contain unescaped commas inside descriptive fields, generating up to 9 `Unnamed: X` trailing columns.
   - A tiny fraction of rows (~20 out of 100,707 lines, <0.02%) have malformed delimiters that require `on_bad_lines='skip'` or robust quote handling.

4. **Category Association**:
   - The original CSV files do not contain an explicit `category` column; the category is strictly derived from the file name. The preprocessing pipeline in Phase 2 must inject normalized category names (e.g., `Audio & Video`, `Cameras`, `Car Accessories`, `Laptops`, `Men's Fashion`, `Men's Footwear`, `Mobiles`, `Movies`, `Toys & Games`).

5. **Currency & Localization**:
   - Raw prices are denominated in USD (`Price(Dollar)`). In accordance with the Indian e-commerce specification, Phase 2 will clean numeric prices and convert them to INR (₹) using a standard realistic conversion rate.
