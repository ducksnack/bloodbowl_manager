# Blood Bowl League Manager

This is a Django project for managing a Blood Bowl league. The app provides tools to organize matches, track team statistics, manage players, and handle league operations efficiently. It is designed for both casual leagues and competitive tournaments.

## Requirements

To run this project, you will need:

- Python 3.10 or higher

- Django 4.x

After running the database migrations, you can populate the database with initial data (factions, player types, and injury types) using the following command:

python manage.py populate_initial_data


## Features Developed So Far

### Team and Player Management

* Create and manage teams and their players.

* Track player statistics and attributes.

* Level up players

### Match Scheduling and Results

* Schedule matches between teams.

* Record match results, including casualties, weather conditions, and other relevant details.

### Stat Tracking

* Log stats like touchdowns, casualties, and injuries during matches, with detailed attribution to involved players.

### Team Statistics

* View team performance metrics and other statistics.

### League Management

* Create and manage leagues.

* Register teams in leagues.
  
* Track league results and standings.
  
## Features in the Pipeline

### Match features

* Add option to add Injuries to players during a match, unrelated to caused casualties (e.g. from failed dodges)

### CSS and Styling

* Improve the visual design of the app for a better user experience.

### User Authentication

* Add user login and management functionality to enable multi-user access and roles.
