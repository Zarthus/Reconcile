#!/bin/bash

function help() {
  echo "\
Usage: $0 [OPTIONS].

Starts the python bot in a screen session if it is not already running.

  -d,  --daemon      launch the bot but don't attach to the created screen (mostly for use by the init script).
  -h,  --help        display this help file.
  -k,  --kill        kill the process the bot is using, this is not a graceful way of exiting,
                      use of the bots actual functions are recommended.
  -p,  --python      use the 'python' command over 'python3'.
  -p3, --python3     use the 'python3' command over 'python'.
  -r,  --restart     kill the bots process, then start it up again with no parameters.
  -u,  --update      retrieve data from git, the same as 'git pull'.
  -ur, --updrest     kill the bots process, retrieve updates from git, then start it up again with no parameters.
  -v,  --verbose     show more verbose output."

  exit 0
}

function doexit() {
  if [ ! -f "ircbot.pid" ]; then
    echo "Could not kill bot - no ircbot.pid exists. Is the bot running?"
    exit 2
  fi

  kill `cat ircbot.pid`
  success_kill=$?
  rm ircbot.pid
  success_rm=$?

  if [[ $success_kill -eq 0 ]]; then
    echo "The bot has been forcefully shut down."
  else
    echo "Could not kill the process."
  fi

  if [[ $success_rm -ne 0 ]]; then
    echo "Could not remove ircbot.pid."
    if [[ $success_kill -eq 0 ]]; then
      exit 1
    fi
  fi

  exit $success_kill
}

function doupdate() {
  echo "Pulling data from git.."
  git pull
  exit 0
}

function dorestart() {
  $0 -k
  $0
  exit 0
}

function update_and_restart() {
  $0 -k
  git pull
  $0
  exit 0
}

be_verbose=0
use_python3=0
use_python=0
screen_args=""

for arg in $@; do
  case "$arg" in
    -d|--daemon)   screen_args="-dm";;
    -h|--help)     help;;
    -k|--kill)     doexit;;
    -p|--python)   use_python=1;;
    -p3|--python3)  use_python3=1;;
    -r|--restart)  dorestart;;
    -u|--update)   doupdate;;
    -ur|--updrest) update_and_restart;;
    -v|--verbose)  be_verbose=1;;
  esac
done

if [ -e "ircbot.pid" ]; then
  if [[ $be_verbose -eq 1 ]]; then
    echo "ircbot.pid exists, will not start as process is already running."
  fi
  exit 0
fi

if [[ $be_verbose -eq 1 ]]; then
  echo "Starting bot."
fi

if [[ $use_python3 -eq 1 ]]; then
  screen $screen_args python3 bot.py
elif [[ $use_python -eq 1 ]]; then
  screen $screen_args python bot.py
else
  pytest=`python3 -c "print('1')"`  # Some machines run both python2 and python3, if python3 is a command we use that.

  if [[ $pytest -eq 1 ]]; then
    screen $screen_args python3 bot.py
  else
    screen $screen_args python bot.py
  fi
fi

exit 0
