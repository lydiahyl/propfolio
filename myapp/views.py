from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import pandas as pd
import json
from .models import Data

def index(request):
    """Display the main dashboard with data table and charts"""
    data_objects = Data.objects.all()
    context = {'data_objects': data_objects}
    return render(request, 'myapp/index.html', context)

def upload_csv(request):
    """Handle CSV file upload and data processing"""
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, 'No file selected. Please choose a CSV file to upload.')
            return redirect('myapp:index')
        
        file = request.FILES['file']
        
        # Validate file type
        if not file.name.endswith('.csv'):
            messages.error(request, 'Invalid file type. Please upload a CSV file.')
            return redirect('myapp:index')
        
        try:
            # Clear previous data
            Data.objects.all().delete()
            
            # Read and process CSV
            df = pd.read_csv(file)
            
            # Validate required columns
            required_columns = ['property_name', 'property_price', 'property_rent', 'emi', 'tax', 'other_exp']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                messages.error(request, f'Missing required columns: {", ".join(missing_columns)}')
                return redirect('myapp:index')
            
            json_records = df.reset_index().to_json(orient='records')
            data = json.loads(json_records)
            
            # Process and save data
            for d in data:
                name = d['property_name']
                price = d['property_price']
                rent = d['property_rent']
                emi = d['emi']
                tax = d['tax']
                exp = d['other_exp']
                expenses_monthly = emi + tax + exp
                income_monthly = rent - expenses_monthly
                
                Data.objects.create(
                    name=name, 
                    price=price, 
                    rent=rent,
                    emi=emi, 
                    tax=tax, 
                    exp=exp, 
                    expenses_monthly=expenses_monthly, 
                    income_monthly=income_monthly
                )
            
            messages.success(request, f'Successfully uploaded and processed {len(data)} properties.')
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            
    return redirect('myapp:index')

def clear_data(request):
    """Clear all property data"""
    if request.method == 'POST':
        Data.objects.all().delete()
        messages.success(request, 'All property data has been cleared.')
    return redirect('myapp:index')

# Keep the old view for backward compatibility
def hello(request):
    """Redirect to the new index view"""
    return redirect('myapp:index')