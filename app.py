from flask import Flask, render_template, request
from assay_pricer import AssayPricer

app = Flask(__name__)
pricer = AssayPricer()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the list of assays from the form
        assays_text = request.form.get('assays', '')
        # Split the text into a list of assays (handling both comma and newline separators)
        assays_list = [assay.strip() for assay in assays_text.replace('\n', ',').split(',') if assay.strip()]
        
        # Process the request using our existing pricer
        available, unavailable, total_cost = pricer.process_request(assays_list)
        
        return render_template('index.html', 
                             available=available, 
                             unavailable=unavailable, 
                             total_cost=total_cost,
                             assays_text=assays_text)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 