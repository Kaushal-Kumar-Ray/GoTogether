from backend.app import create_app

app = create_app()

@app.route("/health")
def health():
    return "Status: All Servers are healthy and running smoothly!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)