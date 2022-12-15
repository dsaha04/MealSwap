#!/usr/bin/env python

#-----------------------------------------------------------------------
# create.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

import sys
import psycopg2
import sqlalchemy
import sqlalchemy.ext.declarative
import os
#-----------------------------------------------------------------------

Base = sqlalchemy.ext.declarative.declarative_base()

class Users (Base):
    __tablename__ = 'users'
    netid = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    nickname = sqlalchemy.Column(sqlalchemy.String)
    plan = sqlalchemy.Column(sqlalchemy.String)
    phone = sqlalchemy.Column(sqlalchemy.String)

class Requested (Base):
    __tablename__ = 'requested'
    reqid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    netid = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('users.netid'))
    requested = sqlalchemy.Column(sqlalchemy.String)
    times = sqlalchemy.Column(sqlalchemy.String)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime)

class Exchanges (Base):
    __tablename__ = 'exchanges'
    reqid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    netid = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('users.netid'))
    swapnetid = sqlalchemy.Column(sqlalchemy.String)
    times = sqlalchemy.Column(sqlalchemy.String)
    completed = sqlalchemy.Column(sqlalchemy.String)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime)

class Deletedrequest (Base):
    __tablename__ = 'deletedrequest'
    # delid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    reqid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    netid = sqlalchemy.Column(sqlalchemy.String, primary_key=True)

class Blocked (Base):
    __tablename__ = 'blocked'
    blockid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    netid = sqlalchemy.Column(sqlalchemy.String)
    block_netid = sqlalchemy.Column(sqlalchemy.String)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime)



# DATABASE_URL = os.getenv('DATABASE_URL')
# engine = sqlalchemy.create_engine(DATABASE_URL)
# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)