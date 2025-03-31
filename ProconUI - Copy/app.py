from flask import Flask, redirect, request, render_template_string, url_for
import subprocess
import os
import time
import uuid

app = Flask(__name__)

used_ports = set()
base_frontend_port = 3100
base_backend_port = 5100
base_couchdb_port = 6000
base_redis_port = 6400

def get_next_available_port(base_port):
    port = base_port
    while port in used_ports:
        port += 1
    used_ports.add(port)
    return port

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        unique_id = uuid.uuid4().hex[:8]

        frontend_port = get_next_available_port(base_frontend_port)
        backend_port = get_next_available_port(base_backend_port)
        couchdb_port = get_next_available_port(base_couchdb_port)
        redis_port = get_next_available_port(base_redis_port)

        env = os.environ.copy()
        env.update({
            "FRONTEND_PORT": str(frontend_port),
            "BACKEND_PORT": str(backend_port),
            "COUCHDB_PORT": str(couchdb_port),
            "REDIS_PORT": str(redis_port),
            "STACK_ID": unique_id
        })

        compose_file_path = r"C:\Users\Henok\Desktop\system_managemnt_tool\docker-compose.yml"
        docker_compose_path = r"C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe"

        try:
            result = subprocess.run(
                [docker_compose_path, "-f", compose_file_path, "-p", f"stack_{unique_id}", "up", "-d"],
                check=True,
                capture_output=True,
                text=True,
                env=env
            )
            print("stdout:", result.stdout)
            print("stderr:", result.stderr)

            time.sleep(5)

            return redirect(f"http://localhost:{frontend_port}")
        except subprocess.CalledProcessError as e:
            print("Error:", e.stderr)
            return f"Error running docker-compose: {e.stderr}", 500
        except Exception as e:
            print("Unexpected error:", e)
            return f"Unexpected error: {e}", 500

    # Updated subscription page with a company look, screenshots and a payment form
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Company Name - Subscribe to Task Management App</title>
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
      <style>
        body {
          background-color: #f8f9fa;
        }
        .subscription-container {
          margin: 50px auto;
          background-color: #ffffff;
          padding: 30px;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .logo {
          width: 150px;
        }
        .screenshot {
          max-width: 100%;
          height: auto;
          border: 1px solid #ddd;
          border-radius: 4px;
          margin-bottom: 15px;
        }
        .payment-form {
          background-color: #f1f1f1;
          padding: 20px;
          border-radius: 12px;
        }
      </style>
    </head>
    <body>
      <div class="container subscription-container">
        <div class="row">
          <!-- Left Column: Company information, description and screenshots -->
          <div class="col-md-6">
            <img src="{{ url_for('static', filename='logo.png') }}" alt="Company Logo" class="logo mb-4">
            <h2>Subscribe to Our Task Management App</h2>
            <p class="text-muted">
              Experience a seamless task management system that empowers your team to collaborate and achieve more.
              Our platform provides intuitive interfaces, real-time updates, and robust tools to help you stay organized.
            </p>
            <h4>Screenshots:</h4>
            <img src="{{ url_for('static', filename='screenshot1.png') }}" alt="Screenshot 1" class="screenshot">
            <img src="{{ url_for('static', filename='screenshot2.png') }}" alt="Screenshot 2" class="screenshot">
          </div>
          <!-- Right Column: Payment form -->
          <div class="col-md-6">
            <div class="payment-form">
              <h4>Payment Details</h4>
              <form method="post">
                <div class="mb-3">
                  <label for="cardNumber" class="form-label">Card Number</label>
                  <input type="text" class="form-control" id="cardNumber" name="cardNumber" placeholder="Enter card number" required>
                </div>
                <div class="mb-3">
                  <label for="expiryDate" class="form-label">Expiry Date</label>
                  <input type="text" class="form-control" id="expiryDate" name="expiryDate" placeholder="MM/YY" required>
                </div>
                <div class="mb-3">
                  <label for="cvv" class="form-label">CVV</label>
                  <input type="text" class="form-control" id="cvv" name="cvv" placeholder="CVV" required>
                </div>
                <button type="submit" class="btn btn-primary">Subscribe Now</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(port=4000, debug=True)
