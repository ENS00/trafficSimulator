# version 1.3.1
## Added:
- Fix too many crashes due to rear-end collisions

# version 1.3
## Added:
- Bug fixed, from now a car that has to turn left, starts to turn earlier, to get a better trajectory
- Bug fixed, the duration of the traffic light didn't respect the configuration provided by the user
- Drunkenness, tiredness, seniority, tire wear, broken brakes and rain affect vehicles

# version 1.2.6
## Added:
- Added options to better control traffic lights
- Bug fixed, if you choose to never turn off the traffic light, it now works as expected
- Added characteristics that influence the driver and the vehicle, drunkenness, tiredness, seniority, tire wear, broken brakes and rain
- **N.B.** At the moment only drunkenness and broken brakes affect the movement of the vehicle

# version 1.2.5
## Added:
- Panels updated
- More info on csv outputs
- Vehicles do not generate agglomerations anymore

# version 1.2.4
## Added:
- Fixed a rare bug where the simulator was unable to assign a color to a car
- Fixed a bug: when the user chose the largest spawn frequency value, it actually generated fewer cars
- Added new panels!
- Panels support multi-line text
- Drivers now drive even better

# version 1.2.3
## Added:
- Moved methods from [position.py](./position.py) to [const.py](./const.py)
- Moved class Waypoint from [position.py](./position.py) to [objects.py](./objects.py)
- Other options are customizable by the user
- Performance improvements
- Removed the threading system because it is less performing
- Many bugs fixed

# version 1.2.2
## Added:
- Handling output exceptions and errors
- Data collected per hour

# version 1.2.1
## Added:
- Spawn rate using peak times (maybe to revise)
- Defined data to be saved in file/DB
- First tests for the output
- User can now personalize in [configuration.ini](configuration.ini):
  * Start time of simulation
  * Adjust spawn quantity (increase/decrease cars generated)

# version 1.2.0
## Added:
- Vehicle that has to turn left, awaits some time and if he can't still turn, he will choose to go straight instead
- Vehicle movement is managed by an asynchronous process, so it's untied from render process (closely related with fps)
- Easy [configuration file](configuration.ini) for common users
- Now the simulator uses only default font
- UI classes
- Little fixes

# version 1.1.1
## Added:
- Vehicle that has to turn left, awaits some time and if he can't still turn, he will choose to go straight instead

# version 1.1.0
## Added:
- Vehicle movement is more detailed and precise
- Vehicle checks to its left before the turn
- The Collision Prediction algorithm has been replaced with another more performing calculation
- Vehicles can no longer spawn on each other
- Added option to disable *autospawn* and control whenever spawn a vehicle
- Window positioning

# version 1.0.0
## Added:
- Version system + changelog file
- Code rearrangement
- Graphic Library moved from [tkinter](https://docs.python.org/3/library/tkinter.html) to [pygame](https://www.pygame.org/)
- New time management: game is **syncronized** and when the game "*lags*" the time is slowed down as well
- When the car turns, the position is calculed using [Ackermann steering geometry](https://en.wikipedia.org/wiki/Ackermann_steering_geometry)
- The color of the car is now determined by a normal distribution
- Little bug fix

As a consequence to these changes, the performance has definitely improved, you don't notice the lag although there is a little
