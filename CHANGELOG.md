# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).


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
