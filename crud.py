# from dataclasses import asdict

from certifi import where
from httpx import delete
from sqlalchemy.orm import Session
from sqlalchemy import insert, and_, delete, values, update
import datetime
import functions
import config
# Local imports
import models
import schemas
from models import Subscriber, Groups
from schemas import Group


# # ###################### Remove when done used for autocomplet ##############
# def get_db() :
#     db = SessionLocal()
#     try :
#         yield db
#     finally :
#         db.close()
#
#
# db: Session = Depends(get_db)

def get_subscribers(db: Session, skip: int = 0, limit: int = 100) :
    subscribers = (
        db.query(models.Subscriber)
        .with_entities(models.Subscriber.username, models.Subscriber.email_address, models.Groups.state)
        .join(Groups, and_(models.Subscriber.username == models.Groups.username), isouter=True)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return subscribers


def get_subscriber(db: Session, username: str) :
    subscriber = (
        db.query(models.Subscriber)
        .with_entities(models.Subscriber.username, models.Subscriber.email_address, models.Groups.state)
        .join(Groups, and_(models.Subscriber.username == models.Groups.username), isouter=True)
        .filter(models.Subscriber.username == username)
        .all()
    )
    if not subscriber :
        return None
    return subscriber[0]


def delete_subscriber(db: Session, username: str) :
    db.execute(delete(Subscriber).where(Subscriber.username == username))
    db.execute(delete(Groups).where(Groups.username == username))
    db.commit()
    return True


def add_subscriber(db: Session, username: str, password: str, email_address: str, state: schemas.SubscriberState) :
    db.execute(insert(Groups).values(username=username,
                                     domain=config.domain,
                                     state=state
                                     ))
    subscriber = db.execute(insert(Subscriber).values(username=username,
                                                      password=password,
                                                      domain=config.domain,
                                                      email_address=email_address
                                                      ))
    db.commit()
    return subscriber


def update_subscriber(db: Session, username: str, subscriberinfo: schemas.SubscriberUpdate) :
    subscriber = (
        db.query(models.Subscriber)
        .join(Groups, and_(models.Subscriber.username == models.Groups.username), isouter=True)
        .filter(models.Subscriber.username == username)
        .first()
    )
    print(subscriber.username)
    subscriber_data = subscriberinfo.model_dump(exclude_unset=True)
    print(subscriber_data)
    for key, value in subscriber_data.items() :
        setattr(subscriber, key, value)
    if subscriberinfo.state :
        db.query(Groups).filter(Groups.username == username).update({ Groups.state : subscriberinfo.state })
    db.commit()
    print(subscriber_data)


def validate_auth_key(db: Session, authkey: schemas.AuthResponse) :
    keyinfo = db.query(models.Users).filter(models.Users.api_key == authkey).first()
    return keyinfo


def validate_subscriber(db: Session, username: str) :
    subscriber = (
        db.query(models.Subscriber)
        .with_entities(models.Subscriber.username, models.Subscriber.email_address, models.Groups.state)
        .join(Groups, and_(models.Subscriber.username == models.Groups.username), isouter=True)
        .filter(models.Subscriber.username == username)
        .all()
    )
    if not subscriber :
        return False
    return True


def validate_subscription(db: Session, username: str, destination: str) :
    subscription = (
        db.query(models.Subscriptions)
        .with_entities(models.Subscriptions.username)
        .filter(models.Subscriptions.username == username, models.Subscriptions.destination == destination)
        .all()
    )
    if not subscription :
        return False
    return True


def get_subscriptions(db: Session, username, skip: int = 0, limit: int = 100) :
    subscriptions = (
        db.query(models.Subscriptions)
        .with_entities(models.Subscriptions.username, models.Subscriptions.destination, models.Subscriptions.state,
                       models.Subscriptions.expiry)
        .filter(models.Subscriptions.username == username)
        .offset(skip)
        .limit(limit)
        .all()
    )
    ''' We have to decode the expiry dates back to ISO'''
    subscription_data = [dict(r._mapping) for r in subscriptions]
    for i, v in enumerate(subscription_data) :
        subscription_data[i]['expiry'] = functions.timerec_to_expiry_datetime(str(subscription_data[i]['expiry']))
    return subscription_data


def add_subscription(db: Session, username: str, destination: str, state: schemas.SubscriptionState, expiry: datetime) :
    expiry = functions.expiry_datetime_to_timerec(expiry)
    db.execute(insert(models.Subscriptions).values(username=username,
                                                   destination=destination,
                                                   state=state,
                                                   expiry=expiry
                                                   ))
    db.commit()
    return True


def update_subscription(db: Session, username: str, destination: str, subscriptionInfo: schemas.SubscriptionUpdate) :
    subscription = (
        db.query(models.Subscriptions)
        .filter(models.Subscriptions.username == username, models.Subscriptions.destination == destination)
        .first()
    )
    subscription_data = subscriptionInfo.model_dump(exclude_unset=True)
    for key, value in subscription_data.items() :
        if key == 'expiry' :
            value = functions.expiry_datetime_to_timerec(value)
        setattr(subscription, key, value)
    db.commit()
    (print(subscription_data))


def delete_subscription(db: Session, username: str, destination: str) :
    db.execute(delete(models.Subscriptions).where(models.Subscriptions.username == username, models.Subscriptions.destination == destination))
    db.commit()
    return True
