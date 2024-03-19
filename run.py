from app import app
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("サーバ起動成功: http://localhost:5000/")
    app.run(debug=True, host="0.0.0.0", port=5000)
