# File: server.py
# Date Created: 2025-01-08
# Description: This Flask application provides an endpoint (`/fetch_data`) to fetch, filter, and sort financial data.
# It retrieves data from the Financial Modeling Prep API, processes it based on query parameters, and returns the filtered 
# and sorted data as a JSON response. The app also supports Cross-Origin Resource Sharing (CORS) for frontend integration.

from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os
from flask_cors import CORS  # Import CORS to handle cross-origin requests
import requests
from waitress import serve  # Import Waitress for production server compatibility on Windows


# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes to allow requests from different origins

# API Key and URL for fetching data from the Financial Modeling Prep API
load_dotenv()
API_KEY = os.getenv("API_KEY")  # Replace with your actual API key
API_URL = f"https://financialmodelingprep.com/api/v3/income-statement/AAPL?period=annual&apikey={API_KEY}"

# Endpoint to fetch financial data, filter, and sort based on query parameters
@app.route("/fetch_data", methods=["GET"])
def fetch_data():
    # Fetch data from the Financial Modeling Prep API
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an error if the API response is not successful
        data = response.json()  # Parse the JSON response
    except requests.exceptions.RequestException as e:
        # Return an error message if the API request fails
        return jsonify({"error": str(e)}), 500

    # Extract query parameters from the request URL
    start_date = request.args.get("startDate", type=int)
    end_date = request.args.get("endDate", type=int)
    min_revenue = request.args.get("minRevenue", type=float)
    max_revenue = request.args.get("maxRevenue", type=float)
    min_net_income = request.args.get("minNetIncome", type=float)
    max_net_income = request.args.get("maxNetIncome", type=float)
    sort_by = request.args.get("sortBy", default="date", type=str)

    # Filter the data based on the provided query parameters
    filtered_data = filter_data(data, start_date, end_date, min_revenue, max_revenue, min_net_income, max_net_income)

    # Sort the filtered data based on the selected sort option
    if sort_by == "date":
        filtered_data = sorted(filtered_data, key=lambda x: x["date"], reverse=True)
    elif sort_by == "revenue":
        filtered_data = sorted(filtered_data, key=lambda x: x["revenue"], reverse=True)
    elif sort_by == "netIncome":
        filtered_data = sorted(filtered_data, key=lambda x: x["netIncome"], reverse=True)

    # Return the filtered and sorted data as a JSON response
    return jsonify(filtered_data)

# Helper function to filter data based on the provided parameters
def filter_data(data, start_date, end_date, min_revenue, max_revenue, min_net_income, max_net_income):
    filtered = []
    for item in data:
        # Apply filtering conditions based on the query parameters
        if start_date and item["date"] < start_date:
            continue
        if end_date and item["date"] > end_date:
            continue
        if min_revenue and item["revenue"] < min_revenue:
            continue
        if max_revenue and item["revenue"] > max_revenue:
            continue
        if min_net_income and item["netIncome"] < min_net_income:
            continue
        if max_net_income and item["netIncome"] > max_net_income:
            continue
        filtered.append(item)  # Add the item to the filtered list if all conditions are met
    
    return filtered

# Run the Flask app using Waitress for production compatibility on Windows
if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)  # Waitress will handle the serving of the app
