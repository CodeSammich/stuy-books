#!/usr/bin/env mongo
var db = new Mongo().getDB('accounts-database')
db.dropDatabase();
