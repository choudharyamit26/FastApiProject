from fastapi import status, Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.auth.responses import UserWithOrdersResponse
from app.api.auth.schemas import CreateOrderRequest
from app.api.models.models import User, Product, Order, order_product_association
from app.config.config import get_db
from app.utils.security import oauth_scheme2

orders_router = APIRouter(
    prefix="/order", tags=["Order"], responses={404: {"description": "Not found"}}
)


# POST endpoint to create an order with multiple products
@orders_router.post("/create", status_code=status.HTTP_201_CREATED)
def create_order(
    order: CreateOrderRequest,
    authenticated: str = Depends(oauth_scheme2),
    db: Session = Depends(get_db),
):
    # Check if the user exists
    user = db.query(User).filter(User.id == order.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create a new order
    new_order = Order(user_id=order.user_id)
    db.add(new_order)

    # Add products to the order
    for product_request in order.products:
        product = (
            db.query(Product).filter(Product.id == product_request.product_id).first()
        )
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_request.product_id} not found",
            )

        stmt = order_product_association.insert().values(
            order_id=new_order.id,
            product_id=product.id,
            quantity=product_request.quantity,
        )
        db.execute(stmt)

    # Commit the transaction (no try-except needed here)
    db.commit()
    db.refresh(new_order)

    return {"message": "Order created successfully", "order_id": new_order.id}


@orders_router.get("/orders/{order_id}")
def get_order(
    order_id: int,
    authenticated: str = Depends(oauth_scheme2),
    db: Session = Depends(get_db),
):
    # Fetch order with products
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Prepare the response
    order_data = {
        "order_id": order.id,
        "user_id": order.user_id,
        "products": [
            {
                "product_id": product.id,
                "product_name": product.name,
                "quantity": association.quantity,
            }
            for product, association in db.query(Product, order_product_association)
            .join(
                order_product_association,
                Product.id == order_product_association.c.product_id,
            )
            .filter(order_product_association.c.order_id == order.id)
        ],
    }

    return JSONResponse(content=order_data)


# Endpoint to fetch user with their orders using a JOIN
@orders_router.get(
    "/users-with-orders/{user_id}", response_model=UserWithOrdersResponse
)
def get_user_with_orders(
    user_id: int,
    authenticated: str = Depends(oauth_scheme2),
    db: Session = Depends(get_db),
):
    # Perform a JOIN to get the user and their orders
    stmt = db.query(User).join(Order).filter(User.id == user_id).all()

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
