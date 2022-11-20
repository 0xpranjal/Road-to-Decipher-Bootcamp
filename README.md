# Road-to-Decipher-Bootcamp
This repo contains code and slides for Road to Decipher Bootcamp

# Setting up your developer environment

### Install brew
```
cd /opt
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
export PATH=/opt/homebrew/bin:$PATH
export PATH=/opt/homebrew/sbin:$PATH
```

### Install python 3
`brew install python3`

## Install nodejs
`brew install node`

## Install sandbox
`git clone https://github.com/algorand/sandbox.git`

## Changes in configuration for running sandbox within a propject folder
```
volumes:
- type: bind
  source: ../
  target: /data
```

## Intialising sandbox
`./sandbox up -v`
`./sandbox enter algod`