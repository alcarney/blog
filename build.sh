#!/bin/bash

cd themes/local
npm i
npm run build

cd ../../
hugo version
hugo