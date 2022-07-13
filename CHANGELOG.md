# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).


## [0.4.2] - 2022.07.06

### Improvements
- doc improvement for release
- name change to avoid confusions


## [0.4.1] - 2022.02.17

### Features

- **client inference return tuple with a bool representing inference success/fail and inference/error msg (#34)**

### Improvements

- doc improvements
- better webcam example (#29)
- updated `archipel-utils` version & remove deprecated warnings (#32)

### Fixes 

- handle case when `cv2` not installed when inference (#31)


## [0.3.1] - 2021-12-02

### Improvements
 
- remove confusing logging when builtin input / output type
- update archipel utils version


## [0.3.0] - 2021-11-30

### Features

- refactor build and cli (#26)

### Improvements
 
- better documentation (#25)

### Fixes 

- missing decode/encode function for `dict`
- remove `access:` from sended message


## [0.2.3] - 2021-09-02

### Features

- New example with dockerfile (face alignment)

### Improvements
 
- better logs print

### Fixes 

- Fix worker copy when script different from build context
- Valid testing even when worker starting logs


## [0.2.2] - 2021-08-25

### Features

- Add buildargs option to build (#23)

### Improvements

- Increase coverage to 94% (#22)

### Fix

- Change build context to follow docker one (#21)


## [0.2.1] - 2021-08-09

### **Fixes**

- fix version extractor `setup.py` and `archipel-utils`

## [0.2.0] - 2021-08-09

### **Features**

- Add CLI commands and model tester. Renaming into `i2-cli` (#16)

### **Improvements**

- Use general alpine utils (#14)
