from flask import Flask, render_template
from flask import jsonify
from rate_limiter import RateLimiter

app=Flask(__name__)
rate_limiter = RateLimiter(limit=5,window_size=60)
rate_limiter.initialize()

@app.route('/')
def index():
    try:
        if rate_limiter.allow_request():
            return render_template('index.html')
            #return jsonify({"message": "Access granted"})
        else:
            return render_template('error.html')
            #return jsonify({"error": "Rate limit exceeded"}), 429  # Return 429 Too Many Requests status code
    except RuntimeError as e:
        return jsonify({"error": f"Rate limiter error: {e}"}), 500
        

if __name__ == '__main__':
    app.run(debug=True)
