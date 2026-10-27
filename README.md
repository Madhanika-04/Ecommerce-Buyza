# E-Commerce Recommendation System

An end-to-end, Indian-localized E-Commerce application with Content-Based Recommendation powered by TF-IDF Vectorization and Cosine Similarity, built with a FastAPI backend and a React/Vite frontend.

---

## 📌 Project Architecture

```
                                  +------------------------------------+
                                  |     React 18 + Vite Frontend       |
                                  |  (Indian UI, ₹ INR, Cart, Wishlist)|
                                  +-----------------+------------------+
                                                    | REST API (Axios)
                                                    v
                                  +------------------------------------+
                                  |       FastAPI Backend API          |
                                  |  (Catalog, Filtering, Pydantic)   |
                                  +--------+------------------+--------+
                                           |                  |
                    +----------------------+                  +----------------------+
                    |                                                                |
                    v                                                                v
+---------------------------------------+                      +---------------------------------------+
|          MongoDB Database             |                      |        ML Recommendation Engine       |
| (Cart, Wishlist, Orders, Persistence) |                      | (TF-IDF Vectorizer + Cosine Sim Query)|
+---------------------------------------+                      +---------------------------------------+
```

---

## 🛠️ Technology Stack

- **Data Science & ML**: Python 3.11, Pandas, NumPy, Scikit-learn, TF-IDF Vectorizer, Cosine Similarity, Joblib, Matplotlib, Seaborn
- **Backend**: FastAPI, Uvicorn, Pydantic v2, PyMongo, MongoDB Server v8.0
- **Frontend**: React (Vite), JavaScript, Tailwind CSS, Lucide Icons, Axios, React Router
- **Testing & Tools**: Pytest, Jupyter Notebooks, Git

---

## 📂 Project Directory Structure

```
ecommerce-recommendation-system/
├── data/
│   ├── raw/                           # Original Kaggle CSV files (9 categories)
│   ├── processed/                     # Cleaned and unified product catalog
│   └── README.md                      # Dataset schemas and metadata
├── notebooks/
│   ├── 01_dataset_inspection.ipynb     # Phase 1: Exploration of raw CSVs & schemas
│   ├── 02_data_cleaning.ipynb         # Phase 2: Missing values, normalization, formatting
│   ├── 03_exploratory_data_analysis.ipynb # Phase 3: Category, price & text distributions
│   ├── 04_feature_engineering.ipynb   # Phase 4: Text representation & TF-IDF matrix
│   └── 05_recommendation_evaluation.ipynb # Phase 5: Evaluation & Cosine Similarity checks
├── src/
│   ├── data/                          # Data loading & cleaning pipeline scripts
│   ├── features/                      # TF-IDF vectorization & feature transformers
│   ├── models/                        # Scalable query-specific cosine similarity engine
│   ├── evaluation/                    # Diversity, coverage, and similarity metrics
│   └── utils/                         # Helper functions & Indian currency conversions
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entrypoint & CORS configuration
│   │   ├── api/                       # API route handlers (products, recommendations, cart, etc.)
│   │   ├── core/                      # Settings, logging, and environment configuration
│   │   ├── db/                        # MongoDB client connection & indexes
│   │   ├── schemas/                   # Pydantic request & response models
│   │   └── services/                  # Recommendation service & catalog queries
│   ├── tests/                         # Pytest test suite for API & ML integration
│   ├── requirements.txt               # Backend dependencies
│   └── .env.example                   # Environment configuration template
├── frontend/                          # React + Vite Indian E-Commerce user interface
├── artifacts/                         # Saved TF-IDF vectorizer and sparse feature matrix
├── reports/
│   └── figures/                       # Exported EDA plots (distributions, counts)
├── docs/                              # Technical documentation & API specs
├── scripts/
│   └── inspect_dataset.py             # Phase 1 automated schema inspector
├── tests/                             # Root unit & integration tests
├── .gitignore                         # Comprehensive ignore rules
├── pyproject.toml                     # Python packaging & tool configuration
└── README.md                          # Main project guide
```

---

## 📊 Dataset: 100k Amazon Products

Source: [Kaggle - A Comprehensive Dataset of 100k Amazon Products](https://www.kaggle.com/datasets/joyshil0599/a-comprehensive-dataset-of-100k-amazon-products)

| File Name | Domain / Category | Rows |
| :--- | :--- | :--- |
| `amazon_audio_video.csv` | Audio & Video | 2,760 |
| `amazon_camra.csv` | Cameras & Accessories | 11,965 |
| `amazon_car_accessories.csv` | Automotive & Car Accessories | 9,571 |
| `amazon_laptop.csv` | Laptops & Computers | 2,306 |
| `amazon_men.csv` | Men's Clothing | 23,953 |
| `amazon_men_shoe.csv` | Men's Footwear | 23,744 |
| `amazon_mobile.csv` | Mobiles & Tablets | 6,974 |
| `amazon_movies.csv` | Movies & Cinema | 8,002 |
| `amazon_toys_1.csv` | Toys & Games | 11,403 |
| **Total** | **9 Categories** | **100,678 Records** |

---

## 🚀 Execution & Verification

### Run Dataset Inspection:
```powershell
python scripts/inspect_dataset.py
```

### Git Repository Status:
- Remote: `https://github.com/Madhanika-04/Ecommerce-Buyza.git`
