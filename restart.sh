#!/usr/bin/env mongo
var db = new Mongo().getDB('accounts-database')
db.dropDatabase();
db = new Mongo().getDB('books-database')
db.dropDatabase();
