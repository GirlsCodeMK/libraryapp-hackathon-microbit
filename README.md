# Setup
To set up this project on your own machine, perform these steps.

1. Fork this repository, then clone it. Fork it via the GitHub website, then clone it with either GitHub desktop or the command line (if you've got the ssh keys set up)
```
$ git clone git@github.com:mygithubusernae/libraryapp-hackathon-microbit.git
```
(Use the address of your fork of this repo: you'll need to change `mygithubusername` in the line above.)

2. Once you have a copy of the repository, open a terminal in that directory
```    
$ cd /path/to/libraryapp-hackathon-microbit/
```

3. Once there, create and activate a virtual environment for the project    
```    
$ python3 -m venv gcmb
$ source gcmb/bin/activate
```

(If you're on Windows using the `cmd` terminal, the command is
```
$ ./gcmb/Scripts/activate
```
If you're on Windows using the _Git Bash_ terminal, the command is
```
$ source gcmb/Scripts/activate
```
)

4. Install the required libraries, such as PySerial
```    
(gcmb) $ pip install -r requirements.txt
```

5. You'll also need to install the [Mu editor](https://codewith.mu/en/download). If you're on Windows or a Mac, download the installer. If you're on something else, install Mu with
```    
(gcmb) $ pip install mu-editor
```

# What's what
There are three directories in the repository: `host-pc`, `central-microbit`, and `remote-microbit`.

`host-pc` contains the code that runs on the central PC. The code on this PC does several jobs:
* it reads from the website API, to find all the known microbits
* it creates the messages and sends them to the `central-microbit` for sending
* it receives responses from the microbit
* if necessary, it updates the `last_microbit_update` field on the website

`central-microbit` is connected to the `host-pc` by a USB cable. It simply takes the messages sent to it by the `host-pc`, broadcasts them with the radio, and sends back any messages it receives.

There will be several `remote-microbit`s. Each is attached to a book copy or a person. When it receives a radio messages for that microbit, it finds the message and displays it. It then sends back an `ack` message to say that it's been received. 

# Setting up the microbits
### Channels
There will be several different groups working on their own microbits. To avoid people interfering with each other, set the `channel` in the top of the microbit scripts to something distinct. The [microbit radio documentation](https://microbit-micropython.readthedocs.io/en/latest/radio.html) says you can go from 0 to 83, so there's plenty of space. Try to ensure your channel is a good few different from anyone else's.

Each microbit will need its own code flashing on to it.

### IDs
Each `remote-microbit` has its own ID number, so remember to reset it when you flash the code onto each microbit. 

### Telling the database about microbits
Currently, book copies and users can be associated with microbits. Use the admin panel (probably at `http://localhost:8000/admin`) to add microbits to the ones you want. Use the same IDs as you did when you flashed the code to the remote microbits!

### Users and tokens
You'll need to create a user with write access to the web app, so that the `host-pc` script can update the database when it's found a microbit. Create that user through the admin panel (probably at `http://localhost:8000/admin`) and then create an `Auth Token` for the user. 

Once you've done that, add your token to the details in `write_config.py`. Run that script then you'll be able to have your `host-pc` script talk to the local copy of the library database. 

When you want to connect to the live system on Heroku, log in to the [Library app admin page](https://fathomless-scrubland-17825.herokuapp.com/admin/) and find the token you're after.

Please don't add the tokens into source control!

### Running everything
Connect a battery pack to each remote microbit and physically attach it to the appropriate book or person. (When the microbit restarts, it should say `Waiting 3` or something, with the number being its ID). 

Connect the central microbit to the the host pc by the USB cable. Your PC may suggest opening files on the microbit: do so.

Run the host pc script, 
```    
(gcmb) $ python host-pc/host_api_reader_async.py
```

and it should start spewing out a trace of what it's doing. You'll almost certainly need to change the setting of `port` at the top of the script to be where your PC thinks the microbit is attached.

# Making changes

Let's say you want to make a change/enhancement/extension to the app.

## Setup
You only need do this once.

Create a new `remote` link, called `upstream`, that points to the original repository. This will allow you to keep up to date with ongoing changes that others have made. (You have to do this on the command line: GitHub desktop doesn't support this.)
```
(gcmb) $ git remote add upstream https://github.com/GirlsCodeMK/libraryapp-hackathon-microbit.git
```

## Starting work
Before you start work, ask around to make sure no-one else is working on that feature!

1. Make sure your local copy of your repository is up-to-date by `pull`ing any changes.
```
(gcmb) $ git checkout master
(gcmb) $ git fetch upstream
(gcmb) $ git merge --ff-only upstream/master
```

2. Create and checkout a new branch for your feature. Call the branch anything you want, but you may want to include your name and/or the issue number (if you're addressing [an open issue on the project](https://github.com/GirlsCodeMK/libraryapp-hackathon-python-starthere/issues)).
```
(gcmb) $ git branch cool-feature
(gcmb) $ git checkout cool-feature
```
(You can do both of these steps as one with `git checkout -b cool-feature`)

3. Do some work on this feature. Make commits often, as is good Git practice.

4. Sooner or later (and preferably sooner), you'll want to `push` these commits to your own repository. The _first_ time you do this, you need to tell Git to create a new branch in your remote `origin` repository on GitHub.
```
(gcmb) $ git push --set-upstream origin cool-feature
```

5. As you continue to work, make more commits and push them.
```
(gcmb) $ git push origin cool-feature
```

## Getting your changes accepted
Once you've finished your cool feature, it's time to get it accepted into the main project.

1. Check that the main `master` hasn't changed while you've been working.
```
(gcmb) $ git checkout master
(gcmb) $ git fetch upstream
(gcmb) $ git merge --ff-only upstream/master
```
As you've not changed our local copy of `master`, there should be no conflicts here.

2. Merge the newly-updated `master` into your feature branch
```
(gcmb) % git checkout cool-feature
(gcmb) % git merge master
```
(If you're feeling confident about what you're doing, you can `rebase` your changes instead of `merge`ing them.)

3. Fix any conflicts between your changes and the updates in `master`. Once you're done, commit the changes back to your feature branch. (Git is helpful here in guiding you through the process.)

4. Push your changes back up to your repository
```
(gcmb) $ git push origin cool-feature
```

5. On the GitHub website, find the big green "New pull request" button to ask for your changes to be included into main repository.

6. That's all you need do: someone else will look at your changes and advise you on what happens next. Your changes could be accepted as-is, or the review could suggest some improvements to make to your feature. 


## Logging
The development system is set up to [log some messages to the console](https://docs.djangoproject.com/en/2.1/topics/logging/) (the same terminal where the messages appear from `runserver`). At the moment, logging is only active for calls in the `views.py` file. 

To log a step of a function, include the line
```
logger.warning('copy delete args: ' + str(self.kwargs))
```
...and the message will appear when the function is used.

Note that the argument to `logger` must be a single `str`ing, so you need to convert non-`str`ing arguments for `logger`.

# Links

The [Django documentation](https://docs.djangoproject.com/en/2.1/) is essential reading, including the [Django "getting started" tutorial](https://docs.djangoproject.com/en/2.1/intro/).

This application is based on the [DjangoGirls tutorial system](https://tutorial.djangogirls.org/en/) and the [Mozilla Development tutorial](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Tutorial_local_library_website).
