# version 1.1.0
## Added:
- Vehicle movement is more detailed and precise
- Vehicle checks to its left before the turn
- The Collision Prediciton algorithm has been replaced with another more performing calculation
- Vehicles can no longer spawn on each other
- Added option to disable *autospawn* and control whenever spawn a vehicle

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

---

## Things To Do:
- Move classes in different files to simplify management
- Suitably move methods away from [position.py](./position.py)
- Improve prediction collision (and how avoid it!)
- Make some tests with different resolutions
- Create a class to delegate the task of redirecting the output