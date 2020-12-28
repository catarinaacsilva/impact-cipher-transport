# Key exchange server



## Requirements

- Flask
- Python

## Create a venv

1. `python3 -m venv venv`
2. `source venv/bin/activate`

# Test the main file (app.py)

1. Run app.py: `python app.py`

2. Open a terminal and: `curl -X POST -H "Content-Type: application/json" -d '{"id": "1", "pubkey": "anystring"}' localhost:5000/putkey`

3. Open browser on `http://127.0.0.1:5000/getkey/1`



## Authors

* **Catarina Silva** - [catarinaacsilva](https://github.com/catarinaacsilva)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details