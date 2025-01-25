# Blood Bowl League Manager

This is a Django project for managing a Blood Bowl league. The app provides tools to organize matches, track team statistics, manage players, and handle league operations efficiently. It is designed for both casual leagues and competitive tournaments.

## Requirements

To run this project, you will need:

- Python 3.10 or higher

- Django 4.x

After running the database migrations, you can populate the database with initial data (factions, player types, and injury types) using the following command:

'''bash
python manage.py populate_initial_data
'''


## Features Developed So Far

### Team and Player Management

* Create and manage teams and their players.

* Track player statistics and attributes.

### Match Scheduling and Results

* Schedule matches between teams.

* Record match results, including casualties, weather conditions, and other relevant details.

### Stat Tracking

* Log stats like touchdowns, casualties, and injuries during matches, with detailed attribution to involved players.

### Team Statistics

* View team performance metrics and other statistics.

### Initial Leagues

* Track league results and standings.
  
## Features in the Pipeline

### League Management

* Create and manage leagues.

* Register teams in leagues.

### Player Level-Ups

* Implement functionality for leveling up players as they gain experience.

### CSS and Styling

* Improve the visual design of the app for a better user experience.

### User Authentication

* Add user login and management functionality to enable multi-user access and roles.

---

If you have any questions or run into issues, feel free to reach out or submit feedback!
