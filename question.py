import csv
import pandas as pd
import matplotlib.pyplot as plt


def loading_through_csv(location):
    data = []
    try:
        with open(location, mode='r', newline='', encoding='utf-8') as data_file:
            reader = csv.reader(data_file)
            header = next(reader)  # Read the header row
            for line in reader:
                data.append(dict(zip(header, line)))  # Map each line to the header
    except FileNotFoundError:
        print(f"Error: The file {location} does not exist.")
    return data


def print_table(data):
    if not data:
        print("No data to display.")
        return

    keys = data[0].keys()
    max_lengths = {key: max(len(key), max(len(str(row[key])) for row in data)) for key in keys}

    print(" | ".join(key.ljust(max_lengths[key]) for key in keys))
    print("-+-".join('-' * max_lengths[key] for key in keys))

    for row in data:
        print(" | ".join(str(row[key]).ljust(max_lengths[key]) for key in keys))
    print()


def retrieve_by_oem_id(data, oem_id):
    result = []
    for record in data:
        if record.get('oem_id') == oem_id:
            result.append({
                'model_name': record.get('model_name'),
                'manufacturer': record.get('manufacturer'),
                'weight': record.get('weight'),
                'price': record.get('price'),
                'price_unit': record.get('price_unit')
            })
    return result


def retrieve_device_info_by_codename(data, codename):
    if not isinstance(data, list) or not all(isinstance(device, dict) for device in data):
        raise ValueError("Input data must be a list of dictionaries.")
    return [
        {
            'brand': device.get('brand'),
            'model_name': device.get('model'),
            'ram_capacity': device.get('ram_capacity'),
            'market_regions': device.get('market_regions'),
            'info_added_date': device.get('info_added_date')
        }
        for device in data
        if device.get('codename') == codename
    ]


def retrieve_device_info_by_ram_capacity(data, ram_capacity):
    result = []
    for device in data:
        if device['ram_capacity'] == ram_capacity:
            result.append({
                'oem_id': device['oem_id'],
                'released_date': device['released_date'],
                'announced_date': device['announced_date'],
                'dimensions': device['dimensions'],
                'device_category': device['device_category']
            })
    return result


def retrieve_with_condition(data):
    result = []
    for device in data:
        if int(device['display_refresh_rate']) > 90:
            result.append({
                'oem_id': device['oem_id'],
                'display_refresh_rate': int(device['display_refresh_rate']),
                'display_type': device['display_type'],
                'market_regions': device['market_regions']
            })
    return result


def loading_through_pandas(filepath):
    try:
        data = pd.read_csv(filepath, parse_dates=['released_date'])
        data['released_date'] = pd.to_datetime(data['released_date'], dayfirst=True, errors='coerce')
        return data
    except FileNotFoundError:
        print(f"Error: The file {filepath} does not exist.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()


def top_regions_for_brand(data, brand):
    brand_data = data[data['brand'] == brand]
    top_regions = brand_data['market_regions'].str.split(', ').explode().value_counts().head(5)
    return top_regions


def average_price_for_brand(data, brand):
    brand_data = data[data['brand'] == brand]
    average_price = brand_data.groupby('price_currency')['price'].mean()
    return average_price


def derive_screen_insights(data):
    data['pixel_density'] = (data['x_resolution'] ** 2 + data['y_resolution'] ** 2) ** 0.5 / data['display_diagonal']
    sorted_data = data.sort_values(by='pixel_density', ascending=False)
    max_pixel_density_device = sorted_data.iloc[0]
    return max_pixel_density_device


def custom_analysis(data):
    try:
        # Specify the date format to avoid warnings
        data['release_year'] = pd.to_datetime(data['released_date'], format='%d-%m-%y').dt.year
        devices_per_year = data['release_year'].value_counts().sort_index().reset_index()
        devices_per_year.columns = ['Year', 'Number of Devices']
        print(devices_per_year)
    except ValueError:
        # Handle case where the date format is incorrect
        print("Error: Incorrect date format in 'released_date' column. Please ensure dates are in 'YYYY-MM-DD' format.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def create_ram_type_chart(data):
    ram_type_counts = data['ram_type'].value_counts()
    colors = ['skyblue', 'lightcoral', 'lightgreen', 'lightsalmon', 'lightblue']
    plt.figure(figsize=(8, 8))
    plt.pie(ram_type_counts, labels=ram_type_counts.index, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.title('Proportion of RAM Types for Devices in the Current Market')
    plt.show()


def create_usb_connector_chart(data):
    usb_connector_counts = data['usb_connector'].value_counts()
    plt.figure(figsize=(10, 6))
    usb_connector_counts.plot(kind='bar', color='skyblue')
    plt.title('Number of Devices for Each USB Connector Type')
    plt.xlabel('USB Connector Type')
    plt.ylabel('Number of Devices')
    plt.xticks(rotation=45, ha='right')
    plt.show()


def convert_to_gbp(row):
    if row['price_currency'] != 'GBP':
        return row['price'] * 0.85
    return row['price']


def create_price_trends_charts(data):
    data['price_gbp'] = data.apply(convert_to_gbp, axis=1)
    data['year'] = pd.to_datetime(data['released_date']).dt.year
    for year in range(2020, 2024):
        year_data = data[data['year'] == year]
        monthly_avg_price = year_data.groupby(pd.to_datetime(year_data['released_date']).dt.month)['price_gbp'].mean()
        plt.figure(figsize=(10, 6))
        plt.plot(monthly_avg_price.index, monthly_avg_price.values, marker='o', label=f'Year {year}')
        plt.title(f'Monthly Average Price Trends (GBP) - {year}')
        plt.xlabel('Month')
        plt.ylabel('Average Price (GBP)')
        plt.legend()
        plt.show()


def create_scatter_plot(data):
    if 'weight' not in data.columns or 'price' not in data.columns:
        print("Data does not contain required columns: 'weight' and 'price'.")
        return
    plt.figure(figsize=(10, 6))
    plt.scatter(data['weight'], data['price'], alpha=0.5)
    plt.title('Scatter Plot: Device Weight vs. Price')
    plt.xlabel('Device Weight (grams)')
    plt.ylabel('Device Price')
    plt.show()


def average_weight_per_brand(data):
    average_weights = data.groupby('brand')['weight'].mean()
    return average_weights


def create_average_weight_chart(data):
    avg_weight_per_brand = data.groupby('brand')['weight'].mean()
    plt.figure(figsize=(10, 6))
    avg_weight_per_brand.plot(kind='bar', color='lightblue')
    plt.title('Average Weight of Devices per Brand')
    plt.xlabel('Brand')
    plt.ylabel('Average Weight (grams)')
    plt.xticks(rotation=45, ha='right')
    plt.show()
