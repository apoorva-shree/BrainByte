from flask import Flask, request, render_template
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/donate", methods=["GET", "POST"])
def donate():
    if request.method == "POST":
        name = request.form["name"]
        contact = request.form["contact"]
        food_type = request.form["food_type"]
        quantity = request.form["quantity"]
        location = request.form["location"]
        expiry_time = request.form["expiry_time"]

        # Handle image upload
        food_image = request.files["food_image"]
        image_path = os.path.join(UPLOAD_FOLDER, food_image.filename)
        food_image.save(image_path)

        # Optional: run freshness detection
        freshness = predict_freshness(image_path)

        return f"Thank you {name}! Food is {freshness} and will be picked up soon."

    return render_template("donate.html")

app.run(debug=True)