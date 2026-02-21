# src/data/processor.py
import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data-processor')

def load_data(file_path):
    """Load data from a CSV file."""
    logger.info(f"Loading data from {file_path}")
    return pd.read_csv(file_path)

def clean_data(df):
    """Clean the dataset by handling missing values, outliers, and performing feature engineering."""
    logger.info("Cleaning and engineering dataset")
    
    # Make a copy to avoid modifying the original dataframe
    df_cleaned = df.copy()
    
    # Handle missing values
    for column in df_cleaned.columns:
        missing_count = df_cleaned[column].isnull().sum()
        if missing_count > 0:
            logger.info(f"Found {missing_count} missing values in {column}")
            if pd.api.types.is_numeric_dtype(df_cleaned[column]):
                median_value = df_cleaned[column].median()
                df_cleaned[column] = df_cleaned[column].fillna(median_value)
            else:
                mode_value = df_cleaned[column].mode()[0]
                df_cleaned[column] = df_cleaned[column].fillna(mode_value)
    
    # Handle outliers in price (target variable)
    Q1 = df_cleaned['price'].quantile(0.25)
    Q3 = df_cleaned['price'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    df_cleaned = df_cleaned[(df_cleaned['price'] >= lower_bound) & 
                            (df_cleaned['price'] <= upper_bound)]
    logger.info(f"Removed outliers. New shape: {df_cleaned.shape}")

    # --- Feature Engineering (from Notebook 02) ---
    logger.info("Performing feature engineering")
    from datetime import datetime
    df_cleaned['house_age'] = datetime.now().year - df_cleaned['year_built']
    df_cleaned['price_per_sqft'] = df_cleaned['price'] / df_cleaned['sqft']
    df_cleaned['bed_bath_ratio'] = df_cleaned['bedrooms'] / df_cleaned['bathrooms']
    df_cleaned['bed_bath_ratio'] = df_cleaned['bed_bath_ratio'].replace([np.inf, -np.inf], np.nan).fillna(0)

    # --- Categorical Encoding ---
    logger.info("Encoding categorical variables")
    # Convert 'location' and 'condition' to dummy variables (One-Hot Encoding)
    df_cleaned = pd.get_dummies(df_cleaned, columns=['location', 'condition'], prefix=['loc', 'cond'])
    
    # Drop rows with NaN in price (target) just in case
    df_cleaned = df_cleaned.dropna(subset=['price'])
    
    return df_cleaned

def process_data(input_file, output_file):
    """Full data processing pipeline."""
    # Create output directory if it doesn't exist
    output_path = Path(output_file).parent
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load data
    df = load_data(input_file)
    logger.info(f"Loaded data with shape: {df.shape}")
    
    # Clean data
    df_cleaned = clean_data(df)
    
    # Save processed data
    df_cleaned.to_csv(output_file, index=False)
    logger.info(f"Saved processed data to {output_file}")
    
    return df_cleaned

if __name__ == "__main__":
    # Example usage
    process_data(
        input_file="data/raw/house_data.csv", 
        output_file="data/processed/cleaned_house_data.csv"
    )
