import csv
import json
import math
import io
from scipy.stats import chi2
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.response import Response

#from benfordslaw import is_conforming
from waitress import serve

@view_config(route_name='benford', renderer='templates/home.html')
def benford(request):
    if 'csvfile' not in request.POST: # check if the file was uploaded
        return Response(json.dumps({'error': 'No file uploaded'}), status=400)
    
    csvfile = request.POST['csvfile'].file # get the uploaded csv file from post request
    csvreader = csv.reader(csvfile, delimiter=',')#csv.reader object is created called csvreader using csvfile 
    
    
    # Extract the first digit of each row in the CSV data
    digits = []
    for row in csvreader:
        if len(row) > 0:
            try:
                digit = int(str(row[0])[0])
                digits.append(digit)
            except ValueError:
                pass

    # Count the number of occurrences of each first digit
    counts = [0] * 9
    for digit in digits:
        counts[digit - 1] += 1

    # Calculate the expected frequency of each first digit according to Benford's law
    expected_frequencies = [0.0] * 9
    for i in range(1, 10):
        expected_frequencies[i - 1] = math.log10(1 + 1.0 / i) * len(digits)

    # Calculate the actual frequency of each first digit in the data
    actual_frequencies = [float(count) for count in counts]

    # Calculate the chi-squared statistic to compare the expected and actual frequencies
    chi_squared = sum([(actual_frequencies[i] - expected_frequencies[i]) ** 2 / expected_frequencies[i] for i in range(9)])

    # Calculate the degrees of freedom of the chi-squared distribution
    degrees_of_freedom = 9 - 1

    # Calculate the p-value of the chi-squared test
    p_value = 1 - chi2.cdf(chi_squared, degrees_of_freedom)
    
    # Check if the p-value is below the significance level of 0.05
    if p_value < 0.05:
        result = {'conforms': False, 'p_value': p_value}
    else:
        result = {'conforms': True, 'p_value': p_value}

    # Return the result as JSON
    return Response(json.dumps(result), content_type='application/json')
    
    


if __name__ == '__main__':
    config = Configurator()
    config.add_route('benford', '/benford')
    config.add_view(benford, route_name='benford', renderer='json')
    app = config.make_wsgi_app()
    serve(app, host='0.0.0.0', port=8080)