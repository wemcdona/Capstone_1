# Crunchylist

Crunchylist is a website used as a tracker for anime. It allows users to create a list of the anime they are watching by pulling data from the anime list of the Kitsu API and adding it to their own personal list. The website utilizes a database to store user lists and usernames.

## Features

- **User Authentication:** Users can sign up with an email, username, password, and an optional profile picture.
- **Profile Management:** Users can edit their profile information.
- **Anime List Management:** Users can add, view, and delete anime from their personal list.
- **Limited API:** The available anime for adding and removing is limited due to the constraints of the Kitsu API.

## Getting Started

To get started with Crunchylist, follow these steps:

1. Clone this repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Set up a PostgreSQL database and configure the connection in `config.py`.
4. Run `python app.py` to start the Flask application.
5. Access the website through your browser.

## Technologies Used

- HTML
- CSS
- Python
- Flask
- Flask-WTF
- PostgreSQL

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).