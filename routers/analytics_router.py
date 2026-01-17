import io

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from database import get_db
from repositories import analytics_repository
from schemas import schemas

router = APIRouter(prefix="/v1/analytics", tags=["Analytics"])


@router.get("/average-duration")
def get_average_duration(db: Session = Depends(get_db)) -> dict:
    average_duration = analytics_repository.calculate_average_duration(db)
    return {"average_duration": average_duration}


@router.get("/order-frequency")
def get_order_frequency(db: Session = Depends(get_db)) -> list:
    order_frequencies = analytics_repository.order_frequency_per_customer(db)
    return [
        {"customer_id": customer_id, "order_count": order_count}
        for customer_id, order_count in order_frequencies
    ]


@router.get("/customer-activity")
def get_customer_activity_periods(db: Session = Depends(get_db)) -> list:
    customer_activity_periods = analytics_repository.identify_customer_activity_periods(
        db
    )
    return [
        {"year": year, "month": month, "total_orders": total_orders}
        for year, month, total_orders in customer_activity_periods
    ]


@router.get("/active-customers")
def get_active_customers(start: str, end: str, db: Session = Depends(get_db)) -> dict:
    start_date = schemas.parse_datetime(start)
    end_date = schemas.parse_datetime(end)
    active_customer_count = analytics_repository.count_active_customers(
        db, start_date, end_date
    )
    return {"active_customer_count": active_customer_count}


@router.get("/average-duration-img")
def average_duration(db: Session = Depends(get_db)) -> Response:
    avg = analytics_repository.calculate_average_duration(db)

    fig, ax = plt.subplots()
    ax.bar(["Average"], [avg])
    ax.set_ylabel("Duration")
    ax.set_title("Average Duration of Completed Work Orders")

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)

    return Response(content=img.getvalue(), media_type="image/png")


# Order frequency
@router.get("/order-frequency/image")
def order_frequency_image(db: Session = Depends(get_db)) -> Response:
    frequencies = analytics_repository.order_frequency_per_customer(db)

    df = pd.DataFrame(frequencies, columns=["customer_id", "order_count"])

    plt.figure(figsize=(10, 6))
    sns.barplot(x="customer_id", y="order_count", data=df)

    img = io.BytesIO()
    plt.savefig(img, format="png")

    return Response(img.getvalue(), media_type="image/png")


# Customer activity
@router.get("/customer-activity/image")
def customer_activity_image(db: Session = Depends(get_db)) -> Response:
    activities = analytics_repository.identify_customer_activity_periods(db)

    df = pd.DataFrame(activities, columns=["year", "month", "total_orders"])

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="month", y="total_orders", hue="year")

    img = io.BytesIO()
    plt.savefig(img, format="png")

    return Response(img.getvalue(), media_type="image/png")


# Active customers
@router.get("/active-customers/image")
def active_customers_image(start: str, end: str, db: Session = Depends(get_db)) -> Response:
    start_date = schemas.parse_datetime(start)
    end_date = schemas.parse_datetime(end)

    count = analytics_repository.count_active_customers(db, start_date, end_date)

    plt.figure(figsize=(5, 5))
    plt.pie([count], labels=["Active Customers"])

    img = io.BytesIO()
    plt.savefig(img, format="png")

    return Response(img.getvalue(), media_type="image/png")
