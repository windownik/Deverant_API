<div align="center">
  <img alt="Deverant logo" src="https://i.postimg.cc/wvhDZTPn/Deverant.png" width="400px" />

  # Our service is diary for your incomes
  # Welcome to Deverant API
  # Version: 0.0.1.1 Alfa
</div>

# About Deverant
Our service is diary for your incomes. Our service allows you to manage your projects while you work. Keep track of the time spent on each project and each task. You can also determine the cost of your development hour on each project.
# Links
Our API running on Heroku

Documentation:

https://deverant-server.herokuapp.com/redoc

https://deverant-server.herokuapp.com/docs

# What does this API can:
Create new account, of course you can log in and log out.

At first you can create new project and create new tasks in this project. In this version every project must have tasks. When you create task you can write worktime logs. 

Worktime log is information when you started working on the task and finished. After you create worktime log, our service calculate how long time you work on every project and every task in project. If you don't know what is your price hour - Deverant calculate it for you.

Currency - Default USD. This param you can change after project creation. In this version service can't exchange money automatically.

All functions of our service available for log in users.

# Whats new in version 0.0.1.1 Alfa

Rework automaticall documentation.

# Fly to version 0.0.2 Alfa
Create email confirm for new users. 

Add endpoint for update password. 

Add endpoint for update user's default currency.

Create user's default currency param.

Create automatic exchange for user's statistic endpoint.

Create automatically delete old (more 30 days) tokens